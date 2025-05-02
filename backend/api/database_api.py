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

def get_db_session():
    """Crea y retorna una sesión de base de datos, asegurando que las tablas existen."""
    db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
    db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
    if not db_files:
        raise HTTPException(status_code=500, detail="No se encontró ninguna base de datos")
    latest_db = max(db_files, key=os.path.getmtime)
    engine = create_engine(f'sqlite:///{latest_db}')
    # Asegura que las tablas existen antes de operar
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

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
