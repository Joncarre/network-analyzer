from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from datetime import datetime
import glob

Base = declarative_base()

class CaptureSession(Base):
    """Modelo para almacenar información de una sesión de captura"""
    __tablename__ = 'capture_sessions'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(512), nullable=True)
    interface = Column(String(100), nullable=True)
    filter_applied = Column(String(255), nullable=True)
    pcap_file = Column(String(512), nullable=True)
    packet_count = Column(Integer, default=0)
    status = Column(String(50), default="en_progreso")
    capture_date = Column(DateTime, default=datetime.now)
    
    packets = relationship("Packet", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CaptureSession(id={self.id}, file={self.file_name})>"

class Packet(Base):
    """Modelo para almacenar información detallada de paquetes"""
    __tablename__ = 'packets'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('capture_sessions.id'), nullable=False)
    
    # Metadatos generales del paquete
    packet_number = Column(Integer, nullable=False)  # Número secuencial en la captura
    timestamp = Column(Float, nullable=False)        # Timestamp de captura (epoch)
    capture_length = Column(Integer)                 # Longitud capturada
    packet_length = Column(Integer)                  # Longitud original (wire length)
    capture_interface = Column(String, nullable=True) # Interfaz donde se capturó
    frame_number = Column(Integer, nullable=True)     # Número de frame
    
    # Metadatos adicionales del frame
    frame_time_relative = Column(Float, nullable=True)  # Tiempo relativo desde inicio de captura
    frame_time_delta = Column(Float, nullable=True)     # Tiempo desde frame anterior
    
    # Capa 2 - Ethernet
    src_mac = Column(String(17), nullable=True)      # Dirección MAC origen
    dst_mac = Column(String(17), nullable=True)      # Dirección MAC destino
    eth_type = Column(String(10), nullable=True)     # Tipo Ethernet (0x0800 para IPv4)
    vlan_id = Column(Integer, nullable=True)         # VLAN ID si está presente
    
    # Bits adicionales de Ethernet
    eth_dst_lg = Column(Boolean, nullable=True)       # Bit Locally Administered (dirección destino)
    eth_dst_ig = Column(Boolean, nullable=True)       # Bit Individual/Group (dirección destino)
    eth_src_lg = Column(Boolean, nullable=True)       # Bit Locally Administered (dirección origen)
    eth_src_ig = Column(Boolean, nullable=True)       # Bit Individual/Group (dirección origen)
    
    # PPP - Point-to-Point Protocol
    ppp_protocol = Column(String(10), nullable=True)  # Protocolo PPP
    ppp_direction = Column(String(10), nullable=True) # Dirección PPP
    
    # CAPA 3 - IP (campos comunes)
    ip_version = Column(Integer, nullable=True)      # Versión IP (4 o 6)
    src_ip = Column(String(45), nullable=True)       # Dirección IP origen
    dst_ip = Column(String(45), nullable=True)       # Dirección IP destino
    
    # CAPA 3 - IPv4 específico
    ip_header_length = Column(Integer, nullable=True) # IHL en bytes
    ip_dscp = Column(Integer, nullable=True)         # Differentiated Services Code Point
    ip_ecn = Column(Integer, nullable=True)          # Explicit Congestion Notification
    ip_total_length = Column(Integer, nullable=True) # Longitud total del datagrama
    ip_identification = Column(Integer, nullable=True) # Campo de identificación
    ip_flags = Column(Integer, nullable=True)        # Flags (DF, MF)
    ip_flag_df = Column(Boolean, nullable=True)      # Don't Fragment flag
    ip_flag_mf = Column(Boolean, nullable=True)      # More Fragments flag
    ip_fragment_offset = Column(Integer, nullable=True) # Fragment offset
    ip_ttl = Column(Integer, nullable=True)          # Time To Live
    ip_protocol = Column(Integer, nullable=True)     # Protocolo encapsulado
    ip_checksum = Column(String(10), nullable=True)  # Checksum
    ip_options = Column(String, nullable=True)       # Opciones IP (representación de texto)
    
    # CAPA 3 - IPv6 específico
    ipv6_traffic_class = Column(Integer, nullable=True)  # Traffic Class
    ipv6_flow_label = Column(Integer, nullable=True)     # Flow Label
    ipv6_payload_length = Column(Integer, nullable=True) # Payload Length
    ipv6_next_header = Column(Integer, nullable=True)    # Next Header
    ipv6_hop_limit = Column(Integer, nullable=True)      # Hop Limit
    ipv6_ext_headers = Column(String, nullable=True)     # Extension Headers (JSON)
    
    # CAPA 4 - Común
    transport_protocol = Column(String(10), nullable=True) # TCP, UDP, ICMP, etc.
    src_port = Column(Integer, nullable=True)         # Puerto origen
    dst_port = Column(Integer, nullable=True)         # Puerto destino
    
    # CAPA 4 - TCP específico
    tcp_seq_number = Column(Integer, nullable=True)   # Sequence Number
    tcp_ack_number = Column(Integer, nullable=True)   # Acknowledgment Number
    tcp_header_length = Column(Integer, nullable=True) # Data Offset en bytes
    tcp_flags_raw = Column(Integer, nullable=True)    # Flags como valor entero
    
    # TCP Flags individuales
    tcp_flag_ns = Column(Boolean, default=False)      # ECN-nonce
    tcp_flag_cwr = Column(Boolean, default=False)     # Congestion Window Reduced
    tcp_flag_ece = Column(Boolean, default=False)     # ECN-Echo
    tcp_flag_urg = Column(Boolean, default=False)     # Urgent
    tcp_flag_ack = Column(Boolean, default=False)     # Acknowledgment
    tcp_flag_psh = Column(Boolean, default=False)     # Push
    tcp_flag_rst = Column(Boolean, default=False)     # Reset
    tcp_flag_syn = Column(Boolean, default=False)     # Synchronize
    tcp_flag_fin = Column(Boolean, default=False)     # Finish
    
    tcp_window_size = Column(Integer, nullable=True)  # Window Size
    tcp_window_size_scalefactor = Column(Integer, nullable=True)  # Window Scale Factor
    tcp_window_size_value = Column(Integer, nullable=True)  # Window Size Value (calculated)
    tcp_checksum = Column(String(10), nullable=True)  # Checksum
    tcp_urgent_pointer = Column(Integer, nullable=True) # Urgent Pointer
    tcp_options = Column(String, nullable=True)       # Opciones TCP (representación de texto)
    tcp_mss = Column(Integer, nullable=True)          # Maximum Segment Size
    tcp_sack_permitted = Column(Boolean, nullable=True) # SACK permitido
    tcp_ts_value = Column(Integer, nullable=True)     # Timestamp value
    tcp_ts_echo = Column(Integer, nullable=True)      # Timestamp echo reply
    tcp_stream_index = Column(Integer, nullable=True) # Índice de flujo
    tcp_payload_size = Column(Integer, nullable=True) # Tamaño del payload
    tcp_analysis_flags = Column(String, nullable=True) # Flags de análisis (retransmisión, etc.)
    tcp_analysis_rtt = Column(Float, nullable=True)   # Round-Trip Time calculado
    tcp_keep_alive = Column(Boolean, nullable=True)   # TCP Keep Alive
    
    # TCP Análisis avanzado
    tcp_analysis_bytes_in_flight = Column(Integer, nullable=True)  # Bytes en vuelo
    tcp_analysis_push_bytes_sent = Column(Integer, nullable=True)  # Bytes enviados con PSH
    tcp_analysis_acks_frame = Column(Integer, nullable=True)       # Frame que ACK este paquete
    tcp_analysis_retransmission = Column(Boolean, nullable=True)   # Es retransmisión
    tcp_analysis_duplicate_ack = Column(Boolean, nullable=True)    # Es ACK duplicado
    tcp_analysis_zero_window = Column(Boolean, nullable=True)      # Ventana cero
    tcp_analysis_window_update = Column(Boolean, nullable=True)    # Actualización de ventana
    tcp_analysis_keep_alive = Column(Boolean, nullable=True)       # Es keep-alive
    tcp_analysis_keep_alive_ack = Column(Boolean, nullable=True)   # Es ACK de keep-alive
    
    # CAPA 4 - UDP específico
    udp_length = Column(Integer, nullable=True)       # Longitud UDP
    udp_checksum = Column(String(10), nullable=True)  # Checksum
    udp_stream_index = Column(Integer, nullable=True) # Índice de flujo
    udp_payload_size = Column(Integer, nullable=True) # Tamaño del payload
    
    # CAPA 4 - ICMP específico
    icmp_type = Column(Integer, nullable=True)        # Tipo de ICMP
    icmp_code = Column(Integer, nullable=True)        # Código de ICMP
    icmp_checksum = Column(String(10), nullable=True) # Checksum
    icmp_identifier = Column(Integer, nullable=True)  # Identificador (Echo)
    icmp_sequence = Column(Integer, nullable=True)    # Número de secuencia (Echo)
    icmp_gateway = Column(String(45), nullable=True)  # Gateway (redirect)
    icmp_length = Column(Integer, nullable=True)      # Longitud ICMP (opcional)
    icmp_mtu = Column(Integer, nullable=True)         # MTU (Destination Unreachable/Fragmentation Needed)
    icmp_unused = Column(Integer, nullable=True)      # Campo reservado/unused
    
    # ARP específico
    arp_opcode = Column(Integer, nullable=True)           # Operation Code (1=req, 2=reply)
    arp_src_hw = Column(String(17), nullable=True)       # Hardware Address (src MAC)
    arp_dst_hw = Column(String(17), nullable=True)       # Hardware Address (dst MAC)
    arp_src_ip = Column(String(15), nullable=True)       # Protocol Address (src IP)
    arp_dst_ip = Column(String(15), nullable=True)       # Protocol Address (dst IP)
    
    # Metadatos adicionales
    delta_time = Column(Float, nullable=True)         # Tiempo desde el paquete anterior
    
    # Campos generales de análisis
    info_text = Column(String, nullable=True)         # Texto informativo del paquete
    is_error = Column(Boolean, default=False)
    is_malformed = Column(Boolean, default=False)
    protocol_stack = Column(String, nullable=True)    # Pila completa de protocolos
    
    # Relaciones
    session = relationship("CaptureSession", back_populates="packets")
    tcp_info = relationship("TCPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    udp_info = relationship("UDPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    icmp_info = relationship("ICMPInfo", back_populates="packet", uselist=False, cascade="all, delete-orphan")
    anomalies = relationship("Anomaly", back_populates="packet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Packet(id={self.id}, src={self.src_ip}, dst={self.dst_ip}, proto={self.protocol})>"

class TCPInfo(Base):
    """Información adicional para paquetes TCP"""
    __tablename__ = 'tcp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    seq_number = Column(Integer, nullable=True)
    ack_number = Column(Integer, nullable=True)
    window_size = Column(Integer, nullable=True)
    header_length = Column(Integer, nullable=True)
    flag_syn = Column(Boolean, default=False)
    flag_ack = Column(Boolean, default=False)
    flag_fin = Column(Boolean, default=False)
    flag_rst = Column(Boolean, default=False)
    flag_psh = Column(Boolean, default=False)
    flag_urg = Column(Boolean, default=False)
    flag_ece = Column(Boolean, default=False)
    flag_cwr = Column(Boolean, default=False)
    has_timestamp = Column(Boolean, default=False)
    timestamp_value = Column(Integer, nullable=True)
    timestamp_echo = Column(Integer, nullable=True)
    mss = Column(Integer, nullable=True)
    window_scale = Column(Integer, nullable=True)
    
    packet = relationship("Packet", back_populates="tcp_info")
    
    def __repr__(self):
        return f"<TCPInfo(id={self.id}, src_port={self.src_port}, dst_port={self.dst_port})>"

class UDPInfo(Base):
    """Información adicional para paquetes UDP"""
    __tablename__ = 'udp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    src_port = Column(Integer, nullable=False)
    dst_port = Column(Integer, nullable=False)
    length = Column(Integer, nullable=True)
    
    packet = relationship("Packet", back_populates="udp_info")
    
    def __repr__(self):
        return f"<UDPInfo(id={self.id}, src_port={self.src_port}, dst_port={self.dst_port})>"

class ICMPInfo(Base):
    """Información adicional para paquetes ICMP"""
    __tablename__ = 'icmp_info'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    type = Column(Integer, nullable=False)
    code = Column(Integer, nullable=False)
    checksum = Column(String(10), nullable=True)
    identifier = Column(Integer, nullable=True)
    sequence = Column(Integer, nullable=True)
    description = Column(String(255), nullable=True)
    
    packet = relationship("Packet", back_populates="icmp_info")
    
    def __repr__(self):
        return f"<ICMPInfo(id={self.id}, type={self.type}, code={self.code})>"

class Anomaly(Base):
    """Modelo para almacenar anomalías detectadas en los paquetes"""
    __tablename__ = 'anomalies'
    
    id = Column(Integer, primary_key=True)
    packet_id = Column(Integer, ForeignKey('packets.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('capture_sessions.id'), nullable=True)
    type = Column(String(100), nullable=False)
    description = Column(String(512), nullable=False)
    severity = Column(String(50), nullable=False)  # alta, media, baja
    detection_method = Column(String(100), nullable=True)
    detection_time = Column(DateTime, default=datetime.now)
    
    packet = relationship("Packet", back_populates="anomalies")
    
    def __repr__(self):
        return f"<Anomaly(id={self.id}, type={self.type}, severity={self.severity})>"

def init_db(db_path=None, force_new=False):
    """
    Inicializa la base de datos. Busca la más reciente o crea una nueva.
    
    Args:
        db_path (str, optional): Ruta específica a la base de datos. Si no se proporciona, se usa/crea una en el directorio predeterminado.
        force_new (bool, optional): Si es True, siempre crea una base de datos nueva, incluso si hay una existente.
    
    Returns:
        tuple: (engine, db_path)
    """
    if db_path is None:
        db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
        os.makedirs(db_dir, exist_ok=True)
        
        # Si force_new es True o si no hay bases de datos existentes, crear una nueva
        if force_new:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_path = os.path.join(db_dir, f"database_{timestamp}.db")
            print(f"[INFO] Using database: {db_path}")
        else:
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
        # Solo mostramos este mensaje cuando no estamos forzando una nueva base de datos
        if not force_new or db_path is not None:
            print(f"Tablas aseguradas/creadas en: {db_path}")
    except Exception as e:
        print(f"Error al crear/asegurar tablas en {db_path}: {e}")
        raise # Re-raise exception after logging
    
    return engine, db_path # Return path as well for clarity if needed

