from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from datetime import datetime
import glob

Base = declarative_base()

class CaptureSession(Base):
    """Modelo para almacenar metadatos de una sesión de captura"""
    __tablename__ = 'capture_sessions'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    capture_date = Column(DateTime, default=datetime.utcnow)
    interface = Column(String(255))
    duration = Column(Integer)  # en segundos
    packet_count = Column(Integer)
    filter_applied = Column(String(512))
    
    # Relaciones
    packets = relationship("Packet", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CaptureSession(id={self.id}, file='{self.file_name}')>"

class Packet(Base):
    """Modelo para almacenar información básica de paquetes"""
    __tablename__ = 'packets'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('capture_sessions.id'), nullable=False)
    packet_number = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)
    capture_length = Column(Integer)  # longitud capturada
    packet_length = Column(Integer)  # longitud original
    
    # Información de capa 3 (Red)
    ip_version = Column(Integer)  # 4 o 6
    src_ip = Column(String(45))  # Soporta IPv4 e IPv6
    dst_ip = Column(String(45))  # Soporta IPv4 e IPv6
    ttl = Column(Integer)
    ip_flags = Column(Integer)
    ip_id = Column(Integer)
    ip_header_length = Column(Integer)
    is_fragment = Column(Boolean, default=False)
    fragment_offset = Column(Integer)
    
    # Información de protocolo
    protocol = Column(String(10))  # TCP, UDP, ICMP, etc.
    
    # Relaciones
    session = relationship("CaptureSession", back_populates="packets")
    tcp_info = relationship("TCPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    udp_info = relationship("UDPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    icmp_info = relationship("ICMPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="packet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Packet(id={self.id}, src={self.src_ip}, dst={self.dst_ip}, proto={self.protocol})>"

class TCPInfo(Base):
    """Información específica de TCP"""
    __tablename__ = 'tcp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    seq_number = Column(Integer)
    ack_number = Column(Integer)
    window_size = Column(Integer)
    header_length = Column(Integer)
    
    # Flags TCP
    flag_syn = Column(Boolean, default=False)
    flag_ack = Column(Boolean, default=False)
    flag_fin = Column(Boolean, default=False)
    flag_rst = Column(Boolean, default=False)
    flag_psh = Column(Boolean, default=False)
    flag_urg = Column(Boolean, default=False)
    flag_ece = Column(Boolean, default=False)
    flag_cwr = Column(Boolean, default=False)
    
    # Opciones TCP
    has_timestamp = Column(Boolean, default=False)
    timestamp_value = Column(Integer)
    timestamp_echo = Column(Integer)
    mss = Column(Integer)  # Maximum Segment Size
    window_scale = Column(Integer)
    
    packet = relationship("Packet", back_populates="tcp_info")
    
    def __repr__(self):
        return f"<TCPInfo(src_port={self.src_port}, dst_port={self.dst_port})>"

class UDPInfo(Base):
    """Información específica de UDP"""
    __tablename__ = 'udp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    length = Column(Integer)
    
    packet = relationship("Packet", back_populates="udp_info")
    
    def __repr__(self):
        return f"<UDPInfo(src_port={self.src_port}, dst_port={self.dst_port})>"

class ICMPInfo(Base):
    """Información específica de ICMP"""
    __tablename__ = 'icmp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    icmp_type = Column(Integer, nullable=False)
    icmp_code = Column(Integer, nullable=False)
    icmp_type_name = Column(String(50))  # Nombre descriptivo del tipo
    checksum = Column(Integer)
    identifier = Column(Integer)  # Para ICMP Echo
    sequence_number = Column(Integer)  # Para ICMP Echo
    
    packet = relationship("Packet", back_populates="icmp_info")
    
    def __repr__(self):
        return f"<ICMPInfo(type={self.icmp_type}, code={self.icmp_code})>"

class Anomaly(Base):
    """Modelo para almacenar anomalías detectadas en los paquetes"""
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    type = Column(String(50), nullable=False)  # Tipo de anomalía
    description = Column(Text, nullable=False)  # Descripción de la anomalía
    severity = Column(String(20))  # baja, media, alta, crítica
    
    packet = relationship("Packet", back_populates="anomalies")
    
    def __repr__(self):
        return f"<Anomaly(type='{self.type}', severity='{self.severity}')>"

def init_db(db_path=None):
    """
    Inicializa la base de datos. Busca la más reciente o crea una nueva.
    """
    if db_path is None:
        db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
        os.makedirs(db_dir, exist_ok=True)
        
        # Buscar la base de datos más reciente
        db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
        if db_files:
            db_path = max(db_files, key=os.path.getmtime)
            print(f"Usando la base de datos existente más reciente: {db_path}")
        else:
            # Si no hay ninguna, crear una nueva con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_path = os.path.join(db_dir, f"database_{timestamp}.db")
            print(f"No se encontraron bases de datos existentes. Creando nueva: {db_path}")
    
    # Asegurarse de que el directorio existe (redundante pero seguro)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Crear el motor y las tablas
    engine = create_engine(f'sqlite:///{db_path}')
    try:
        Base.metadata.create_all(engine)
        print(f"Tablas aseguradas/creadas en: {db_path}")
    except Exception as e:
        print(f"Error al crear/asegurar tablas en {db_path}: {e}")
        raise # Re-raise exception after logging
    
    return engine, db_path # Return path as well for clarity if needed

