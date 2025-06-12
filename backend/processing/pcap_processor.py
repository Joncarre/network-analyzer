import pyshark
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, CaptureSession, Packet, TCPInfo, UDPInfo, ICMPInfo, Anomaly

class PCAPProcessor:
    """Clase para procesar archivos PCAP y almacenar datos en la base de datos"""
    
    def __init__(self, db_path=None, pcap_file=None):
        """
        Inicializa el procesador de PCAP.
        
        Args:
            db_path (str, opcional): Ruta a la base de datos SQLite.
            pcap_file (str, opcional): Ruta al archivo PCAP.
        """
        db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
        os.makedirs(db_dir, exist_ok=True)
        if db_path is None:
            if pcap_file is not None:
                # Usar el nombre base del pcap para el .db
                base = os.path.splitext(os.path.basename(pcap_file))[0]
                db_path = os.path.join(db_dir, f"{base}.db")
            else:
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
            # Capturar tiempo de inicio para calcular duración
            import time
            start_time = time.time()
            
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
            
            # Cargar el archivo PCAP con pyshark
            print(f"Cargando archivo PCAP con pyshark...")
            cap = pyshark.FileCapture(pcap_file)
            
            # Procesar cada paquete
            packet_count = 0
            skipped_packets = 0
            error_packets = 0
            processed_packet_numbers = set()
            
            print(f"Comenzando procesamiento de paquetes con pyshark...")
            packet_iterator = iter(cap)
            packet_number_counter = 0
            
            # Realizar commits más frecuentemente para reducir el riesgo de perder datos
            commit_frequency = 100  # Hacer commit cada 100 paquetes
            pending_packet_count = 0

            while True:
                try:
                    packet = next(packet_iterator)
                    packet_number_counter += 1
                    packet_number = packet_number_counter

                    if packet_number in processed_packet_numbers:
                        continue
                    processed_packet_numbers.add(packet_number)

                    if packet_number % 1000 == 0:
                        print(f"Procesando paquete pyshark #{packet_number}...")
                    
                    try:
                        # Procesar este paquete en una "mini-transacción"
                        result = self._process_packet(db_session, capture_session, packet_number, packet)
                        if result:  # Si el procesamiento fue exitoso
                            packet_count += 1
                            pending_packet_count += 1
                        else:
                            skipped_packets += 1
                    except Exception as packet_error:
                        # Registrar el error pero continuar con otros paquetes
                        error_packets += 1
                        print(f"Error al procesar el paquete pyshark #{packet_number}: {packet_error}")
                        # No hacer rollback aquí, solo continuamos con el siguiente paquete

                    # Hacer commit más frecuentemente
                    if pending_packet_count >= commit_frequency:
                        try:
                            db_session.commit()
                            if packet_number % 1000 == 0:  # Solo imprimimos cada 1000 para no llenar la consola
                                print(f"Commit realizado tras procesar {packet_number} paquetes ({packet_count} exitosos)")
                            pending_packet_count = 0  # Reiniciar contador
                        except Exception as commit_error:
                            print(f"Error durante el commit periódico: {commit_error}")
                            # Intentar continuar sin hacer rollback para salvar lo que se pueda
                            # db_session.rollback()

                except StopIteration:
                    print("Fin de la iteración de paquetes.")
                    break
                except Exception as e:
                    error_packets += 1
                    print(f"Error general al procesar el paquete pyshark #{packet_number_counter}: {e}")
                    # No hacemos rollback aquí para mantener los paquetes procesados hasta ahora

            # Asegurarse de hacer commit de los últimos paquetes pendientes
            if pending_packet_count > 0:
                try:
                    db_session.commit()
                    print(f"Commit final de {pending_packet_count} paquetes pendientes")
                except Exception as final_commit_error:
                    print(f"Error durante el commit final de paquetes pendientes: {final_commit_error}")
              # Actualizar el conteo de paquetes en la sesión
            try:
                capture_session.packet_count = packet_count
                db_session.commit()
                print(f"Actualización del conteo de paquetes de la sesión: {packet_count}")
            except Exception as e:
                print(f"Error al actualizar el conteo de paquetes: {e}")
                try:
                    db_session.rollback()
                    capture_session.packet_count = packet_count
                    db_session.commit()
                except:
                    print("No se pudo actualizar el conteo de paquetes en la sesión")
            
            cap.close()
            
            # Calcular tiempo total de procesamiento
            end_time = time.time()
            processing_duration = end_time - start_time
            
            print(f"\n===== RESUMEN DEL PROCESAMIENTO =====")
            print(f"Total de paquetes examinados (aprox): {packet_number_counter}")
            print(f"Paquetes procesados con éxito: {packet_count}")
            print(f"Paquetes omitidos: {skipped_packets}")
            print(f"Paquetes con errores: {error_packets}")
            print(f"Tiempo de procesamiento: {processing_duration:.2f} segundos")
            print(f"Base de datos: {self.db_path}")
            
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
        Procesa un paquete individual (PyShark) y extrae información detallada de las capas 3 y 4.
        
        Returns:
            bool: True si el paquete fue procesado correctamente, False en caso contrario.
        """
        # Variables para almacenar el timestamp del paquete anterior (para calcular delta)
        # Esta variable se mantendrá entre llamadas a _process_packet
        if not hasattr(self, '_last_packet_time'):
            self._last_packet_time = None
            self._start_time = None
            
        # Función auxiliar para convertir strings a enteros con manejo de 'False'
        def safe_int_convert(value, base=10, default=None):
            if value is None:
                return default
            try:
                return int(value, base)
            except ValueError:
                if value == 'False':
                    return 0
                return default
                
        # Metadatos básicos del paquete
        try:
            timestamp = float(packet.sniff_timestamp)
            capture_length = safe_int_convert(getattr(packet, 'captured_length', None))
            packet_length = safe_int_convert(getattr(packet, 'length', None))
            
            # Registrar la hora de inicio si es el primer paquete
            if self._start_time is None:
                self._start_time = timestamp
            
            # Calcular tiempos relativos
            frame_time_relative = timestamp - self._start_time if self._start_time is not None else 0.0
            
            # Calcular delta_time (tiempo desde el paquete anterior)
            delta_time = None
            if self._last_packet_time is not None:
                delta_time = timestamp - self._last_packet_time
            self._last_packet_time = timestamp
            
            # Obtener interfaz de captura y metadatos del frame
            capture_interface = None
            frame_number = None
            frame_protocols = None
            
            if hasattr(packet, 'frame'):
                frame = packet.frame
                capture_interface = getattr(frame, 'interface_id', None)
                frame_number = safe_int_convert(getattr(frame, 'number', None))
                frame_protocols = getattr(frame, 'protocols', None)
        except AttributeError as e:
            print(f"Error accediendo a metadatos básicos del paquete #{packet_number}: {e}")
            return False

        # Construir pila de protocolos
        protocol_stack = ",".join([layer.layer_name for layer in packet.layers])
        
        # Inicializar todas las variables que poblaremos
        # Capa 2 - Ethernet
        src_mac = dst_mac = eth_type = None
        eth_dst_lg = eth_dst_ig = eth_src_lg = eth_src_ig = None
        vlan_id = None
        
        # PPP
        ppp_protocol = ppp_direction = None
        
        # Capa 3 - IP (común)
        ip_version = None
        src_ip = dst_ip = None
        
        # Capa 3 - IPv4
        ip_header_length = ip_dscp = ip_ecn = ip_total_length = None
        ip_identification = ip_flags = ip_flag_df = ip_flag_mf = None
        ip_fragment_offset = ip_ttl = ip_protocol = ip_checksum = None
        ip_options = None
        
        # Capa 3 - IPv6
        ipv6_traffic_class = ipv6_flow_label = ipv6_payload_length = None
        ipv6_next_header = ipv6_hop_limit = None
        ipv6_ext_headers = None
        
        # Capa 4 - Común
        transport_protocol = None
        src_port = dst_port = None
        
        # Capa 4 - TCP
        tcp_seq_number = tcp_ack_number = tcp_header_length = tcp_flags_raw = None
        tcp_flag_ns = tcp_flag_cwr = tcp_flag_ece = tcp_flag_urg = False
        tcp_flag_ack = tcp_flag_psh = tcp_flag_rst = tcp_flag_syn = tcp_flag_fin = False
        tcp_window_size = tcp_window_size_scalefactor = tcp_checksum = tcp_urgent_pointer = None
        tcp_window_size_value = None  # Asegurar inicialización
        tcp_options = None
        tcp_mss = tcp_sack_permitted = tcp_ts_value = tcp_ts_echo = None
        tcp_stream_index = tcp_payload_size = tcp_analysis_flags = tcp_analysis_rtt = None
        tcp_keep_alive = False
        
        # Capa 4 - UDP
        udp_length = udp_checksum = udp_stream_index = udp_payload_size = None
        
        # Capa 4 - ICMP
        icmp_type = icmp_code = icmp_checksum = icmp_identifier = None
        icmp_sequence = icmp_gateway = icmp_length = icmp_mtu = icmp_unused = None
        
        # ARP específico
        arp_opcode = arp_src_hw = arp_dst_hw = arp_src_ip = arp_dst_ip = None
        
        # Variables para información adicional
        info_text = None
        is_error = False
        is_malformed = False

        # Procesamiento por capas
        try:
            # Procesar Ethernet (capa 2)
            if hasattr(packet, 'eth'):
                eth = packet.eth
                src_mac = eth.src if hasattr(eth, 'src') else None
                dst_mac = eth.dst if hasattr(eth, 'dst') else None
                eth_type = eth.type if hasattr(eth, 'type') else None
                
                # Algunos bits específicos Ethernet que pueden ser útiles
                eth_dst_lg = bool(safe_int_convert(getattr(eth, 'dst_lg', None)))
                eth_dst_ig = bool(safe_int_convert(getattr(eth, 'dst_ig', None)))
                eth_src_lg = bool(safe_int_convert(getattr(eth, 'src_lg', None)))
                eth_src_ig = bool(safe_int_convert(getattr(eth, 'src_ig', None)))
            
            # Procesar VLAN si existe
            if hasattr(packet, 'vlan'):
                vlan = packet.vlan
                vlan_id = safe_int_convert(getattr(vlan, 'id', None))
            
            # Procesar PPP si existe
            if hasattr(packet, 'ppp'):
                ppp = packet.ppp
                ppp_protocol = getattr(ppp, 'protocol', None)
                ppp_direction = getattr(ppp, 'direction', None)
            
            # Procesar IP (versión 4 o 6)
            if hasattr(packet, 'ip'):
                ip = packet.ip
                ip_version = safe_int_convert(getattr(ip, 'version', None))
                src_ip = getattr(ip, 'src', None)
                dst_ip = getattr(ip, 'dst', None)
                
                # Campos específicos IPv4
                if ip_version == 4:
                    ip_header_length = safe_int_convert(getattr(ip, 'hdr_len', None))
                    ip_dscp = safe_int_convert(getattr(ip, 'dsfield_dscp', None))
                    ip_ecn = safe_int_convert(getattr(ip, 'dsfield_ecn', None))
                    ip_total_length = safe_int_convert(getattr(ip, 'len', None))
                    ip_identification = safe_int_convert(getattr(ip, 'id', None), 16)
                    
                    # Flags
                    ip_flags = safe_int_convert(getattr(ip, 'flags', None), 16)
                    ip_flag_df = bool(safe_int_convert(getattr(ip, 'flags_df', None)))
                    ip_flag_mf = bool(safe_int_convert(getattr(ip, 'flags_mf', None)))
                    
                    ip_fragment_offset = safe_int_convert(getattr(ip, 'frag_offset', None))
                    ip_ttl = safe_int_convert(getattr(ip, 'ttl', None))
                    ip_protocol = safe_int_convert(getattr(ip, 'proto', None))
                    ip_checksum = getattr(ip, 'checksum', None)
                    
                    # Opcional: opciones IP
                    ip_options = getattr(ip, 'opt', None)
                
                # Campos específicos IPv6
                elif ip_version == 6 and hasattr(packet, 'ipv6'):
                    ipv6 = packet.ipv6
                    ipv6_traffic_class = safe_int_convert(getattr(ipv6, 'tclass', None))
                    ipv6_flow_label = safe_int_convert(getattr(ipv6, 'flow', None))
                    ipv6_payload_length = safe_int_convert(getattr(ipv6, 'plen', None))
                    ipv6_next_header = safe_int_convert(getattr(ipv6, 'nxt', None))
                    ipv6_hop_limit = safe_int_convert(getattr(ipv6, 'hlim', None))
            
            elif hasattr(packet, 'ipv6'):  # A veces no hay capa 'ip' sino directamente 'ipv6'
                ipv6 = packet.ipv6
                ip_version = 6
                src_ip = getattr(ipv6, 'src', None)
                dst_ip = getattr(ipv6, 'dst', None)
                ipv6_traffic_class = safe_int_convert(getattr(ipv6, 'tclass', None))
                ipv6_flow_label = safe_int_convert(getattr(ipv6, 'flow', None))
                ipv6_payload_length = safe_int_convert(getattr(ipv6, 'plen', None))
                ipv6_next_header = safe_int_convert(getattr(ipv6, 'nxt', None))
                ipv6_hop_limit = safe_int_convert(getattr(ipv6, 'hlim', None))
            
            # Procesar ARP
            if hasattr(packet, 'arp'):
                arp = packet.arp
                arp_opcode = safe_int_convert(getattr(arp, 'opcode', None))
                arp_src_hw = getattr(arp, 'src_hw_mac', None)
                arp_dst_hw = getattr(arp, 'dst_hw_mac', None)
                arp_src_ip = getattr(arp, 'src_proto_ipv4', None)
                arp_dst_ip = getattr(arp, 'dst_proto_ipv4', None)
            
            # Procesar TCP
            if hasattr(packet, 'tcp'):
                tcp = packet.tcp
                transport_protocol = 'TCP'
                
                src_port = safe_int_convert(getattr(tcp, 'srcport', None))
                dst_port = safe_int_convert(getattr(tcp, 'dstport', None))
                
                tcp_seq_number = safe_int_convert(getattr(tcp, 'seq', None))
                tcp_ack_number = safe_int_convert(getattr(tcp, 'ack', None))
                tcp_header_length = safe_int_convert(getattr(tcp, 'hdr_len', None))
                
                # TCP Flags (como valor raw)
                tcp_flags_raw = safe_int_convert(getattr(tcp, 'flags', None), 16)
                
                # Flags individuales
                tcp_flag_ns = bool(safe_int_convert(getattr(tcp, 'flags_ns', None)))
                tcp_flag_cwr = bool(safe_int_convert(getattr(tcp, 'flags_cwr', None)))
                tcp_flag_ece = bool(safe_int_convert(getattr(tcp, 'flags_ecn', None)))
                tcp_flag_urg = bool(safe_int_convert(getattr(tcp, 'flags_urg', None)))
                tcp_flag_ack = bool(safe_int_convert(getattr(tcp, 'flags_ack', None)))
                tcp_flag_psh = bool(safe_int_convert(getattr(tcp, 'flags_push', None)))
                tcp_flag_rst = bool(safe_int_convert(getattr(tcp, 'flags_reset', None)))
                tcp_flag_syn = bool(safe_int_convert(getattr(tcp, 'flags_syn', None)))
                tcp_flag_fin = bool(safe_int_convert(getattr(tcp, 'flags_fin', None)))
                
                # Window y otros campos
                tcp_window_size = safe_int_convert(getattr(tcp, 'window_size', None))
                tcp_window_size_value = safe_int_convert(getattr(tcp, 'window_size_value', None))
                tcp_window_size_scalefactor = safe_int_convert(getattr(tcp, 'window_size_scalefactor', None))
                
                tcp_checksum = getattr(tcp, 'checksum', None)
                tcp_urgent_pointer = safe_int_convert(getattr(tcp, 'urgent_pointer', None))
                
                # Opciones TCP (representación de texto o JSON)
                tcp_options = getattr(tcp, 'options', None)
                
                # Opciones específicas comunes
                tcp_mss = safe_int_convert(getattr(tcp, 'options_mss_val', None))
                tcp_sack_permitted = bool(safe_int_convert(getattr(tcp, 'options_sack_perm', None)))
                tcp_ts_value = safe_int_convert(getattr(tcp, 'options_timestamp_tsval', None))
                tcp_ts_echo = safe_int_convert(getattr(tcp, 'options_timestamp_tsecr', None))
                
                # Análisis adicional TCP (fields from tcp.analysis)
                tcp_stream_index = safe_int_convert(getattr(tcp, 'stream', None))
                tcp_payload_size = safe_int_convert(getattr(tcp, 'len', None))
                tcp_analysis_flags = getattr(tcp, 'analysis_flags', None)
                tcp_analysis_rtt = safe_int_convert(getattr(tcp, 'analysis_rtt', None), default=0.0)
                tcp_keep_alive = bool(safe_int_convert(getattr(tcp, 'analysis_keep_alive', None)))
            
            # Procesar UDP
            elif hasattr(packet, 'udp'):
                udp = packet.udp
                transport_protocol = 'UDP'
                
                src_port = safe_int_convert(getattr(udp, 'srcport', None))
                dst_port = safe_int_convert(getattr(udp, 'dstport', None))
                
                udp_length = safe_int_convert(getattr(udp, 'length', None))
                udp_checksum = getattr(udp, 'checksum', None)
                
                udp_stream_index = safe_int_convert(getattr(udp, 'stream', None))
                udp_payload_size = len(getattr(udp, 'payload', b''))
            
            # Procesar ICMP
            elif hasattr(packet, 'icmp'):
                icmp = packet.icmp
                transport_protocol = 'ICMP'
                
                icmp_type = safe_int_convert(getattr(icmp, 'type', None))
                icmp_code = safe_int_convert(getattr(icmp, 'code', None))
                icmp_checksum = getattr(icmp, 'checksum', None)
                
                # Campos comunes para ciertos tipos de mensajes ICMP
                icmp_identifier = safe_int_convert(getattr(icmp, 'identifier', None))
                icmp_sequence = safe_int_convert(getattr(icmp, 'seq', None))
                icmp_gateway = getattr(icmp, 'gateway', None)
                icmp_length = safe_int_convert(getattr(icmp, 'length', None))
                icmp_mtu = safe_int_convert(getattr(icmp, 'mtu', None))
                icmp_unused = safe_int_convert(getattr(icmp, 'unused', None))
            
            # Procesar ICMPv6
            elif hasattr(packet, 'icmpv6'):
                icmpv6 = packet.icmpv6
                transport_protocol = 'ICMPv6'
                
                icmp_type = safe_int_convert(getattr(icmpv6, 'type', None))
                icmp_code = safe_int_convert(getattr(icmpv6, 'code', None))
                icmp_checksum = getattr(icmpv6, 'checksum', None)
                
                # Campos comunes para ciertos tipos de mensajes ICMPv6
                icmp_identifier = safe_int_convert(getattr(icmpv6, 'identifier', None))
                icmp_sequence = safe_int_convert(getattr(icmpv6, 'seq', None))
            
            # Información de texto
            info_text = getattr(packet, 'info', None)
            
        except Exception as e:
            print(f"Error durante el procesamiento de capas del paquete #{packet_number}: {e}")
            info_text = f"Error de procesamiento: {e}"
            is_error = True
        
        # Crear un nuevo objeto Packet
        try:
            new_packet = Packet(
                session_id=capture_session.id,
                packet_number=packet_number,
                timestamp=timestamp,
                capture_length=capture_length,
                packet_length=packet_length,
                capture_interface=capture_interface,
                frame_number=frame_number,
                
                # Capa 2 - Ethernet
                src_mac=src_mac,
                dst_mac=dst_mac,
                eth_type=eth_type,
                eth_dst_lg=eth_dst_lg,
                eth_dst_ig=eth_dst_ig,
                eth_src_lg=eth_src_lg,
                eth_src_ig=eth_src_ig,
                vlan_id=vlan_id,
                
                # PPP
                ppp_protocol=ppp_protocol,
                ppp_direction=ppp_direction,
                
                # Capa 3 - IP (común)
                ip_version=ip_version,
                src_ip=src_ip,
                dst_ip=dst_ip,
                
                # Capa 3 - IPv4 específico
                ip_header_length=ip_header_length,
                ip_dscp=ip_dscp,
                ip_ecn=ip_ecn,
                ip_total_length=ip_total_length,
                ip_identification=ip_identification,
                ip_flags=ip_flags,
                ip_flag_df=ip_flag_df,
                ip_flag_mf=ip_flag_mf,
                ip_fragment_offset=ip_fragment_offset,
                ip_ttl=ip_ttl,
                ip_protocol=ip_protocol,
                ip_checksum=ip_checksum,
                ip_options=ip_options,
                
                # Capa 3 - IPv6 específico
                ipv6_traffic_class=ipv6_traffic_class,
                ipv6_flow_label=ipv6_flow_label,
                ipv6_payload_length=ipv6_payload_length,
                ipv6_next_header=ipv6_next_header,
                ipv6_hop_limit=ipv6_hop_limit,
                ipv6_ext_headers=ipv6_ext_headers,
                
                # Capa 4 - Común
                transport_protocol=transport_protocol,
                src_port=src_port,
                dst_port=dst_port,
                
                # Capa 4 - TCP específico
                tcp_seq_number=tcp_seq_number,
                tcp_ack_number=tcp_ack_number,
                tcp_header_length=tcp_header_length,
                tcp_flags_raw=tcp_flags_raw,
                tcp_flag_ns=tcp_flag_ns,
                tcp_flag_cwr=tcp_flag_cwr,
                tcp_flag_ece=tcp_flag_ece,
                tcp_flag_urg=tcp_flag_urg,
                tcp_flag_ack=tcp_flag_ack,
                tcp_flag_psh=tcp_flag_psh,
                tcp_flag_rst=tcp_flag_rst,
                tcp_flag_syn=tcp_flag_syn,
                tcp_flag_fin=tcp_flag_fin,
                tcp_window_size=tcp_window_size,
                tcp_window_size_scalefactor=tcp_window_size_scalefactor,
                tcp_window_size_value=tcp_window_size_value,
                tcp_checksum=tcp_checksum,
                tcp_urgent_pointer=tcp_urgent_pointer,
                tcp_options=tcp_options,
                tcp_mss=tcp_mss,
                tcp_sack_permitted=tcp_sack_permitted,
                tcp_ts_value=tcp_ts_value,
                tcp_ts_echo=tcp_ts_echo,
                tcp_stream_index=tcp_stream_index,
                tcp_payload_size=tcp_payload_size,
                tcp_analysis_flags=tcp_analysis_flags,
                tcp_analysis_rtt=tcp_analysis_rtt,
                tcp_keep_alive=tcp_keep_alive,
                
                # Capa 4 - UDP específico
                udp_length=udp_length,
                udp_checksum=udp_checksum,
                udp_stream_index=udp_stream_index,
                udp_payload_size=udp_payload_size,
                
                # Capa 4 - ICMP específico
                icmp_type=icmp_type,
                icmp_code=icmp_code,
                icmp_checksum=icmp_checksum,
                icmp_identifier=icmp_identifier,
                icmp_sequence=icmp_sequence,
                icmp_gateway=icmp_gateway,
                icmp_length=icmp_length,
                icmp_mtu=icmp_mtu,
                icmp_unused=icmp_unused,
                
                # ARP específico
                arp_opcode=arp_opcode,
                arp_src_hw=arp_src_hw,
                arp_dst_hw=arp_dst_hw,
                arp_src_ip=arp_src_ip,
                arp_dst_ip=arp_dst_ip,
                
                # Metadatos adicionales
                delta_time=delta_time,
                
                # Campos generales de análisis
                info_text=info_text,
                is_error=is_error,
                is_malformed=is_malformed,
                protocol_stack=protocol_stack,
                frame_time_relative=frame_time_relative
            )
            
            db_session.add(new_packet)
            
            # Crear información específica de protocolo si es necesario
            # TCP Info
            if transport_protocol == 'TCP':
                tcp_info = TCPInfo(
                    packet=new_packet,
                    src_port=src_port,
                    dst_port=dst_port,
                    seq_number=tcp_seq_number,
                    ack_number=tcp_ack_number,
                    window_size=tcp_window_size,
                    header_length=tcp_header_length,
                    flag_syn=tcp_flag_syn,
                    flag_ack=tcp_flag_ack,
                    flag_fin=tcp_flag_fin,
                    flag_rst=tcp_flag_rst,
                    flag_psh=tcp_flag_psh,
                    flag_urg=tcp_flag_urg,
                    flag_ece=tcp_flag_ece,
                    flag_cwr=tcp_flag_cwr,
                    has_timestamp=tcp_ts_value is not None,
                    timestamp_value=tcp_ts_value,
                    timestamp_echo=tcp_ts_echo,
                    mss=tcp_mss,
                    window_scale=tcp_window_size_scalefactor
                )
                db_session.add(tcp_info)
                
            # UDP Info
            elif transport_protocol == 'UDP':
                udp_info = UDPInfo(
                    packet=new_packet,
                    src_port=src_port or 0,
                    dst_port=dst_port or 0,
                    length=udp_length
                )
                db_session.add(udp_info)
                
            # ICMP Info
            elif transport_protocol in ['ICMP', 'ICMPv6']:
                icmp_info = ICMPInfo(
                    packet=new_packet,
                    type=icmp_type or 0,
                    code=icmp_code or 0,
                    checksum=icmp_checksum,
                    identifier=icmp_identifier,
                    sequence=icmp_sequence,
                    description=f"Type: {icmp_type}, Code: {icmp_code}"
                )
                db_session.add(icmp_info)
            
            return True
            
        except Exception as e:
            print(f"Error al crear objeto de paquete #{packet_number}: {e}")
            import traceback
            traceback.print_exc()
            return False