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

def get_db_session():
    """Crea y retorna una sesión de base de datos"""
    db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
    db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
    
    if not db_files:
        raise HTTPException(status_code=500, detail="No se encontró ninguna base de datos")
        
    # Ordenar por fecha de modificación (más reciente primero)
    latest_db = max(db_files, key=os.path.getmtime)
    
    engine = create_engine(f'sqlite:///{latest_db}')
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
        
        # Si se proporciona un ID de sesión, obtener datos de contexto
        if chat_request.session_id:
            db_session = get_db_session()
            try:
                # Verificar que existe la sesión
                capture = db_session.query(CaptureSession).filter(CaptureSession.id == chat_request.session_id).first()
                
                if not capture:
                    raise HTTPException(status_code=404, detail=f"Sesión con ID {chat_request.session_id} no encontrada")
                
                # Obtener datos básicos para contexto
                packet_count = capture.packet_count
                
                # Contar paquetes por protocolo
                protocol_rows = db_session.query(Packet.protocol, func.count(Packet.id)).filter(
                    Packet.session_id == chat_request.session_id
                ).group_by(Packet.protocol).all()
                
                protocol_counts = {protocol: count for protocol, count in protocol_rows}
                
                # Contar anomalías
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
                
            finally:
                db_session.close()
        
        # Procesar la consulta con Claude
        response = claude.query(chat_request.message, session_data)
        
        return ChatResponse(response=response)
        
    except HTTPException:
        raise
    except Exception as e:
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
