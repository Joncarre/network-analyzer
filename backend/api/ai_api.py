from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import sessionmaker
import glob
from datetime import datetime

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
    Procesa una consulta en lenguaje natural y retorna la respuesta.
    
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
                
                # Análisis detallado por protocolos para esta sesión específica
                protocol_rows = db_session.query(Packet.transport_protocol, func.count(Packet.id)).filter(
                    Packet.session_id == chat_request.session_id
                ).group_by(Packet.transport_protocol).all()
                protocol_counts = {protocol: count for protocol, count in protocol_rows}
                
                # Análisis TCP específico de la sesión
                tcp_session_analysis = {}
                if 'TCP' in protocol_counts:
                    tcp_syn = db_session.query(func.count(Packet.id)).filter(
                        Packet.session_id == chat_request.session_id,
                        Packet.transport_protocol == 'TCP',
                        Packet.tcp_flag_syn == True,
                        Packet.tcp_flag_ack == False
                    ).scalar()
                    
                    tcp_rst = db_session.query(func.count(Packet.id)).filter(
                        Packet.session_id == chat_request.session_id,
                        Packet.transport_protocol == 'TCP',
                        Packet.tcp_flag_rst == True
                    ).scalar()
                    
                    tcp_fin = db_session.query(func.count(Packet.id)).filter(
                        Packet.session_id == chat_request.session_id,
                        Packet.transport_protocol == 'TCP',
                        Packet.tcp_flag_fin == True
                    ).scalar()
                    
                    tcp_session_analysis = {
                        "syn_packets": tcp_syn,
                        "rst_packets": tcp_rst,
                        "fin_packets": tcp_fin,
                        "total_tcp": protocol_counts.get('TCP', 0)
                    }
                
                # Top IPs en esta sesión
                top_src_ips_session = db_session.query(
                    Packet.src_ip,
                    func.count(Packet.id).label('count')
                ).filter(Packet.session_id == chat_request.session_id).group_by(
                    Packet.src_ip
                ).order_by(func.count(Packet.id).desc()).limit(10).all()
                
                top_dst_ips_session = db_session.query(
                    Packet.dst_ip,
                    func.count(Packet.id).label('count')
                ).filter(Packet.session_id == chat_request.session_id).group_by(
                    Packet.dst_ip
                ).order_by(func.count(Packet.id).desc()).limit(10).all()
                
                # Puertos más atacados en esta sesión
                top_ports_session = db_session.query(
                    Packet.dst_port,
                    func.count(Packet.id).label('count')
                ).filter(
                    Packet.session_id == chat_request.session_id,
                    Packet.dst_port.is_not(None)
                ).group_by(Packet.dst_port).order_by(func.count(Packet.id).desc()).limit(15).all()
                
                # Análisis temporal de la sesión
                session_temporal = {}
                first_packet = db_session.query(Packet.timestamp).filter(
                    Packet.session_id == chat_request.session_id
                ).order_by(Packet.timestamp).first()
                last_packet = db_session.query(Packet.timestamp).filter(
                    Packet.session_id == chat_request.session_id
                ).order_by(Packet.timestamp.desc()).first()
                
                if first_packet and last_packet:
                    duration = last_packet[0] - first_packet[0]
                    pps = packet_count / duration if duration > 0 else 0
                    session_temporal = {
                        "duration_seconds": round(duration, 2),
                        "packets_per_second": round(pps, 2),
                        "start_time": datetime.fromtimestamp(first_packet[0]).strftime('%Y-%m-%d %H:%M:%S'),
                        "end_time": datetime.fromtimestamp(last_packet[0]).strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                # Tamaños de paquetes en la sesión
                size_stats = db_session.query(
                    func.avg(Packet.packet_length),
                    func.max(Packet.packet_length),
                    func.min(Packet.packet_length)
                ).filter(Packet.session_id == chat_request.session_id).first()
                
                # Anomalías específicas de esta sesión
                anomaly_count = db_session.query(func.count(Anomaly.id)).join(
                    Packet, Packet.id == Anomaly.packet_id
                ).filter(Packet.session_id == chat_request.session_id).scalar()
                
                session_anomalies = db_session.query(
                    Anomaly.type,
                    func.count(Anomaly.id).label('count')
                ).join(Packet, Packet.id == Anomaly.packet_id).filter(
                    Packet.session_id == chat_request.session_id
                ).group_by(Anomaly.type).all()
                
                session_data = {
                    "session_id": chat_request.session_id,
                    "file_name": capture.file_name,
                    "packet_count": packet_count,
                    "protocols": protocol_counts,
                    "tcp_detailed_analysis": tcp_session_analysis,
                    "top_source_ips": [{"ip": ip, "packets": count} for ip, count in top_src_ips_session],
                    "top_destination_ips": [{"ip": ip, "packets": count} for ip, count in top_dst_ips_session],
                    "most_targeted_ports": [{"port": port, "packets": count} for port, count in top_ports_session if port],
                    "temporal_analysis": session_temporal,
                    "packet_sizes": {
                        "average": round(size_stats[0], 2) if size_stats[0] else 0,
                        "maximum": size_stats[1] if size_stats[1] else 0,
                        "minimum": size_stats[2] if size_stats[2] else 0
                    },
                    "anomaly_count": anomaly_count,
                    "anomalies_by_type": [{"type": anom_type, "count": count} for anom_type, count in session_anomalies]
                }
                
            elif chat_request.db_file:
                db_session = get_db_session(chat_request.db_file)
                # Estadísticas globales enriquecidas si no hay session_id
                total_packets = db_session.query(func.count(Packet.id)).scalar()
                udp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol == 'UDP').scalar()
                tcp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol == 'TCP').scalar()
                icmp_packets = db_session.query(func.count(Packet.id)).filter(Packet.transport_protocol.like('ICMP%')).scalar()
                
                # Análisis detallado de TCP - flags y patrones sospechosos
                tcp_syn_packets = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_syn == True,
                    Packet.tcp_flag_ack == False
                ).scalar()
                
                tcp_rst_packets = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_rst == True
                ).scalar()
                
                tcp_fin_packets = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_fin == True
                ).scalar()
                
                # Top IPs más activas (posibles atacantes)
                top_src_ips = db_session.query(
                    Packet.src_ip,
                    func.count(Packet.id).label('count')
                ).group_by(Packet.src_ip).order_by(func.count(Packet.id).desc()).limit(10).all()
                
                top_dst_ips = db_session.query(
                    Packet.dst_ip,
                    func.count(Packet.id).label('count')
                ).group_by(Packet.dst_ip).order_by(func.count(Packet.id).desc()).limit(10).all()
                
                # Puertos más atacados
                top_dst_ports = db_session.query(
                    Packet.dst_port,
                    func.count(Packet.id).label('count')
                ).filter(Packet.dst_port.is_not(None)).group_by(Packet.dst_port).order_by(func.count(Packet.id).desc()).limit(15).all()
                
                # Análisis temporal - paquetes por minuto (para detectar ráfagas)
                # Obtener timestamps del primer y último paquete
                first_packet = db_session.query(Packet.timestamp).order_by(Packet.timestamp).first()
                last_packet = db_session.query(Packet.timestamp).order_by(Packet.timestamp.desc()).first()
                
                temporal_analysis = {}
                if first_packet and last_packet:
                    duration_seconds = last_packet[0] - first_packet[0]
                    packets_per_second = total_packets / duration_seconds if duration_seconds > 0 else 0
                    temporal_analysis = {
                        "duration_seconds": round(duration_seconds, 2),
                        "packets_per_second": round(packets_per_second, 2),
                        "capture_start": datetime.fromtimestamp(first_packet[0]).strftime('%Y-%m-%d %H:%M:%S'),
                        "capture_end": datetime.fromtimestamp(last_packet[0]).strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                # Análisis de tamaños de paquetes
                avg_packet_size = db_session.query(func.avg(Packet.packet_length)).scalar()
                max_packet_size = db_session.query(func.max(Packet.packet_length)).scalar()
                min_packet_size = db_session.query(func.min(Packet.packet_length)).scalar()
                
                # Detección de patrones sospechosos
                suspicious_patterns = {}
                
                # 1. Posible SYN Flood
                if tcp_syn_packets > 1000:
                    syn_ratio = tcp_syn_packets / tcp_packets if tcp_packets > 0 else 0
                    if syn_ratio > 0.7:  # Más del 70% son SYN
                        suspicious_patterns["possible_syn_flood"] = {
                            "syn_packets": tcp_syn_packets,
                            "syn_ratio": round(syn_ratio, 3),
                            "severity": "HIGH"
                        }
                
                # 2. Escaneo de puertos
                unique_dst_ports = db_session.query(func.count(func.distinct(Packet.dst_port))).scalar()
                if unique_dst_ports > 100:
                    suspicious_patterns["possible_port_scan"] = {
                        "unique_ports_targeted": unique_dst_ports,
                        "severity": "MEDIUM"
                    }
                
                # 3. DDoS por volumen
                if temporal_analysis.get("packets_per_second", 0) > 5000:
                    suspicious_patterns["possible_ddos"] = {
                        "packets_per_second": temporal_analysis["packets_per_second"],
                        "total_volume": total_packets,
                        "severity": "HIGH"
                    }
                  # 4. Análisis de RST storms
                if tcp_rst_packets > tcp_packets * 0.3:  # Más del 30% son RST
                    suspicious_patterns["rst_storm"] = {
                        "rst_packets": tcp_rst_packets,
                        "rst_ratio": round(tcp_rst_packets / tcp_packets, 3),
                        "severity": "MEDIUM"
                    }
                
                # ======= ANÁLISIS AVANZADO DE ANOMALÍAS =======
                
                # Análisis de TTL inusuales
                ttl_analysis = db_session.query(Packet.ip_ttl, func.count(Packet.id).label('count')).filter(
                    Packet.ip_ttl.isnot(None)
                ).group_by(Packet.ip_ttl).all()
                
                suspicious_ttl = []
                for ttl, count in ttl_analysis:
                    if ttl and ttl < 10:  # TTL muy bajo = posible traceroute/escaneo
                        suspicious_ttl.append({"ttl": ttl, "count": count, "risk": "high", "description": "Possible traceroute/scanning"})
                    elif ttl and ttl > 250:  # TTL muy alto = posible manipulación
                        suspicious_ttl.append({"ttl": ttl, "count": count, "risk": "medium", "description": "Unusually high TTL"})

                # Detección avanzada de escaneo de puertos por IP origen
                port_scan_detection = db_session.query(
                    Packet.src_ip,
                    func.count(func.distinct(Packet.dst_port)).label('unique_ports'),
                    func.count(Packet.id).label('total_packets')
                ).filter(
                    Packet.dst_port.isnot(None),
                    Packet.src_ip.isnot(None)
                ).group_by(Packet.src_ip).having(
                    func.count(func.distinct(Packet.dst_port)) > 50  # Más de 50 puertos únicos
                ).all()
                
                port_scanners = []
                for src_ip, unique_ports, packets in port_scan_detection:
                    intensity = "critical" if unique_ports > 1000 else "high" if unique_ports > 200 else "medium"
                    port_scanners.append({
                        "ip": src_ip,
                        "unique_ports_scanned": unique_ports,
                        "total_packets": packets,
                        "scan_intensity": intensity,
                        "attack_type": "Port Scan"
                    })

                # Análisis de fragmentación IP sospechosa
                fragmented_packets = db_session.query(func.count(Packet.id)).filter(
                    or_(Packet.ip_flag_mf == True, Packet.ip_fragment_offset > 0)
                ).scalar() or 0
                
                fragmentation_percentage = round((fragmented_packets / total_packets * 100), 2) if total_packets > 0 else 0

                # Paquetes con tamaños anómalos
                tiny_packets = db_session.query(func.count(Packet.id)).filter(
                    Packet.packet_length < 60  # Menores a 60 bytes
                ).scalar() or 0
                
                jumbo_packets = db_session.query(func.count(Packet.id)).filter(
                    Packet.packet_length > 1500  # Mayores a MTU estándar
                ).scalar() or 0                # Análisis de flags TCP sospechosos adicionales
                
                # Christmas tree packets (múltiples flags activos simultáneamente)
                christmas_tree = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_syn == True,
                    Packet.tcp_flag_fin == True,
                    Packet.tcp_flag_rst == True,
                    Packet.tcp_flag_psh == True,
                    Packet.tcp_flag_urg == True
                ).scalar() or 0

                # NULL scan (sin flags)
                null_scan = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_syn == False,
                    Packet.tcp_flag_fin == False,
                    Packet.tcp_flag_rst == False,
                    Packet.tcp_flag_psh == False,
                    Packet.tcp_flag_urg == False,
                    Packet.tcp_flag_ack == False
                ).scalar() or 0

                # FIN scan
                fin_scan = db_session.query(func.count(Packet.id)).filter(
                    Packet.transport_protocol == 'TCP',
                    Packet.tcp_flag_fin == True,
                    Packet.tcp_flag_syn == False,
                    Packet.tcp_flag_ack == False
                ).scalar() or 0

                # Análisis de distribución temporal para detectar ráfagas
                # Obtener todos los timestamps para análisis temporal detallado
                all_timestamps = db_session.query(Packet.timestamp).order_by(Packet.timestamp).all()
                
                temporal_anomalies = {}
                if len(all_timestamps) > 1:
                    timestamps = [t[0] for t in all_timestamps]
                    first_time, last_time = timestamps[0], timestamps[-1]
                    duration = last_time - first_time
                    
                    # Dividir en intervalos de 10 segundos para detectar ráfagas
                    interval_size = 10  # segundos
                    intervals = {}
                    
                    for ts in timestamps:
                        interval_key = int((ts - first_time) / interval_size)
                        intervals[interval_key] = intervals.get(interval_key, 0) + 1
                    
                    if intervals:
                        avg_per_interval = sum(intervals.values()) / len(intervals)
                        max_per_interval = max(intervals.values())
                        
                        if max_per_interval > avg_per_interval * 20:  # Pico 20x mayor que promedio
                            temporal_anomalies["traffic_burst"] = {
                                "max_packets_per_10s": max_per_interval,
                                "average_packets_per_10s": round(avg_per_interval, 2),
                                "burst_ratio": round(max_per_interval / avg_per_interval, 2),
                                "severity": "HIGH"
                            }

                # Análisis de comunicaciones asimétricas (posible spoofing)
                asymmetric_comms = db_session.query(
                    Packet.src_ip,
                    Packet.dst_ip,
                    func.count(Packet.id).label('outbound'),
                ).group_by(Packet.src_ip, Packet.dst_ip).subquery()

                # Buscar pares con comunicación muy asimétrica
                comm_pairs = db_session.query(asymmetric_comms).all()
                asymmetric_patterns = []
                
                for src, dst, out_count in comm_pairs:
                    # Buscar tráfico de vuelta
                    in_count = db_session.query(func.count(Packet.id)).filter(
                        Packet.src_ip == dst,
                        Packet.dst_ip == src
                    ).scalar() or 0
                    
                    if out_count > 100 and (in_count == 0 or out_count / in_count > 50):
                        asymmetric_patterns.append({
                            "src_ip": src,
                            "dst_ip": dst,
                            "outbound_packets": out_count,
                            "inbound_packets": in_count,
                            "asymmetry_ratio": "∞" if in_count == 0 else round(out_count / in_count, 2),
                            "possible_attack": "IP Spoofing or DDoS"
                        })

                # Compilar análisis completo de anomalías
                advanced_anomaly_analysis = {
                    "suspicious_ttl_values": suspicious_ttl,
                    "port_scanning_detected": {
                        "scanner_count": len(port_scanners),
                        "scanners": port_scanners
                    },
                    "fragmentation_analysis": {
                        "fragmented_packets": fragmented_packets,
                        "fragmentation_percentage": fragmentation_percentage,
                        "potential_evasion": fragmentation_percentage > 5.0
                    },
                    "packet_size_anomalies": {
                        "tiny_packets": tiny_packets,
                        "jumbo_packets": jumbo_packets,
                        "size_distribution_suspicious": tiny_packets > total_packets * 0.1 or jumbo_packets > total_packets * 0.1
                    },
                    "advanced_tcp_attacks": {
                        "christmas_tree_packets": christmas_tree,
                        "null_scan_packets": null_scan,
                        "fin_scan_packets": fin_scan,
                        "stealth_scan_detected": christmas_tree > 0 or null_scan > 100 or fin_scan > 100
                    },
                    "temporal_anomalies": temporal_anomalies,
                    "asymmetric_communications": {
                        "suspicious_pairs": asymmetric_patterns,
                        "potential_spoofing": len(asymmetric_patterns) > 0
                    }
                }

                # Anomalías detectadas automáticamente
                anomaly_count = db_session.query(func.count(Anomaly.id)).scalar()
                anomaly_types = db_session.query(
                    Anomaly.type,
                    func.count(Anomaly.id).label('count')
                ).group_by(Anomaly.type).all()
                
                session_data = {
                    "file_name": chat_request.db_file,
                    "total_packets": total_packets,
                    "protocol_breakdown": {
                        "tcp": tcp_packets,
                        "udp": udp_packets,
                        "icmp": icmp_packets,
                        "other": total_packets - tcp_packets - udp_packets - icmp_packets
                    },
                    "tcp_analysis": {
                        "syn_packets": tcp_syn_packets,
                        "rst_packets": tcp_rst_packets,
                        "fin_packets": tcp_fin_packets,
                        "syn_ratio": round(tcp_syn_packets / tcp_packets, 3) if tcp_packets > 0 else 0
                    },
                    "top_source_ips": [{"ip": ip, "packets": count} for ip, count in top_src_ips],
                    "top_destination_ips": [{"ip": ip, "packets": count} for ip, count in top_dst_ips],
                    "top_targeted_ports": [{"port": port, "packets": count} for port, count in top_dst_ports if port],
                    "temporal_analysis": temporal_analysis,
                    "packet_size_stats": {
                        "average": round(avg_packet_size, 2) if avg_packet_size else 0,
                        "maximum": max_packet_size or 0,
                        "minimum": min_packet_size or 0
                    },                    "suspicious_patterns_detected": suspicious_patterns,
                    "advanced_anomaly_analysis": advanced_anomaly_analysis,
                    "anomalies": {
                        "total_count": anomaly_count,
                        "by_type": [{"type": anom_type, "count": count} for anom_type, count in anomaly_types]
                    }
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
