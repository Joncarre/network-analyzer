from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import glob

from ai.claude_integration import ClaudeAI
from database.models import Base, CaptureSession, Packet, Anomaly

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Modelo para solicitud de chat
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    db_file: Optional[str] = None
    user_preference: Optional[str] = None

# Modelo para respuesta de chat
class ChatResponse(BaseModel):
    response: str

# Singleton para la instancia de Claude
_claude_instance = None

def get_claude():
    """Obtiene una instancia singleton de ClaudeAI"""
    global _claude_instance
    if _claude_instance is None:
        try:
            _claude_instance = ClaudeAI()
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error al inicializar la IA: {str(e)}"
            )
    return _claude_instance

def get_db_session(db_file: Optional[str] = None):
    """Crea y retorna una sesión de base de datos"""
    db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
    
    if db_file:
        db_path = os.path.abspath(os.path.join(db_dir, db_file))
        if not db_path.startswith(os.path.abspath(db_dir)) or not db_file.endswith('.db') or not os.path.exists(db_path):
            raise HTTPException(status_code=400, detail="Base de datos no válida")
    else:
        db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
        
        if not db_files:
            raise HTTPException(status_code=500, detail="No se encontró ninguna base de datos")
            
        # Ordenar por fecha de modificación (más reciente primero)
        db_path = max(db_files, key=os.path.getmtime)
    
    engine = create_engine(f'sqlite:///{db_path}')
    # Asegurar que las tablas existan antes de operar
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@router.post("/chat", response_model=ChatResponse)
async def process_chat(
    chat_request: ChatRequest,
    claude: ClaudeAI = Depends(get_claude)
) -> ChatResponse:
    """
    Procesa una consulta en lenguaje natural y retorna una respuesta.
    
    Si se proporciona un session_id, la consulta se contextualiza con los datos
    de esa sesión de captura.
    """
    try:
        session_data = None
        db_session = None
        try:
            if chat_request.session_id:
                db_session = get_db_session(chat_request.db_file)
                # Verificar que existe la sesión
                capture = db_session.query(CaptureSession).filter(CaptureSession.id == chat_request.session_id).first()
                if not capture:
                    raise HTTPException(status_code=404, detail=f"Sesión con ID {chat_request.session_id} no encontrada")
                packet_count = capture.packet_count
                protocol_rows = db_session.query(Packet.transport_protocol, func.count(Packet.id)).filter(
                    Packet.session_id == chat_request.session_id
                ).group_by(Packet.transport_protocol).all()
                protocol_counts = {protocol: count for protocol, count in protocol_rows}
                anomaly_count = db_session.query(func.count(Anomaly.id)).join(
                    Packet, Packet.id == Anomaly.packet_id
                ).filter(Packet.session_id == chat_request.session_id).scalar()
                session_data = {
                    "session_id": chat_request.session_id,
                    "file_name": capture.file_name,
                    "packet_count": packet_count,
                    "protocols": protocol_counts,
                    "anomaly_count": anomaly_count
                }
            elif chat_request.db_file:
                db_session = get_db_session(chat_request.db_file)
                # Estadísticas globales si no hay session_id
                total_packets = db_session.query(func.count(Packet.id)).scalar()
                udp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol == 'UDP').scalar()
                tcp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol == 'TCP').scalar()
                icmp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol.like('ICMP%')).scalar()
                session_data = {
                    "file_name": chat_request.db_file,
                    "total_packets": total_packets,
                    "udp_packets": udp_packets,
                    "tcp_packets": tcp_packets,
                    "icmp_packets": icmp_packets
                }
        finally:
            if db_session:
                db_session.close()
        response = claude.query(chat_request.message, session_data, chat_request.user_preference)
        return ChatResponse(response=response)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("Error en /api/ai/chat:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al procesar la consulta: {str(e)}")

@router.post("/clear-chat")
async def clear_chat(claude: ClaudeAI = Depends(get_claude)):
    """
    Limpia el historial de conversación actual.
    """
    try:
        claude.clear_conversation()
        return {"message": "Historial de conversación borrado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al borrar historial: {str(e)}")
