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
    
    # CAPA 2 - ETHERNET
    src_mac = Column(String(17), nullable=True)      # Dirección MAC origen
    dst_mac = Column(String(17), nullable=True)      # Dirección MAC destino
    eth_type = Column(String(10), nullable=True)     # Tipo de Ethernet (e.g., 0x0800 para IPv4)
    vlan_id = Column(Integer, nullable=True)         # ID de VLAN si existe
    
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
    
    # CAPA 3 - IPv6 específico
    ipv6_traffic_class = Column(Integer, nullable=True) # Traffic Class
    ipv6_flow_label = Column(Integer, nullable=True)   # Flow Label
    ipv6_payload_length = Column(Integer, nullable=True) # Payload Length
    ipv6_next_header = Column(Integer, nullable=True)  # Next Header
    ipv6_hop_limit = Column(Integer, nullable=True)    # Hop Limit
    
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
    icmp_length = Column(Integer, nullable=True)      # Longitud
    
    # Otros protocolos de capa 7
    protocol = Column(String(10))                    # Protocolo alto nivel (HTTP, DNS, etc.)
    
    # Información DNS
    dns_query_name = Column(String, nullable=True)
    dns_query_type = Column(String, nullable=True)
    dns_response_ips = Column(String, nullable=True)
    dns_record_ttl = Column(Integer, nullable=True)
    
    # Información HTTP
    http_method = Column(String(10), nullable=True)
    http_uri = Column(String, nullable=True)
    http_host = Column(String, nullable=True)
    http_user_agent = Column(String, nullable=True)
    http_referer = Column(String, nullable=True)
    http_response_code = Column(Integer, nullable=True)
    http_content_type = Column(String, nullable=True)
    
    # TLS/SSL
    tls_version = Column(String(20), nullable=True)
    tls_cipher_suite = Column(String, nullable=True)
    tls_server_name = Column(String, nullable=True)
    
    # ARP
    arp_opcode = Column(Integer, nullable=True)
    arp_src_hw = Column(String(17), nullable=True)
    arp_dst_hw = Column(String(17), nullable=True)
    arp_src_ip = Column(String(15), nullable=True)
    arp_dst_ip = Column(String(15), nullable=True)
    
    # DHCP
    dhcp_message_type = Column(String(20), nullable=True)
    dhcp_requested_ip = Column(String(15), nullable=True)
    dhcp_client_mac = Column(String(17), nullable=True)
    
    # Métricas derivadas
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

