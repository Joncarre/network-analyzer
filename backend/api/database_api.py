from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import create_engine, func, desc, or_, and_
from sqlalchemy.orm import sessionmaker, joinedload
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
from database.models import Base, CaptureSession, Packet, TCPInfo, UDPInfo, ICMPInfo, Anomaly
import glob
from collections import defaultdict
from pydantic import BaseModel

router = APIRouter(prefix="/api/database", tags=["database"])

# Función auxiliar para obtener flags TCP como texto
def _get_tcp_flags(tcp_info):
    """Obtiene una representación legible de los flags TCP"""
    flags = []
    if tcp_info.flag_syn: flags.append("SYN")
    if tcp_info.flag_ack: flags.append("ACK")
    if tcp_info.flag_fin: flags.append("FIN")
    if tcp_info.flag_rst: flags.append("RST")
    if tcp_info.flag_psh: flags.append("PSH")
    if tcp_info.flag_urg: flags.append("URG")
    if tcp_info.flag_ece: flags.append("ECE")
    if tcp_info.flag_cwr: flags.append("CWR")
    return ", ".join(flags) if flags else "None"

def get_db_session(db_file: Optional[str] = None):
    """Crea y retorna una sesión de base de datos, asegurando que las tablas existen."""
    db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
    if db_file:
        # Seguridad: solo permitir archivos dentro del directorio y con extensión .db
        db_path = os.path.abspath(os.path.join(db_dir, db_file))
        if not db_path.startswith(os.path.abspath(db_dir)) or not db_file.endswith('.db') or not os.path.exists(db_path):
            raise HTTPException(status_code=400, detail="Base de datos no válida")
    else:
        db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
        if not db_files:
            raise HTTPException(status_code=500, detail="No se encontró ninguna base de datos")
        db_path = max(db_files, key=os.path.getmtime)
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

class SessionResponseItem(BaseModel):
    id: int
    file_name: str
    file_path: Optional[str] = None
    interface: Optional[str] = None
    filter_applied: Optional[str] = None
    capture_date: str
    packet_count: int
    anomaly_count: Optional[int] = 0
    
class SessionsResponse(BaseModel):
    sessions: List[SessionResponseItem]
    total: int

class PacketResponseItem(BaseModel):
    id: int
    packet_number: int
    timestamp: float
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    protocol: Optional[str] = None
    length: int
    details: Optional[Dict[str, Any]] = None
    anomalies: List[Dict[str, Any]] = []

class PacketResponse(BaseModel):
    packets: List[PacketResponseItem]
    total: int

# Endpoint para obtener todas las sesiones de captura
@router.get("/sessions", response_model=SessionsResponse)
async def get_sessions(db_file: Optional[str] = Query(None)):
    db = get_db_session(db_file)
    try:
        # Obtenemos las sesiones con conteo de anomalías
        sessions_with_anomalies = (
            db.query(
                CaptureSession,
                func.count(Anomaly.id).label('anomaly_count')
            )
            .outerjoin(Packet, CaptureSession.id == Packet.session_id)
            .outerjoin(Anomaly, Packet.id == Anomaly.packet_id)
            .group_by(CaptureSession.id)
            .order_by(desc(CaptureSession.capture_date))
            .all()
        )
        
        # Formateamos la respuesta
        session_items = []
        for session, anomaly_count in sessions_with_anomalies:
            # Convertir la fecha a string en formato ISO para JSON
            capture_date_str = session.capture_date.isoformat() if session.capture_date else ""
            
            session_items.append(
                SessionResponseItem(
                    id=session.id,
                    file_name=session.file_name,
                    file_path=session.file_path,
                    interface=session.interface,
                    filter_applied=session.filter_applied,
                    capture_date=capture_date_str,
                    packet_count=session.packet_count or 0,
                    anomaly_count=anomaly_count or 0
                )
            )
        
        return SessionsResponse(sessions=session_items, total=len(session_items))
        
    except Exception as e:
        # Loguear el error para depuración
        import traceback
        print(f"Error al obtener sesiones: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al obtener sesiones: {str(e)}")
    finally:
        db.close()

# Obtener detalles de una sesión específica
@router.get("/sessions/{session_id}", response_model=dict)
def get_session_details(session_id: int, db_file: Optional[str] = Query(None)):
    db_session = get_db_session(db_file)
    try:
        # Buscar la sesión por ID
        session = db_session.query(CaptureSession).filter(CaptureSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Sesión con ID {session_id} no encontrada")
            
        # Contar paquetes y anomalías para esta sesión
        packet_count = db_session.query(func.count(Packet.id)).filter(
            Packet.session_id == session_id
        ).scalar()
        
        anomaly_count = db_session.query(func.count(Anomaly.id)).filter(
            Anomaly.session_id == session_id
        ).scalar()
        
        # Devuelve detalles de la sesión junto con los conteos
        return {
            "id": session.id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "interface": session.interface,
            "pcap_file": session.pcap_file,
            "packet_count": packet_count,
            "anomaly_count": anomaly_count,
            "status": session.status
        }
    finally:
        db_session.close()

# Obtener análisis estadísticos de una sesión
@router.get("/analytics/{session_id}", response_model=dict)
def get_session_analytics(session_id: int, db_file: Optional[str] = Query(None)):
    db_session = get_db_session(db_file)
    try:
        # Verificar que la sesión existe
        session = db_session.query(CaptureSession).filter(CaptureSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Sesión con ID {session_id} no encontrada")
        
        # Estadísticas por protocolo
        protocol_stats = db_session.query(
            Packet.protocol,
            func.count(Packet.id).label('count')
        ).filter(
            Packet.session_id == session_id
        ).group_by(
            Packet.protocol
        ).all()
        
        protocol_data = {p[0]: p[1] for p in protocol_stats}
        
        # Top IPs origen
        top_src_ips = db_session.query(
            Packet.src_ip,
            func.count(Packet.id).label('count')
        ).filter(
            Packet.session_id == session_id
        ).group_by(
            Packet.src_ip
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        # Top IPs destino
        top_dst_ips = db_session.query(
            Packet.dst_ip,
            func.count(Packet.id).label('count')
        ).filter(
            Packet.session_id == session_id
        ).group_by(
            Packet.dst_ip
        ).order_by(
            desc('count')
        ).limit(10).all()
        
        # Distribución de anomalías
        anomaly_distribution = db_session.query(
            Anomaly.type,
            func.count(Anomaly.id).label('count')
        ).filter(
            Anomaly.session_id == session_id
        ).group_by(
            Anomaly.type
        ).all()
        
        return {
            "session_id": session_id,
            "protocol_distribution": protocol_data,
            "top_source_ips": [{"ip": ip, "count": count} for ip, count in top_src_ips],
            "top_destination_ips": [{"ip": ip, "count": count} for ip, count in top_dst_ips],
            "anomaly_distribution": [{"type": type_, "count": count} for type_, count in anomaly_distribution],
            "total_packets": sum(p[1] for p in protocol_stats) if protocol_stats else 0
        }
    finally:
        db_session.close()

@router.get("/list-db-files", response_model=List[dict])
def list_db_files():
    """
    Lista los archivos de base de datos (.db) disponibles en el directorio de bases de datos.
    """
    db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
    if not os.path.exists(db_dir):
        return []
    db_files = []
    for file in sorted(os.listdir(db_dir), reverse=True):
        if file.endswith(".db"):
            file_path = os.path.join(db_dir, file)
            size = os.path.getsize(file_path) / 1024  # KB
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            db_files.append({
                "name": file,
                "path": file_path,
                "size_kb": round(size, 2),
                "modified": mod_time
            })
    return db_files
