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
                    
                    self._process_packet(db_session, capture_session, packet_number, packet)
                    packet_count += 1

                except StopIteration:
                    print("Fin de la iteración de paquetes.")
                    break
                except Exception as e:
                    error_packets += 1
                    print(f"Error al procesar el paquete pyshark #{packet_number}: {e}")

                if packet_number % 1000 == 0:
                    try:
                        db_session.commit()
                        print(f"Commit pyshark realizado tras {packet_number} paquetes")
                    except Exception as commit_error:
                        print(f"Error durante el commit periódico: {commit_error}")
                        db_session.rollback()
            
            try:
                db_session.commit()
            except Exception as final_commit_error:
                print(f"Error durante el commit final: {final_commit_error}")
                db_session.rollback()

            capture_session.packet_count = packet_count
            db_session.commit()
            
            cap.close()
            
            packet_count_db = db_session.query(Packet).filter(Packet.session_id == capture_session.id).count()
            tcp_count = db_session.query(TCPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            udp_count = db_session.query(UDPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            icmp_count = db_session.query(ICMPInfo).join(Packet).filter(Packet.session_id == capture_session.id).count()
            anomaly_count = db_session.query(Anomaly).join(Packet).filter(Packet.session_id == capture_session.id).count()
            
            print(f"\n===== RESUMEN DEL PROCESAMIENTO =====")
            print(f"Total de paquetes examinados (aprox): {packet_number_counter}")
            print(f"Paquetes procesados con éxito: {packet_count}")
            print(f"Paquetes con errores: {error_packets}")
            print(f"\nRegistros en la base de datos:")
            print(f"- Paquetes: {packet_count_db}")
            print(f"- TCP: {tcp_count}")
            print(f"- UDP: {udp_count}")
            print(f"- ICMP: {icmp_count}")
            print(f"- Anomalías: {anomaly_count}")
            
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
        Procesa un paquete individual (PyShark) y extrae información detallada de todas las capas.
        """
        # Variables para almacenar el timestamp del paquete anterior (para calcular delta)
        # Esta variable se mantendrá entre llamadas a _process_packet
        if not hasattr(self, '_last_packet_time'):
            self._last_packet_time = None
        
        # Metadatos básicos del paquete
        try:
            timestamp = float(packet.sniff_timestamp)
            capture_length = int(packet.captured_length) if hasattr(packet, 'captured_length') else None
            packet_length = int(packet.length) if hasattr(packet, 'length') else None
            
            # Calcular delta_time (tiempo desde el paquete anterior)
            delta_time = None
            if self._last_packet_time is not None:
                delta_time = timestamp - self._last_packet_time
            self._last_packet_time = timestamp
            
            # Obtener interfaz de captura si está disponible
            capture_interface = None
            frame_number = None
            if hasattr(packet, 'frame'):
                if hasattr(packet.frame, 'interface_id'):
                    capture_interface = packet.frame.interface_id
                if hasattr(packet.frame, 'number'):
                    frame_number = int(packet.frame.number)
        except AttributeError as e:
            print(f"Error accediendo a metadatos básicos del paquete #{packet_number}: {e}")
            return

        # Construir pila de protocolos
        protocol_stack = ",".join([layer.layer_name for layer in packet.layers])
        
        # Inicializar todas las variables que poblaremos
        # Capa 2 - Ethernet
        src_mac = dst_mac = eth_type = None
        vlan_id = None
        
        # Capa 3 - IP (común)
        ip_version = None
        src_ip = dst_ip = None
        
        # Capa 3 - IPv4
        ip_header_length = ip_dscp = ip_ecn = ip_total_length = None
        ip_identification = ip_flags = ip_flag_df = ip_flag_mf = None
        ip_fragment_offset = ip_ttl = ip_protocol = ip_checksum = None
        
        # Capa 3 - IPv6
        ipv6_traffic_class = ipv6_flow_label = ipv6_payload_length = None
        ipv6_next_header = ipv6_hop_limit = None
        
        # Capa 4 - Común
        transport_protocol = None
        src_port = dst_port = None
        
        # Capa 4 - TCP
        tcp_seq_number = tcp_ack_number = tcp_header_length = tcp_flags_raw = None
        tcp_flag_ns = tcp_flag_cwr = tcp_flag_ece = tcp_flag_urg = False
        tcp_flag_ack = tcp_flag_psh = tcp_flag_rst = tcp_flag_syn = tcp_flag_fin = False
        tcp_window_size = tcp_window_size_scalefactor = tcp_checksum = tcp_urgent_pointer = None
        tcp_options = tcp_mss = tcp_sack_permitted = tcp_ts_value = tcp_ts_echo = None
        tcp_stream_index = tcp_payload_size = tcp_analysis_flags = tcp_analysis_rtt = None
        
        # Capa 4 - UDP
        udp_length = udp_checksum = udp_stream_index = udp_payload_size = None
        
        # Capa 4 - ICMP
        icmp_type = icmp_code = icmp_checksum = icmp_identifier = None
        icmp_sequence = icmp_gateway = icmp_length = None
        
        # Protocolos de capa 7 y superior
        protocol = "UNKNOWN"
        
        # DNS
        dns_query_name = dns_query_type = dns_response_ips = dns_record_ttl = None
        
        # HTTP
        http_method = http_uri = http_host = http_user_agent = http_referer = None
        http_response_code = http_content_type = None
        
        # TLS/SSL
        tls_version = tls_cipher_suite = tls_server_name = None
        
        # ARP
        arp_opcode = arp_src_hw = arp_dst_hw = arp_src_ip = arp_dst_ip = None
        
        # DHCP
        dhcp_message_type = dhcp_requested_ip = dhcp_client_mac = None
        
        # Información general
        info_text = None
        is_error = is_malformed = False

        # Extraer información de la capa Ethernet
        if hasattr(packet, 'eth'):
            try:
                eth_layer = packet.eth
                src_mac = eth_layer.src
                dst_mac = eth_layer.dst
                if hasattr(eth_layer, 'type'):
                    eth_type = eth_layer.type
            except AttributeError as e:
                print(f"Error procesando capa Ethernet para paquete #{packet_number}: {e}")
        
        # Extraer información de VLAN si está presente
        if hasattr(packet, 'vlan'):
            try:
                vlan_layer = packet.vlan
                if hasattr(vlan_layer, 'id'):
                    vlan_id = int(vlan_layer.id)
            except (AttributeError, ValueError) as e:
                print(f"Error procesando capa VLAN para paquete #{packet_number}: {e}")
        
        # Procesar capa IP (v4/v6)
        ip_layer = None
        if hasattr(packet, 'ip'):
            ip_layer = packet.ip
            ip_version = 4
            transport_protocol = "IPv4"
        elif hasattr(packet, 'ipv6'):
            ip_layer = packet.ipv6
            ip_version = 6
            transport_protocol = "IPv6"
        
        # Extraer información detallada de IP
        if ip_layer:
            try:
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                
                # IPv4 específico
                if ip_version == 4:
                    # Header Length
                    if hasattr(ip_layer, 'hdr_len'):
                        ip_header_length = int(ip_layer.hdr_len)
                        
                    # DSCP & ECN (parte de ToS)
                    if hasattr(ip_layer, 'dsfield'):
                        try:
                            dsfield = int(ip_layer.dsfield, 16)
                            ip_dscp = dsfield >> 2  # 6 bits más significativos
                            ip_ecn = dsfield & 0x03  # 2 bits menos significativos
                        except (ValueError, TypeError):
                            pass
                    
                    # Total Length
                    if hasattr(ip_layer, 'len'):
                        ip_total_length = int(ip_layer.len)
                        
                    # Identification
                    if hasattr(ip_layer, 'id'):
                        try:
                            ip_identification = int(ip_layer.id, 16)
                        except (ValueError, TypeError):
                            pass
                    
                    # Flags & Fragment Offset
                    if hasattr(ip_layer, 'flags'):
                        try:
                            ip_flags = int(ip_layer.flags, 16)
                            # El bit DF (Don't Fragment) es 0x4000
                            ip_flag_df = bool(ip_flags & 0x4000)
                            # El bit MF (More Fragments) es 0x2000
                            ip_flag_mf = bool(ip_flags & 0x2000)
                        except (ValueError, TypeError):
                            pass
                            
                    if hasattr(ip_layer, 'frag_offset'):
                        try:
                            ip_fragment_offset = int(ip_layer.frag_offset)
                        except (ValueError, TypeError):
                            pass
                    
                    # TTL
                    if hasattr(ip_layer, 'ttl'):
                        ip_ttl = int(ip_layer.ttl)
                    
                    # Protocol
                    if hasattr(ip_layer, 'proto'):
                        ip_protocol = int(ip_layer.proto)
                    
                    # Checksum
                    if hasattr(ip_layer, 'checksum'):
                        ip_checksum = ip_layer.checksum
                
                # IPv6 específico
                elif ip_version == 6:
                    # Traffic Class
                    if hasattr(ip_layer, 'tclass'):
                        try:
                            ipv6_traffic_class = int(ip_layer.tclass, 16)
                        except (ValueError, TypeError):
                            pass
                    
                    # Flow Label
                    if hasattr(ip_layer, 'flow'):
                        try:
                            ipv6_flow_label = int(ip_layer.flow, 16)
                        except (ValueError, TypeError):
                            pass
                    
                    # Payload Length
                    if hasattr(ip_layer, 'plen'):
                        ipv6_payload_length = int(ip_layer.plen)
                    
                    # Next Header
                    if hasattr(ip_layer, 'nxt'):
                        ipv6_next_header = int(ip_layer.nxt)
                    
                    # Hop Limit
                    if hasattr(ip_layer, 'hlim'):
                        ipv6_hop_limit = int(ip_layer.hlim)
            
            except AttributeError as e:
                print(f"Error procesando capa IP para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa IP para paquete #{packet_number}: {e}")
        
        # Procesar capa de transporte (TCP, UDP, ICMP, ICMPv6)
        
        # TCP
        if hasattr(packet, 'tcp'):
            try:
                tcp_layer = packet.tcp
                transport_protocol = "TCP"
                
                # Puertos
                src_port = int(tcp_layer.srcport)
                dst_port = int(tcp_layer.dstport)
                
                # Números de secuencia y ACK
                if hasattr(tcp_layer, 'seq'):
                    tcp_seq_number = int(tcp_layer.seq)
                if hasattr(tcp_layer, 'ack'):
                    tcp_ack_number = int(tcp_layer.ack)
                
                # Longitud de cabecera
                if hasattr(tcp_layer, 'hdr_len'):
                    tcp_header_length = int(tcp_layer.hdr_len)
                
                # Flags TCP (como valor raw y desglosados)
                if hasattr(tcp_layer, 'flags'):
                    try:
                        tcp_flags_raw = int(tcp_layer.flags, 16)
                        # Desglosar flags individuales (orden: último bit es NS, primer bit es FIN)
                        # NS (ECN-Nonce concealment protection) - 0x100
                        tcp_flag_ns = bool(tcp_flags_raw & 0x100)
                        # CWR (Congestion Window Reduced) - 0x80
                        tcp_flag_cwr = bool(tcp_flags_raw & 0x80)
                        # ECE (ECN-Echo) - 0x40
                        tcp_flag_ece = bool(tcp_flags_raw & 0x40)
                        # URG (Urgent) - 0x20
                        tcp_flag_urg = bool(tcp_flags_raw & 0x20)
                        # ACK (Acknowledgment) - 0x10
                        tcp_flag_ack = bool(tcp_flags_raw & 0x10)
                        # PSH (Push) - 0x8
                        tcp_flag_psh = bool(tcp_flags_raw & 0x8)
                        # RST (Reset) - 0x4
                        tcp_flag_rst = bool(tcp_flags_raw & 0x4)
                        # SYN (Synchronize) - 0x2
                        tcp_flag_syn = bool(tcp_flags_raw & 0x2)
                        # FIN (Finish) - 0x1
                        tcp_flag_fin = bool(tcp_flags_raw & 0x1)
                    except (ValueError, TypeError):
                        pass
                
                # Window Size
                if hasattr(tcp_layer, 'window_size_value'):
                    tcp_window_size = int(tcp_layer.window_size_value)
                elif hasattr(tcp_layer, 'window'):
                    tcp_window_size = int(tcp_layer.window)
                
                # Checksum
                if hasattr(tcp_layer, 'checksum'):
                    tcp_checksum = tcp_layer.checksum
                
                # Urgent Pointer
                if hasattr(tcp_layer, 'urgent_pointer'):
                    tcp_urgent_pointer = int(tcp_layer.urgent_pointer)
                
                # Opciones TCP
                tcp_options_parts = []
                
                # MSS (Maximum Segment Size)
                if hasattr(tcp_layer, 'options_mss_val'):
                    tcp_mss = int(tcp_layer.options_mss_val)
                    tcp_options_parts.append(f"MSS={tcp_mss}")
                
                # SACK Permitted
                if hasattr(tcp_layer, 'options_sack_perm'):
                    tcp_sack_permitted = True
                    tcp_options_parts.append("SACK_PERM=1")
                
                # Timestamps
                if hasattr(tcp_layer, 'options_timestamp_tsval'):
                    tcp_ts_value = int(tcp_layer.options_timestamp_tsval)
                    tcp_options_parts.append(f"TSval={tcp_ts_value}")
                if hasattr(tcp_layer, 'options_timestamp_tsecr'):
                    tcp_ts_echo = int(tcp_layer.options_timestamp_tsecr)
                    tcp_options_parts.append(f"TSecr={tcp_ts_echo}")
                
                # Window Scale
                if hasattr(tcp_layer, 'options_wscale_val'):
                    tcp_window_size_scalefactor = int(tcp_layer.options_wscale_val)
                    tcp_options_parts.append(f"WS={tcp_window_size_scalefactor}")
                
                # Reunir opciones como string
                if tcp_options_parts:
                    tcp_options = "; ".join(tcp_options_parts)
                
                # Stream index
                if hasattr(tcp_layer, 'stream'):
                    tcp_stream_index = int(tcp_layer.stream)
                
                # Payload Size
                if hasattr(tcp_layer, 'payload'):
                    tcp_payload_size = len(tcp_layer.payload)
                
                # Análisis TCP (flags de análisis, RTT)
                if hasattr(tcp_layer, 'analysis_flags'):
                    tcp_analysis_flags = tcp_layer.analysis_flags
                
                if hasattr(tcp_layer, 'analysis_rtt'):
                    try:
                        tcp_analysis_rtt = float(tcp_layer.analysis_rtt)
                    except (ValueError, TypeError):
                        pass
                
                protocol = "TCP"  # Protocolo de alto nivel
                
            except AttributeError as e:
                print(f"Error procesando capa TCP para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa TCP para paquete #{packet_number}: {e}")
        
        # UDP
        elif hasattr(packet, 'udp'):
            try:
                udp_layer = packet.udp
                transport_protocol = "UDP"
                
                # Puertos
                src_port = int(udp_layer.srcport)
                dst_port = int(udp_layer.dstport)
                
                # Longitud
                if hasattr(udp_layer, 'length'):
                    udp_length = int(udp_layer.length)
                
                # Checksum
                if hasattr(udp_layer, 'checksum'):
                    udp_checksum = udp_layer.checksum
                
                # Stream index
                if hasattr(udp_layer, 'stream'):
                    udp_stream_index = int(udp_layer.stream)
                
                # Payload Size - si es accesible
                if hasattr(udp_layer, 'payload'):
                    udp_payload_size = len(udp_layer.payload)
                
                protocol = "UDP"  # Protocolo de alto nivel
                
            except AttributeError as e:
                print(f"Error procesando capa UDP para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa UDP para paquete #{packet_number}: {e}")
        
        # ICMP
        elif hasattr(packet, 'icmp'):
            try:
                icmp_layer = packet.icmp
                transport_protocol = "ICMP"
                
                # Type & Code
                if hasattr(icmp_layer, 'type'):
                    icmp_type = int(icmp_layer.type)
                if hasattr(icmp_layer, 'code'):
                    icmp_code = int(icmp_layer.code)
                
                # Checksum
                if hasattr(icmp_layer, 'checksum'):
                    try:
                        icmp_checksum = icmp_layer.checksum
                    except (ValueError, TypeError):
                        pass
                
                # Identifier (para Echo Request/Reply)
                if hasattr(icmp_layer, 'id'):
                    try:
                        icmp_identifier = int(icmp_layer.id)
                    except (ValueError, TypeError):
                        pass
                
                # Sequence Number (para Echo Request/Reply)
                if hasattr(icmp_layer, 'seq'):
                    try:
                        icmp_sequence = int(icmp_layer.seq)
                    except (ValueError, TypeError):
                        pass
                
                # Gateway (para Redirect)
                if hasattr(icmp_layer, 'gateway'):
                    icmp_gateway = icmp_layer.gateway
                
                # Length (si está disponible)
                if hasattr(icmp_layer, 'length'):
                    try:
                        icmp_length = int(icmp_layer.length)
                    except (ValueError, TypeError):
                        pass
                
                protocol = "ICMP"  # Protocolo de alto nivel
                
            except AttributeError as e:
                print(f"Error procesando capa ICMP para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa ICMP para paquete #{packet_number}: {e}")
        
        # ICMPv6
        elif hasattr(packet, 'icmpv6'):
            try:
                icmpv6_layer = packet.icmpv6
                transport_protocol = "ICMPv6"
                
                # Type & Code
                if hasattr(icmpv6_layer, 'type'):
                    icmp_type = int(icmpv6_layer.type)
                if hasattr(icmpv6_layer, 'code'):
                    icmp_code = int(icmpv6_layer.code)
                
                # Checksum
                if hasattr(icmpv6_layer, 'checksum'):
                    try:
                        icmp_checksum = icmpv6_layer.checksum
                    except (ValueError, TypeError):
                        pass
                
                protocol = "ICMPv6"  # Protocolo de alto nivel
                
            except AttributeError as e:
                print(f"Error procesando capa ICMPv6 para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa ICMPv6 para paquete #{packet_number}: {e}")
        
        # ARP
        elif hasattr(packet, 'arp'):
            try:
                arp_layer = packet.arp
                transport_protocol = "ARP"
                
                # Opcode
                if hasattr(arp_layer, 'opcode'):
                    arp_opcode = int(arp_layer.opcode)
                
                # MAC addresses
                if hasattr(arp_layer, 'src_hw_mac'):
                    arp_src_hw = arp_layer.src_hw_mac
                if hasattr(arp_layer, 'dst_hw_mac'):
                    arp_dst_hw = arp_layer.dst_hw_mac
                
                # IP addresses
                if hasattr(arp_layer, 'src_proto_ipv4'):
                    arp_src_ip = arp_layer.src_proto_ipv4
                if hasattr(arp_layer, 'dst_proto_ipv4'):
                    arp_dst_ip = arp_layer.dst_proto_ipv4
                
                protocol = "ARP"  # Protocolo de alto nivel
                
                # Info text
                arp_action = "request" if arp_opcode == 1 else "reply"
                info_text = f"ARP {arp_action} {arp_src_ip} -> {arp_dst_ip}"
                
            except AttributeError as e:
                print(f"Error procesando capa ARP para paquete #{packet_number}: {e}")
            except ValueError as e:
                print(f"Error de conversión en capa ARP para paquete #{packet_number}: {e}")
        
        # Protocolos de aplicación (L7)
        
        # DNS
        if hasattr(packet, 'dns'):
            try:
                dns_layer = packet.dns
                
                # Consulta DNS
                if hasattr(dns_layer, 'qry_name'):
                    dns_query_name = dns_layer.qry_name
                    if hasattr(dns_layer, 'qry_type'):
                        dns_query_type = self._get_dns_type_name(dns_layer.qry_type)
                
                # Respuesta DNS
                ips = []
                if hasattr(dns_layer, 'a'):
                    if isinstance(dns_layer.a, str) and ',' in dns_layer.a:
                        ips.extend(dns_layer.a.split(','))
                    else:
                        try:
                            ips.append(str(dns_layer.a))
                        except TypeError:
                            try:
                                ips.extend(list(dns_layer.a))
                            except (TypeError, ValueError):
                                pass
                
                # IPv6 AAAA records
                if hasattr(dns_layer, 'aaaa'):
                    if isinstance(dns_layer.aaaa, str) and ',' in dns_layer.aaaa:
                        ips.extend(dns_layer.aaaa.split(','))
                    else:
                        try:
                            ips.append(str(dns_layer.aaaa))
                        except TypeError:
                            try:
                                ips.extend(list(dns_layer.aaaa))
                            except (TypeError, ValueError):
                                pass
                
                # Combinar IPs
                if ips:
                    dns_response_ips = ",".join([ip for ip in ips if ip])
                
                # TTL del registro
                if hasattr(dns_layer, 'a_ttl'):
                    try:
                        dns_record_ttl = int(dns_layer.a_ttl)
                    except (ValueError, TypeError):
                        pass
                
                # Cambiar el protocolo a DNS si no tenemos uno mejor
                if protocol in ["TCP", "UDP"]:
                    protocol = "DNS"
                
                # Info Text
                if dns_query_name:
                    info_text = f"DNS Query: {dns_query_name} ({dns_query_type})"
                elif dns_response_ips:
                    info_text = f"DNS Response: {dns_query_name} -> {dns_response_ips}"
                
            except AttributeError as e:
                print(f"Error procesando capa DNS para paquete #{packet_number}: {e}")
        
        # HTTP
        if hasattr(packet, 'http'):
            try:
                http_layer = packet.http
                
                # Método HTTP (solicitud)
                if hasattr(http_layer, 'request_method'):
                    http_method = http_layer.request_method
                    protocol = "HTTP"
                
                # URI (solicitud)
                if hasattr(http_layer, 'request_uri'):
                    http_uri = http_layer.request_uri
                
                # Host (solicitud)
                if hasattr(http_layer, 'host'):
                    http_host = http_layer.host
                
                # User-Agent (solicitud)
                if hasattr(http_layer, 'user_agent'):
                    http_user_agent = http_layer.user_agent
                
                # Referer (solicitud)
                if hasattr(http_layer, 'referer'):
                    http_referer = http_layer.referer
                
                # Código de respuesta
                if hasattr(http_layer, 'response_code'):
                    try:
                        http_response_code = int(http_layer.response_code)
                        protocol = "HTTP"
                    except (ValueError, TypeError):
                        pass
                
                # Content-Type (respuesta)
                if hasattr(http_layer, 'content_type'):
                    http_content_type = http_layer.content_type
                
                # Info Text
                if http_method and http_uri:
                    info_text = f"HTTP {http_method} {http_uri}"
                elif http_response_code:
                    info_text = f"HTTP Response {http_response_code}"
                    if http_content_type:
                        info_text += f" ({http_content_type})"
                
            except AttributeError as e:
                print(f"Error procesando capa HTTP para paquete #{packet_number}: {e}")
        
        # TLS/SSL
        if hasattr(packet, 'tls') or hasattr(packet, 'ssl'):
            try:
                ssl_layer = packet.tls if hasattr(packet, 'tls') else packet.ssl
                
                # Versión
                if hasattr(ssl_layer, 'record_version'):
                    tls_version = ssl_layer.record_version
                elif hasattr(ssl_layer, 'handshake_version'):
                    tls_version = ssl_layer.handshake_version
                
                # Cipher Suite
                if hasattr(ssl_layer, 'handshake_ciphersuite'):
                    tls_cipher_suite = ssl_layer.handshake_ciphersuite
                
                # SNI (Server Name Indication)
                if hasattr(ssl_layer, 'handshake_extensions_server_name'):
                    tls_server_name = ssl_layer.handshake_extensions_server_name
                
                protocol = "TLS/SSL"
                
                # Info Text
                if tls_version:
                    info_text = f"TLS {tls_version}"
                    if tls_server_name:
                        info_text += f" (SNI: {tls_server_name})"
                
            except AttributeError as e:
                print(f"Error procesando capa TLS/SSL para paquete #{packet_number}: {e}")
        
        # DHCP
        if hasattr(packet, 'dhcp'):
            try:
                dhcp_layer = packet.dhcp
                
                # Tipo de mensaje
                if hasattr(dhcp_layer, 'option_dhcp'):
                    dhcp_message_type = dhcp_layer.option_dhcp
                
                # IP solicitada
                if hasattr(dhcp_layer, 'option_requested_ip_address'):
                    dhcp_requested_ip = dhcp_layer.option_requested_ip_address
                
                # MAC del cliente
                if hasattr(dhcp_layer, 'hw_mac_addr'):
                    dhcp_client_mac = dhcp_layer.hw_mac_addr
                
                protocol = "DHCP"
                
                # Info Text
                if dhcp_message_type:
                    info_text = f"DHCP {dhcp_message_type}"
                    if dhcp_requested_ip:
                        info_text += f" for {dhcp_requested_ip}"
                
            except AttributeError as e:
                print(f"Error procesando capa DHCP para paquete #{packet_number}: {e}")
        
        # Si no hay texto informativo, usar el protocolo o el nivel más alto
        if not info_text and hasattr(packet, 'highest_layer'):
            highest_layer = packet.highest_layer
            if highest_layer and highest_layer != protocol:
                info_text = f"{highest_layer} Packet"
            else:
                info_text = f"{protocol} Packet"
        
        # Detectar paquetes malformados o con errores
        for layer in packet.layers:
            layer_name = layer.layer_name.lower()
            if 'malformed' in layer_name or 'error' in layer_name:
                is_malformed = True
                is_error = True
                if not info_text or not info_text.startswith("ERROR:"):
                    info_text = f"ERROR: Malformed packet - {layer.layer_name}"
                break
        
        # Crear el objeto Packet con toda la información recopilada
        new_packet = Packet(
            session_id=capture_session.id,
            packet_number=packet_number,
            timestamp=timestamp,
            capture_length=capture_length,
            packet_length=packet_length,
            capture_interface=capture_interface,
            frame_number=frame_number,
            delta_time=delta_time,
            
            # Ethernet (L2)
            src_mac=src_mac,
            dst_mac=dst_mac,
            eth_type=eth_type,
            vlan_id=vlan_id,
            
            # IP (L3) - común
            ip_version=ip_version,
            src_ip=src_ip,
            dst_ip=dst_ip,
            
            # IPv4 específico
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
            
            # IPv6 específico
            ipv6_traffic_class=ipv6_traffic_class,
            ipv6_flow_label=ipv6_flow_label,
            ipv6_payload_length=ipv6_payload_length,
            ipv6_next_header=ipv6_next_header,
            ipv6_hop_limit=ipv6_hop_limit,
            
            # Transporte (L4) común
            transport_protocol=transport_protocol,
            src_port=src_port,
            dst_port=dst_port,
            
            # TCP específico
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
            
            # UDP específico
            udp_length=udp_length,
            udp_checksum=udp_checksum,
            udp_stream_index=udp_stream_index,
            udp_payload_size=udp_payload_size,
            
            # ICMP específico
            icmp_type=icmp_type,
            icmp_code=icmp_code,
            icmp_checksum=icmp_checksum,
            icmp_identifier=icmp_identifier,
            icmp_sequence=icmp_sequence,
            icmp_gateway=icmp_gateway,
            icmp_length=icmp_length,
            
            # Capa 7 (Aplicación)
            protocol=protocol,
            
            # DNS
            dns_query_name=dns_query_name,
            dns_query_type=dns_query_type,
            dns_response_ips=dns_response_ips,
            dns_record_ttl=dns_record_ttl,
            
            # HTTP
            http_method=http_method,
            http_uri=http_uri,
            http_host=http_host,
            http_user_agent=http_user_agent,
            http_referer=http_referer,
            http_response_code=http_response_code,
            http_content_type=http_content_type,
            
            # TLS/SSL
            tls_version=tls_version,
            tls_cipher_suite=tls_cipher_suite,
            tls_server_name=tls_server_name,
            
            # ARP
            arp_opcode=arp_opcode,
            arp_src_hw=arp_src_hw,
            arp_dst_hw=arp_dst_hw,
            arp_src_ip=arp_src_ip,
            arp_dst_ip=arp_dst_ip,
            
            # DHCP
            dhcp_message_type=dhcp_message_type,
            dhcp_requested_ip=dhcp_requested_ip,
            dhcp_client_mac=dhcp_client_mac,
            
            # Campos generales
            info_text=info_text,
            is_error=is_error,
            is_malformed=is_malformed,
            protocol_stack=protocol_stack
        )
        
        # Añadir a la sesión y obtener el ID
        db_session.add(new_packet)
        db_session.flush()
        
        # Detectar anomalías
        self._detect_anomalies(db_session, new_packet, packet)
    
    def _get_dns_type_name(self, qtype):
        """
        Convierte un tipo numérico de consulta DNS a su nombre correspondiente.
        """
        dns_types = {
            "1": "A",
            "2": "NS",
            "5": "CNAME",
            "6": "SOA",
            "12": "PTR",
            "15": "MX",
            "16": "TXT",
            "28": "AAAA",
            "33": "SRV"
        }
        # Puede ser un entero, una cadena, o tener formato diferente
        type_str = str(qtype)
        return dns_types.get(type_str, type_str)

    def _process_tcp_packet(self, db_session, packet, tcp_layer):
        """
        Procesa un paquete TCP (PyShark) y almacena la información TCP.
        """
        try:
            flags = int(tcp_layer.flags, 16) if hasattr(tcp_layer, 'flags') else 0
            tcp_info = TCPInfo(
                packet_id=packet.id,
                src_port=int(tcp_layer.srcport),
                dst_port=int(tcp_layer.dstport),
                seq_number=int(tcp_layer.seq) if hasattr(tcp_layer, 'seq') else None,
                ack_number=int(tcp_layer.ack) if hasattr(tcp_layer, 'ack') else None,
                window_size=int(tcp_layer.window_size_value) if hasattr(tcp_layer, 'window_size_value') else None,
                header_length=int(tcp_layer.hdr_len) if hasattr(tcp_layer, 'hdr_len') else None,
                flag_syn=(flags & 0x02) != 0,
                flag_ack=(flags & 0x10) != 0,
                flag_fin=(flags & 0x01) != 0,
                flag_rst=(flags & 0x04) != 0,
                flag_psh=(flags & 0x08) != 0,
                flag_urg=(flags & 0x20) != 0,
                flag_ece=(flags & 0x40) != 0,
                flag_cwr=(flags & 0x80) != 0,
                has_timestamp=hasattr(tcp_layer, 'options_timestamp_tsval'),
                timestamp_value=int(tcp_layer.options_timestamp_tsval) if hasattr(tcp_layer, 'options_timestamp_tsval') else None,
                timestamp_echo=int(tcp_layer.options_timestamp_tsecr) if hasattr(tcp_layer, 'options_timestamp_tsecr') else None,
                mss=int(tcp_layer.options_mss_val) if hasattr(tcp_layer, 'options_mss_val') else None,
                window_scale=int(tcp_layer.options_wscale_val) if hasattr(tcp_layer, 'options_wscale_val') else None
            )
            db_session.add(tcp_info)
        except AttributeError as e:
            print(f"Error processing TCP details for packet {packet.id}: {e}")
        except ValueError as e:
             print(f"Error converting TCP value for packet {packet.id}: {e}")

    def _process_udp_packet(self, db_session, packet, udp_layer):
        """
        Procesa un paquete UDP (PyShark) y almacena la información UDP.
        """
        try:
            udp_info = UDPInfo(
                packet_id=packet.id,
                src_port=int(udp_layer.srcport),
                dst_port=int(udp_layer.dstport),
                length=int(udp_layer.length) if hasattr(udp_layer, 'length') else None
            )
            db_session.add(udp_info)
        except AttributeError as e:
            print(f"Error processing UDP details for packet {packet.id}: {e}")
        except ValueError as e:
             print(f"Error converting UDP value for packet {packet.id}: {e}")

    def _process_icmp_packet(self, db_session, packet, icmp_layer, protocol):
        """
        Procesa un paquete ICMP (PyShark) y almacena la información ICMP.
        """
        icmp_types = { 0: "Echo Reply", 3: "Destination Unreachable" }
        icmpv6_types = { 1: "Destination Unreachable", 2: "Packet Too Big" }
        try:
            icmp_type = int(icmp_layer.type) if hasattr(icmp_layer, 'type') else 0
            icmp_code = int(icmp_layer.code) if hasattr(icmp_layer, 'code') else 0
            
            if protocol == 'ICMP':
                icmp_type_name = icmp_types.get(icmp_type, "Unknown")
            else:
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
        except AttributeError as e:
            print(f"Error processing ICMP details for packet {packet.id}: {e}")
        except ValueError as e:
             print(f"Error converting ICMP value for packet {packet.id}: {e}")

    def _detect_anomalies(self, db_session, packet, pyshark_packet=None):
        """
        Detecta posibles anomalías en un paquete. 
        
        Args:
            db_session: Sesión de base de datos activa
            packet: Objeto Packet de SQLAlchemy (ya tiene todos los campos populados)
            pyshark_packet: (opcional) Objeto de paquete de PyShark original
        """
        anomalies = []
        
        # Anomalías basadas en campos de TCP
        if packet.protocol == 'TCP':
            # Usar tcp_flags_raw si está disponible, o inferir desde flags individuales
            if packet.tcp_flags_raw is not None:
                tcp_flags = packet.tcp_flags_raw
            else:
                tcp_flags = 0
                if packet.tcp_flag_fin: tcp_flags |= 0x01
                if packet.tcp_flag_syn: tcp_flags |= 0x02
                if packet.tcp_flag_rst: tcp_flags |= 0x04
                if packet.tcp_flag_psh: tcp_flags |= 0x08
                if packet.tcp_flag_ack: tcp_flags |= 0x10
                if packet.tcp_flag_urg: tcp_flags |= 0x20
                if packet.tcp_flag_ece: tcp_flags |= 0x40
                if packet.tcp_flag_cwr: tcp_flags |= 0x80
                if packet.tcp_flag_ns:  tcp_flags |= 0x100
                
            # Escaneo Xmas (FIN, PSH, URG flags activos, otros inactivos)
            if (tcp_flags & 0x29) == 0x29 and not (tcp_flags & 0x16):
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Xmas Scan",
                        description="Posible escaneo Xmas detectado (FIN+PSH+URG flags activos)",
                        severity="alta"
                    )
                )
            
            # Escaneo NULL (ningún flag activo)
            if tcp_flags == 0:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="NULL Scan",
                        description="Posible escaneo NULL detectado (ningún flag TCP activo)",
                        severity="alta"
                    )
                )
                
            # Combinación inválida de flags SYN+FIN
            if (tcp_flags & 0x03) == 0x03:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Invalid Flags",
                        description="Combinación inválida de flags TCP (SYN+FIN)",
                        severity="media"
                    )
                )
                
            # Combinación inválida de flags RST+SYN (menos común pero posible ataque)
            if (tcp_flags & 0x06) == 0x06:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Invalid Flags",
                        description="Combinación inválida de flags TCP (RST+SYN)",
                        severity="media"
                    )
                )
                
            # RST flood (requeriría contexto adicional, pero podemos marcar para futura detección)
            if packet.tcp_flag_rst and not (packet.tcp_flag_ack or packet.tcp_flag_syn):
                # Aquí podríamos agregar lógica para detectar patrones de RST flood si agregamos análisis entre distintos paquetes
                pass
                
            # Flags TCP todos activos (altamente sospechoso)
            if tcp_flags == 0x1FF:  # Todos los 9 flags TCP activados
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="All TCP Flags",
                        description="Paquete con todos los flags TCP activos (altamente sospechoso)",
                        severity="alta"
                    )
                )
        
        # Fragmentación sospechosa
        if packet.ip_flag_mf or (packet.ip_fragment_offset is not None and packet.ip_fragment_offset > 0):
            # Fragmento con offset muy pequeño (puede ser usado para evasión)
            if packet.ip_fragment_offset == 1:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Suspicious Fragment",
                        description="Fragmento con offset sospechosamente pequeño (1 byte)",
                        severity="media"
                    )
                )
                
            # Fragmentos solapados (necesitaríamos análisis multifrag)
            # (Se podría implementar en un análisis de segundo nivel)
        
        # TTL muy bajo (posible escaneo o comportamiento anómalo)
        ttl_value = packet.ip_ttl if packet.ip_ttl is not None else packet.ipv6_hop_limit
        if ttl_value is not None and ttl_value < 5:
            anomalies.append(
                Anomaly(
                    packet_id=packet.id,
                    type="Low TTL",
                    description=f"TTL/Hop Limit muy bajo ({ttl_value}), posible comportamiento anómalo",
                    severity="baja"
                )
            )
            
        # Anomalías en la longitud de los paquetes
        if packet.tcp_header_length is not None and packet.ip_header_length is not None:
            # Cabeceras gigantes
            if packet.tcp_header_length > 60:  # TCP máximo normal ~60 bytes
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Oversized Header",
                        description=f"Cabecera TCP anormalmente grande ({packet.tcp_header_length} bytes)",
                        severity="baja"
                    )
                )
                
            if packet.ip_header_length > 60:  # IPv4 máximo normal ~60 bytes
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Oversized Header",
                        description=f"Cabecera IP anormalmente grande ({packet.ip_header_length} bytes)",
                        severity="baja"
                    )
                )
                
        # Anomalías específicas de protocolo
        if packet.protocol == "DNS" and packet.dns_query_name is not None:
            # Detección de nombres DNS sospechosamente largos (posible tunneling/exfiltración)
            if packet.dns_query_name and len(packet.dns_query_name) > 50:
                anomalies.append(
                    Anomaly(
                        packet_id=packet.id,
                        type="Suspicious DNS",
                        description=f"Nombre de consulta DNS anormalmente largo ({len(packet.dns_query_name)} caracteres)",
                        severity="baja"
                    )
                )
                
            # Consultas DNS para dominios conocidos maliciosos (esto requeriría una base de bloques)
            suspicious_domains = ["malware.", "phishing.", "blocked."]
            for domain in suspicious_domains:
                if packet.dns_query_name and domain in packet.dns_query_name.lower():
                    anomalies.append(
                        Anomaly(
                            packet_id=packet.id,
                            type="Suspicious Domain",
                            description=f"Posible consulta a dominio malicioso: {packet.dns_query_name}",
                            severity="media"
                        )
                    )
        
        # Añadir marca de malformed/error si se detectó durante el procesamiento
        if packet.is_malformed or packet.is_error:
            anomalies.append(
                Anomaly(
                    packet_id=packet.id,
                    type="Malformed Packet",
                    description=f"Paquete malformado: {packet.info_text}",
                    severity="media"
                )
            )
        
        # Añadir todas las anomalías detectadas a la base de datos
        for anomaly in anomalies:
            db_session.add(anomaly)
