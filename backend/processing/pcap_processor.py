import pyshark
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, CaptureSession, Packet, TCPInfo, UDPInfo, ICMPInfo, Anomaly

class PCAPProcessor:
    """Clase para procesar archivos PCAP y almacenar datos en la base de datos"""
    
    def __init__(self, db_path=None):
        """
        Inicializa el procesador de PCAP.
        
        Args:
            db_path (str, opcional): Ruta a la base de datos SQLite.
        """
        if db_path is None:
            db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
            os.makedirs(db_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_path = os.path.join(db_dir, f"database_{timestamp}.db")
            
        # Asegurar que el directorio de la base de datos existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Crear el motor de la base de datos y sesión
        self.engine = create_engine(f'sqlite:///{db_path}')
        
        # Asegura que las tablas existen antes de operar
        Base.metadata.create_all(self.engine)
        
        self.Session = sessionmaker(bind=self.engine)
        self.db_path = db_path
    
    def process_pcap_file(self, pcap_file, interface=None, filter_applied=None):
        """
        Procesa un archivo PCAP y almacena los datos en la base de datos.
        
        Args:
            pcap_file (str): Ruta al archivo PCAP
            interface (str, opcional): Nombre de la interfaz de captura
            filter_applied (str, opcional): Filtro utilizado durante la captura
            
        Returns:
            int: ID de la sesión de captura creada
        """
        if not os.path.exists(pcap_file):
            raise FileNotFoundError(f"No se encontró el archivo PCAP: {pcap_file}")
            
        try:
            # Registro adicional para depuración
            print(f"\n===== INICIO PROCESAMIENTO DE PCAP =====")
            print(f"Archivo: {pcap_file}")
            print(f"Tamaño del archivo: {os.path.getsize(pcap_file) / 1024:.2f} KB")
            print(f"Interfaz: {interface}")
            print(f"Base de datos: {self.db_path}")
            
            # Crear una sesión de captura en la base de datos
            db_session = self.Session()
            capture_session = CaptureSession(
                file_name=os.path.basename(pcap_file),
                file_path=pcap_file,
                interface=interface,
                filter_applied=filter_applied,
                capture_date=datetime.now()
            )
            db_session.add(capture_session)
            db_session.commit()
            
            print(f"Sesión de captura creada con ID: {capture_session.id}")
            
            # Cargar el archivo PCAP
            print(f"Cargando archivo PCAP con pyshark...")
            cap = pyshark.FileCapture(pcap_file)
            
            # Procesar cada paquete
            packet_count = 0
            skipped_packets = 0
            error_packets = 0
            
            print(f"Comenzando procesamiento de paquetes...")
            for packet_number, packet in enumerate(cap, start=1):
                try:
                    # Registro adicional cada 1000 paquetes
                    if packet_number % 1000 == 0:
                        print(f"Procesando paquete #{packet_number}...")
                    
                    # Información del paquete para depuración (solo primeros paquetes)
                    if packet_number <= 5:
                        print(f"Paquete #{packet_number} - Capas disponibles: {[layer.layer_name for layer in packet.layers]}")
                    
                    # Procesar el paquete solo si tiene capa IP
                    if hasattr(packet, 'ip') or hasattr(packet, 'ipv6'):
                        self._process_packet(db_session, capture_session, packet_number, packet)
                        packet_count += 1
                    else:
                        skipped_packets += 1
                        if packet_number <= 10:  # Solo mostrar detalles para los primeros paquetes saltados
                            print(f"Saltando paquete #{packet_number} - No tiene capa IP. Capas disponibles: {[layer.layer_name for layer in packet.layers]}")
                except Exception as e:
                    error_packets += 1
                    print(f"Error al procesar el paquete #{packet_number}: {e}")
                    
                # Commit cada 1000 paquetes para evitar problemas de memoria
                if packet_number % 1000 == 0:
                    db_session.commit()
                    print(f"Commit realizado tras {packet_number} paquetes")
            
            # Actualizar el conteo de paquetes en la sesión
            capture_session.packet_count = packet_count
            db_session.commit()
            
            cap.close()
            
            # Verificar registros en la base de datos
            packet_count_db = db_session.query(Packet).filter(Packet.session_id == capture_session.id).count()
            tcp_count = db_session.query(TCPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            udp_count = db_session.query(UDPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            icmp_count = db_session.query(ICMPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            anomaly_count = db_session.query(Anomaly).join(Packet).filter(Packet.session_id == capture_session.id).count()
            
            # Resumen final
            print(f"\n===== RESUMEN DEL PROCESAMIENTO =====")
            print(f"Total de paquetes examinados: {packet_number if packet_number > 0 else 0}")
            print(f"Paquetes procesados con éxito: {packet_count}")
            print(f"Paquetes saltados (sin capa IP): {skipped_packets}")
            print(f"Paquetes con errores: {error_packets}")
            print(f"\nRegistros en la base de datos:")
            print(f"- Paquetes: {packet_count_db}")
            print(f"- TCP: {tcp_count}")
            print(f"- UDP: {udp_count}")
            print(f"- ICMP: {icmp_count}")
            print(f"- Anomalías: {anomaly_count}")
            
            # Verificar tamaño de la base de datos después del procesamiento
            db_size = os.path.getsize(self.db_path)
            print(f"Tamaño de la base de datos después del procesamiento: {db_size / 1024:.2f} KB")
            print(f"===== FIN PROCESAMIENTO DE PCAP =====\n")
            
            return capture_session.id
            
        except Exception as e:
            db_session.rollback()
            print(f"ERROR CRÍTICO durante el procesamiento: {e}")
            import traceback
            traceback.print_exc()
            raise e
            
        finally:
            db_session.close()
    
    def _process_packet(self, db_session, capture_session, packet_number, packet):
        """
        Procesa un paquete individual y lo almacena en la base de datos.
        
        Args:
            db_session: Sesión de base de datos activa
            capture_session: Instancia de CaptureSession
            packet_number (int): Número secuencial del paquete
            packet (pyshark.packet): Objeto de paquete de pyshark
        """
        # Determinar versión IP y obtener capas
        ip_layer = packet.ip if hasattr(packet, 'ip') else packet.ipv6 if hasattr(packet, 'ipv6') else None
        transport_layer = None
        protocol = None
        
        if not ip_layer:
            return  # No procesar paquetes sin capa IP
        
        # Identificar el protocolo de transporte
        if hasattr(packet, 'tcp'):
            transport_layer = packet.tcp
            protocol = 'TCP'
        elif hasattr(packet, 'udp'):
            transport_layer = packet.udp
            protocol = 'UDP'
        elif hasattr(packet, 'icmp'):
            transport_layer = packet.icmp
            protocol = 'ICMP'
        elif hasattr(packet, 'icmpv6'):
            transport_layer = packet.icmpv6
            protocol = 'ICMPv6'
        
        # Crear el registro de paquete básico
        new_packet = Packet(
            session_id=capture_session.id,
            packet_number=packet_number,
            timestamp=float(packet.sniff_timestamp),
            capture_length=int(packet.captured_length) if hasattr(packet, 'captured_length') else None,
            packet_length=int(packet.length) if hasattr(packet, 'length') else None,
            ip_version=int(ip_layer.version) if hasattr(ip_layer, 'version') else None,
            src_ip=ip_layer.src,
            dst_ip=ip_layer.dst,
            ttl=int(ip_layer.ttl) if hasattr(ip_layer, 'ttl') else None,
            ip_flags=int(ip_layer.flags, 16) if hasattr(ip_layer, 'flags') else None,
            ip_id=int(ip_layer.id, 16) if hasattr(ip_layer, 'id') else None,
            ip_header_length=int(ip_layer.hdr_len) if hasattr(ip_layer, 'hdr_len') else None,
            is_fragment=bool(int(ip_layer.flags, 16) & 0x4000) if hasattr(ip_layer, 'flags') else False,
            fragment_offset=int(ip_layer.frag_offset) if hasattr(ip_layer, 'frag_offset') else 0,
            protocol=protocol
        )
        db_session.add(new_packet)
        db_session.flush()  # Para obtener el ID del paquete
        
        # Procesar información específica del protocolo de transporte
        if protocol == 'TCP':
            self._process_tcp_packet(db_session, new_packet, transport_layer)
        elif protocol == 'UDP':
            self._process_udp_packet(db_session, new_packet, transport_layer)
        elif protocol in ['ICMP', 'ICMPv6']:
            self._process_icmp_packet(db_session, new_packet, transport_layer, protocol)
            
        # Detectar anomalías
        self._detect_anomalies(db_session, new_packet, ip_layer, transport_layer)
    
    def _process_tcp_packet(self, db_session, packet, tcp_layer):
        """
        Procesa un paquete TCP y almacena la información TCP.
        
        Args:
            db_session: Sesión de base de datos activa
            packet: Instancia de Packet
            tcp_layer: Capa TCP del paquete
        """
        # Extraer flags TCP
        flags = int(tcp_layer.flags, 16) if hasattr(tcp_layer, 'flags') else 0
        
        tcp_info = TCPInfo(
            packet_id=packet.id,
            src_port=int(tcp_layer.srcport),
            dst_port=int(tcp_layer.dstport),
            seq_number=int(tcp_layer.seq) if hasattr(tcp_layer, 'seq') else None,
            ack_number=int(tcp_layer.ack) if hasattr(tcp_layer, 'ack') else None,
            window_size=int(tcp_layer.window) if hasattr(tcp_layer, 'window') else None,
            header_length=int(tcp_layer.hdr_len) if hasattr(tcp_layer, 'hdr_len') else None,
            
            # Flags TCP
            flag_syn=(flags & 0x02) != 0,
            flag_ack=(flags & 0x10) != 0,
            flag_fin=(flags & 0x01) != 0,
            flag_rst=(flags & 0x04) != 0,
            flag_psh=(flags & 0x08) != 0,
            flag_urg=(flags & 0x20) != 0,
            flag_ece=(flags & 0x40) != 0,
            flag_cwr=(flags & 0x80) != 0,
            
            # Opciones TCP
            has_timestamp=hasattr(tcp_layer, 'options_timestamp_tsval'),
            timestamp_value=int(tcp_layer.options_timestamp_tsval) if hasattr(tcp_layer, 'options_timestamp_tsval') else None,
            timestamp_echo=int(tcp_layer.options_timestamp_tsecr) if hasattr(tcp_layer, 'options_timestamp_tsecr') else None,
            mss=int(tcp_layer.options_mss_val) if hasattr(tcp_layer, 'options_mss_val') else None,
            window_scale=int(tcp_layer.options_wscale_val) if hasattr(tcp_layer, 'options_wscale_val') else None
        )
        db_session.add(tcp_info)
    
    def _process_udp_packet(self, db_session, packet, udp_layer):
        """
        Procesa un paquete UDP y almacena la información UDP.
        
        Args:
            db_session: Sesión de base de datos activa
            packet: Instancia de Packet
            udp_layer: Capa UDP del paquete
        """
        udp_info = UDPInfo(
            packet_id=packet.id,
            src_port=int(udp_layer.srcport),
            dst_port=int(udp_layer.dstport),
            length=int(udp_layer.length) if hasattr(udp_layer, 'length') else None
        )
        db_session.add(udp_info)
    
    def _process_icmp_packet(self, db_session, packet, icmp_layer, protocol):
        """
        Procesa un paquete ICMP y almacena la información ICMP.
        
        Args:
            db_session: Sesión de base de datos activa
            packet: Instancia de Packet
            icmp_layer: Capa ICMP del paquete
            protocol (str): 'ICMP' o 'ICMPv6'
        """
        # Mapeo de tipos ICMP comunes a nombres descriptivos
        icmp_types = {
            0: "Echo Reply",
            3: "Destination Unreachable",
            5: "Redirect",
            8: "Echo Request",
            11: "Time Exceeded",
            13: "Timestamp",
            14: "Timestamp Reply"
        }
        
        # Para ICMPv6
        icmpv6_types = {
            1: "Destination Unreachable",
            2: "Packet Too Big",
            3: "Time Exceeded",
            4: "Parameter Problem",
            128: "Echo Request",
            129: "Echo Reply",
            133: "Router Solicitation",
            134: "Router Advertisement",
            135: "Neighbor Solicitation",
            136: "Neighbor Advertisement"
        }
        
        # Obtener tipo y código ICMP
        icmp_type = int(icmp_layer.type) if hasattr(icmp_layer, 'type') else 0
        icmp_code = int(icmp_layer.code) if hasattr(icmp_layer, 'code') else 0
        
        # Obtener nombre descriptivo según la versión de ICMP
        if protocol == 'ICMP':
            icmp_type_name = icmp_types.get(icmp_type, "Unknown")
        else:  # ICMPv6
            icmp_type_name = icmpv6_types.get(icmp_type, "Unknown")
            
        icmp_info = ICMPInfo(
            packet_id=packet.id,
            icmp_type=icmp_type,
            icmp_code=icmp_code,
            icmp_type_name=icmp_type_name,
            checksum=int(icmp_layer.checksum, 16) if hasattr(icmp_layer, 'checksum') else None,
            identifier=int(icmp_layer.id) if hasattr(icmp_layer, 'id') else None,
            sequence_number=int(icmp_layer.seq) if hasattr(icmp_layer, 'seq') else None
        )
        db_session.add(icmp_info)
    
    def _detect_anomalies(self, db_session, packet, ip_layer, transport_layer):
        """
        Detecta posibles anomalías en un paquete.
        
        Args:
            db_session: Sesión de base de datos activa
            packet: Instancia de Packet
            ip_layer: Capa IP del paquete
            transport_layer: Capa de transporte del paquete
        """
        anomalies = []
        
        # Si es TCP, detectar escaneos anormales (Xmas, NULL)
        if packet.protocol == 'TCP' and transport_layer:
            flags = int(transport_layer.flags, 16) if hasattr(transport_layer, 'flags') else 0
            
            # Escaneo Xmas (FIN, PSH, URG flags activos, resto inactivos)
            if (flags & 0x29) == 0x29 and not (flags & 0x16):
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Xmas Scan",
                        description="Posible escaneo Xmas detectado (FIN+PSH+URG flags activos)",
                        severity="alta"
                    )
                )
            
            # Escaneo NULL (ningún flag activo)
            if flags == 0:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="NULL Scan",
                        description="Posible escaneo NULL detectado (ningún flag TCP activo)",
                        severity="alta"
                    )
                )
                
            # Combinación inválida de flags SYN+FIN
            if (flags & 0x03) == 0x03:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Invalid Flags",
                        description="Combinación inválida de flags TCP (SYN+FIN)",
                        severity="media"
                    )
                )
        
        # Detección de fragmentación sospechosa
        if packet.is_fragment:
            offset = packet.fragment_offset
            if offset == 1:  # Fragmento con offset muy pequeño (puede ser usado para evasión)
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Suspicious Fragment",
                        description="Fragmento con offset sospechosamente pequeño",
                        severity="media"
                    )
                )
        
        # TTL muy bajo (posible escaneo o comportamiento anómalo)
        if hasattr(ip_layer, 'ttl') and int(ip_layer.ttl) < 5:
            anomalies.append(
                Anomaly(
                    packet_id=packet.id,
                    type="Low TTL",
                    description=f"TTL muy bajo ({ip_layer.ttl}), posible comportamiento anómalo",
                    severity="baja"
                )
            )
        
        # Añadir todas las anomalías detectadas a la base de datos
        for anomaly in anomalies:
            db_session.add(anomaly)
