import os
import requests
import json
import time
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()

# Importar métricas de forma segura (opcional)
try:
    from .claude_metrics import ClaudeMetrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

class ClaudeAI:
    """Clase para integrar con la API de Anthropic Claude"""
    
    def __init__(self, enable_metrics: bool = True):
        """Inicializa el cliente de Anthropic Claude"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("No se encontró la clave API de Anthropic Claude. Configura ANTHROPIC_API_KEY en las variables de entorno.")
            
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        self.model = "claude-3-opus-20240229"
        self.max_tokens = 4000
        self.conversation_history = []
        
        # Inicializar métricas de forma segura
        self.metrics = None
        if enable_metrics and METRICS_AVAILABLE:
            try:
                self.metrics = ClaudeMetrics()
            except Exception as e:
                print(f"Warning: No se pudieron inicializar las métricas: {e}")
                self.metrics = None
    
    def generate_system_prompt(self, session_data: Dict[str, Any] = None, user_preference: str = None) -> str:
        """Genera el prompt del sistema que define el comportamiento del asistente, adaptado a la preferencia del usuario."""
        system_prompt = """Eres un experto analista de ciberseguridad especializado en análisis de tráfico de red.
Tu tarea es ayudar a interpretar y analizar datos de tráfico de red, detectar posibles amenazas y responder preguntas sobre el tráfico capturado.

Tienes acceso a datos de paquetes de red que incluyen información de las capas 3 (Red) y 4 (Transporte) del modelo OSI.
No tienes acceso a datos de capas superiores como contenido de aplicaciones o datos de usuario.

Al responder:
- Sé claro y preciso, utilizando terminología técnica cuando sea necesario pero explicando conceptos complejos.
- Cuando identifiques posibles amenazas o comportamientos sospechosos, explica por qué son preocupantes.
- Incluye recomendaciones prácticas cuando sea apropiado.
- Si no tienes suficiente información para responder, indícalo y sugiere qué datos adicionales serían útiles.
- Si la pregunta es ambigua o falta contexto, indícalo explícitamente y pide aclaraciones.
- Responde en español y usa un lenguaje técnico pero accesible para usuarios con conocimientos básicos de redes."""

        # Diferenciación explícita de modos con ejemplos
        if user_preference:
            if user_preference == "corto":
                system_prompt += ("""\n\nMODO RESPUESTA CORTA: Responde en un máximo de 2-3 frases, solo lo esencial. No añadas explicaciones, contexto, ejemplos ni advertencias adicionales. No incluyas introducciones ni conclusiones. Responde de forma directa y concisa.\nEjemplo:\nPregunta: ¿Cuántos paquetes UDP hay en la sesión?\nRespuesta: En la sesión actual se han detectado 781 paquetes UDP.""")
            elif user_preference == "detallado":
                system_prompt += ("""\n\nMODO RESPUESTA DETALLADA: Responde de forma extensa y muy detallada. Explica cada aspecto relevante, proporciona contexto, implicaciones de seguridad, posibles causas, advertencias, ejemplos prácticos, recomendaciones técnicas y cualquier información adicional útil para un análisis profundo. Si la pregunta lo permite, estructura la respuesta en secciones o listas. Añade explicaciones de términos técnicos y posibles escenarios relacionados. Si hay riesgos, explícalos. Si hay buenas prácticas, inclúyelas. Si puedes, aporta referencias o analogías técnicas.\nEjemplo:\nPregunta: ¿Cuántos paquetes UDP hay en la sesión?\nRespuesta: En la sesión actual de captura se han detectado 781 paquetes UDP. El protocolo UDP (User Datagram Protocol) es ampliamente utilizado para aplicaciones que requieren baja latencia, como streaming o DNS. Un volumen elevado de paquetes UDP puede indicar tráfico legítimo de servicios multimedia, pero también puede ser síntoma de ataques como UDP flood. Recomendación: revisar los puertos de destino y origen para identificar patrones inusuales. Si se detectan picos anómalos, podría ser conveniente aplicar filtros o alertas específicas.""")
            elif user_preference == "normal":
                system_prompt += ("""\n\nMODO RESPUESTA NORMAL: Responde en un máximo de 7-9 frases. Responde de forma equilibrada, con una explicación clara y suficiente para entender la respuesta, pero sin entrar en detalles exhaustivos. Incluye contexto relevante y una breve justificación si es útil, pero evita respuestas demasiado largas.\nEjemplo:\nPregunta: ¿Cuántos paquetes UDP hay en la sesión?\nRespuesta: Se han detectado 781 paquetes UDP en la sesión. UDP es común en servicios como DNS o streaming, pero conviene revisar si el volumen es esperado.""")
        
        if session_data:
            # ============= INFORMACIÓN BÁSICA DE LA SESIÓN =============
            packet_count = session_data.get("packet_count", 0)
            protocols = session_data.get("protocols", {})
            file_name = session_data.get("file_name", "N/A")
            
            # ============= ANÁLISIS DE PROTOCOLOS =============
            protocol_breakdown = session_data.get("protocol_breakdown", {})
            tcp_analysis = session_data.get("tcp_detailed_analysis", {}) or session_data.get("tcp_analysis", {})
            
            # ============= INFORMACIÓN TEMPORAL =============
            temporal_analysis = session_data.get("temporal_analysis", {})
            
            # ============= TOP IPs Y PUERTOS =============
            top_source_ips = session_data.get("top_source_ips", [])
            top_destination_ips = session_data.get("top_destination_ips", [])
            top_ports = session_data.get("most_targeted_ports", []) or session_data.get("top_targeted_ports", [])
            
            # ============= ANÁLISIS DE ANOMALÍAS Y ATAQUES =============
            suspicious_patterns = session_data.get("suspicious_patterns_detected", {})
            advanced_anomalies = session_data.get("advanced_anomaly_analysis", {})
            anomalies = session_data.get("anomalies", {})
            
            # ============= ESTADÍSTICAS DE PAQUETES =============
            packet_sizes = session_data.get("packet_sizes", {}) or session_data.get("packet_size_stats", {})
            
            # Obtener el total de paquetes correcto
            total_packets = session_data.get("total_packets", packet_count)
            
            # Construir contexto detallado
            context = f"""
═══════════════════════════════════════════════════════════════════════════════
                        INFORMACIÓN DETALLADA DE LA SESIÓN DE CAPTURA
═══════════════════════════════════════════════════════════════════════════════

📁 ARCHIVO: {file_name}
📊 TOTAL DE PAQUETES: {total_packets:,}

▓▓▓ DISTRIBUCIÓN DE PROTOCOLOS ▓▓▓
"""
            
            # Información de protocolos
            if protocol_breakdown:
                tcp_count = protocol_breakdown.get('tcp', 0)
                udp_count = protocol_breakdown.get('udp', 0)
                icmp_count = protocol_breakdown.get('icmp', 0)
                other_count = protocol_breakdown.get('other', 0)
                
                context += f"""
┌─────────────────────────────────────────────────────────────┐
│ TCP:   {tcp_count:>10,} paquetes ({tcp_count/total_packets*100:.2f}%)  │
│ UDP:   {udp_count:>10,} paquetes ({udp_count/total_packets*100:.2f}%)  │
│ ICMP:  {icmp_count:>10,} paquetes ({icmp_count/total_packets*100:.2f}%)  │
│ OTROS: {other_count:>10,} paquetes ({other_count/total_packets*100:.2f}%)  │
└─────────────────────────────────────────────────────────────┘
"""
            elif protocols:
                for proto, count in protocols.items():
                    percentage = (count / total_packets * 100) if total_packets > 0 else 0
                    context += f"  • {proto}: {count:,} paquetes ({percentage:.2f}%)\n"
            
            # Análisis TCP detallado
            if tcp_analysis:
                context += f"""
▓▓▓ ANÁLISIS DETALLADO TCP ▓▓▓
┌─────────────────────────────────────────────────────────────┐
│ SYN Packets: {tcp_analysis.get('syn_packets', 0):>8,}                          │
│ RST Packets: {tcp_analysis.get('rst_packets', 0):>8,}                          │
│ FIN Packets: {tcp_analysis.get('fin_packets', 0):>8,}                          │
│ SYN Ratio:   {tcp_analysis.get('syn_ratio', 0):>8.3f}                          │
└─────────────────────────────────────────────────────────────┘
"""
            
            # Información temporal
            if temporal_analysis:
                context += f"""
▓▓▓ ANÁLISIS TEMPORAL ▓▓▓
┌─────────────────────────────────────────────────────────────┐
│ Duración:        {temporal_analysis.get('duration_seconds', 0):>8.2f} segundos         │
│ Paq./segundo:    {temporal_analysis.get('packets_per_second', 0):>8.2f}                    │
│ Inicio:          {temporal_analysis.get('start_time', 'N/A'):<19}       │
│ Fin:             {temporal_analysis.get('end_time', 'N/A'):<19}         │
└─────────────────────────────────────────────────────────────┘
"""
                
                # Detectar posibles ataques basados en velocidad
                pps = temporal_analysis.get('packets_per_second', 0)
                if pps > 10000:
                    context += f"\n🚨 ALERTA: Tráfico extremadamente alto ({pps:.0f} pps) - POSIBLE ATAQUE DDoS\n"
                elif pps > 5000:
                    context += f"\n⚠️  ADVERTENCIA: Tráfico muy alto ({pps:.0f} pps) - Monitorear por DDoS\n"
            
            # Top IPs origen (posibles atacantes)
            if top_source_ips:
                context += f"""
▓▓▓ TOP IPs ORIGEN (POSIBLES ATACANTES) ▓▓▓
┌─────────────────────────────────────────────────────────────┐
"""
                for i, ip_data in enumerate(top_source_ips[:10], 1):
                    ip = ip_data.get('ip', 'N/A')
                    packets = ip_data.get('packets', 0)
                    percentage = (packets / total_packets * 100) if total_packets > 0 else 0
                    context += f"│ {i:2}. {ip:<15} {packets:>10,} paq. ({percentage:>5.2f}%) │\n"
                context += "└─────────────────────────────────────────────────────────────┘\n"
            
            # Top IPs destino (posibles víctimas)
            if top_destination_ips:
                context += f"""
▓▓▓ TOP IPs DESTINO (POSIBLES VÍCTIMAS) ▓▓▓
┌─────────────────────────────────────────────────────────────┐
"""
                for i, ip_data in enumerate(top_destination_ips[:10], 1):
                    ip = ip_data.get('ip', 'N/A')
                    packets = ip_data.get('packets', 0)
                    percentage = (packets / total_packets * 100) if total_packets > 0 else 0
                    context += f"│ {i:2}. {ip:<15} {packets:>10,} paq. ({percentage:>5.2f}%) │\n"
                context += "└─────────────────────────────────────────────────────────────┘\n"
            
            # Puertos más atacados
            if top_ports:
                context += f"""
▓▓▓ PUERTOS MÁS ATACADOS ▓▓▓
┌─────────────────────────────────────────────────────────────┐
"""
                for i, port_data in enumerate(top_ports[:15], 1):
                    port = port_data.get('port', 'N/A')
                    packets = port_data.get('packets', 0)
                    percentage = (packets / total_packets * 100) if total_packets > 0 else 0
                    
                    # Identificar servicios conocidos
                    service = "Unknown"
                    if port == 80: service = "HTTP"
                    elif port == 443: service = "HTTPS"
                    elif port == 53: service = "DNS"
                    elif port == 22: service = "SSH"
                    elif port == 21: service = "FTP"
                    elif port == 25: service = "SMTP"
                    elif port == 110: service = "POP3"
                    elif port == 143: service = "IMAP"
                    elif port == 993: service = "IMAPS"
                    elif port == 995: service = "POP3S"
                    
                    context += f"│ {i:2}. Puerto {port:<6} ({service:<8}) {packets:>8,} paq. ({percentage:>5.2f}%) │\n"
                context += "└─────────────────────────────────────────────────────────────┘\n"
            
            # Estadísticas de tamaños de paquetes
            if packet_sizes:
                context += f"""
▓▓▓ ESTADÍSTICAS DE TAMAÑOS DE PAQUETES ▓▓▓
┌─────────────────────────────────────────────────────────────┐
│ Promedio: {packet_sizes.get('average', 0):>8.2f} bytes                       │
│ Máximo:   {packet_sizes.get('maximum', 0):>8,} bytes                       │
│ Mínimo:   {packet_sizes.get('minimum', 0):>8,} bytes                       │
└─────────────────────────────────────────────────────────────┘
"""
            
            # ¡¡¡ PATRONES SOSPECHOSOS DETECTADOS !!!
            if suspicious_patterns:
                context += f"""
🚨🚨🚨 PATRONES SOSPECHOSOS DETECTADOS 🚨🚨🚨
"""
                for pattern_type, details in suspicious_patterns.items():
                    severity = details.get('severity', 'UNKNOWN')
                    if pattern_type == "possible_syn_flood":
                        context += f"""
┌─ SYN FLOOD DETECTADO ({severity}) ──────────────────────────┐
│ SYN Packets: {details.get('syn_packets', 0):,}                               │
│ SYN Ratio:   {details.get('syn_ratio', 0):.3f}                                │
│ ⚠️  ESTO ES UN ATAQUE DE DENEGACIÓN DE SERVICIO (DDoS)     │
└─────────────────────────────────────────────────────────────┘
"""
                    elif pattern_type == "possible_port_scan":
                        context += f"""
┌─ ESCANEO DE PUERTOS DETECTADO ({severity}) ─────────────────┐
│ Puertos únicos escaneados: {details.get('unique_ports_targeted', 0):,}        │
│ ⚠️  ACTIVIDAD DE RECONOCIMIENTO/ESCANEO DETECTADA          │
└─────────────────────────────────────────────────────────────┘
"""
                    elif pattern_type == "possible_ddos":
                        context += f"""
┌─ ATAQUE DDoS DETECTADO ({severity}) ────────────────────────┐
│ Paquetes/segundo: {details.get('packets_per_second', 0):,.0f}               │
│ Volumen total:    {details.get('total_volume', 0):,} paquetes     │
│ 🚨 ATAQUE DE DENEGACIÓN DE SERVICIO DISTRIBUIDO (DDoS)     │
└─────────────────────────────────────────────────────────────┘
"""
                    elif pattern_type == "rst_storm":
                        context += f"""
┌─ RST STORM DETECTADO ({severity}) ──────────────────────────┐
│ RST Packets: {details.get('rst_packets', 0):,}                        │
│ RST Ratio:   {details.get('rst_ratio', 0):.3f}                         │
│ ⚠️  POSIBLE ATAQUE DE RESETEO DE CONEXIONES                │
└─────────────────────────────────────────────────────────────┘
"""
            
            # ANÁLISIS AVANZADO DE ANOMALÍAS
            if advanced_anomalies:
                context += f"""
🔍🔍🔍 ANÁLISIS AVANZADO DE ANOMALÍAS 🔍🔍🔍
"""
                
                # TTL sospechosos
                suspicious_ttl = advanced_anomalies.get("suspicious_ttl_values", [])
                if suspicious_ttl:
                    context += "\n▓ TTL SOSPECHOSOS DETECTADOS ▓\n"
                    for ttl_info in suspicious_ttl:
                        context += f"  • TTL {ttl_info['ttl']}: {ttl_info['count']} paquetes - {ttl_info['description']} (Riesgo: {ttl_info['risk']})\n"
                
                # Escaneo de puertos
                port_scan = advanced_anomalies.get("port_scanning_detected", {})
                if port_scan.get("scanner_count", 0) > 0:
                    context += f"\n▓ ESCÁNERES DE PUERTOS DETECTADOS ▓\n"
                    context += f"Total de escáneres: {port_scan['scanner_count']}\n"
                    for scanner in port_scan.get("scanners", [])[:5]:  # Top 5
                        context += f"  • IP {scanner['ip']}: {scanner['unique_ports_scanned']} puertos escaneados ({scanner['scan_intensity']}) - {scanner['attack_type']}\n"
                
                # Fragmentación
                frag_analysis = advanced_anomalies.get("fragmentation_analysis", {})
                if frag_analysis.get("fragmented_packets", 0) > 0:
                    context += f"\n▓ ANÁLISIS DE FRAGMENTACIÓN ▓\n"
                    context += f"Paquetes fragmentados: {frag_analysis['fragmented_packets']:,} ({frag_analysis['fragmentation_percentage']:.2f}%)\n"
                    if frag_analysis.get("potential_evasion"):
                        context += "⚠️  POSIBLE TÉCNICA DE EVASIÓN POR FRAGMENTACIÓN\n"
                
                # Tamaños anómalos
                size_anomalies = advanced_anomalies.get("packet_size_anomalies", {})
                if size_anomalies.get("tiny_packets", 0) > 0 or size_anomalies.get("jumbo_packets", 0) > 0:
                    context += f"\n▓ TAMAÑOS DE PAQUETE ANÓMALOS ▓\n"
                    context += f"Paquetes tiny (<60B): {size_anomalies.get('tiny_packets', 0):,}\n"
                    context += f"Paquetes jumbo (>1500B): {size_anomalies.get('jumbo_packets', 0):,}\n"
                    if size_anomalies.get("size_distribution_suspicious"):
                        context += "⚠️  DISTRIBUCIÓN DE TAMAÑOS SOSPECHOSA\n"
                
                # Ataques TCP avanzados
                tcp_attacks = advanced_anomalies.get("advanced_tcp_attacks", {})
                if tcp_attacks.get("stealth_scan_detected"):
                    context += f"\n▓ ESCANEOS SIGILOSOS TCP DETECTADOS ▓\n"
                    if tcp_attacks.get("christmas_tree_packets", 0) > 0:
                        context += f"Christmas Tree packets: {tcp_attacks['christmas_tree_packets']:,}\n"
                    if tcp_attacks.get("null_scan_packets", 0) > 0:
                        context += f"NULL scan packets: {tcp_attacks['null_scan_packets']:,}\n"
                    if tcp_attacks.get("fin_scan_packets", 0) > 0:
                        context += f"FIN scan packets: {tcp_attacks['fin_scan_packets']:,}\n"
                    context += "🚨 TÉCNICAS DE ESCANEO SIGILOSO DETECTADAS\n"
                
                # Anomalías temporales
                temporal_anom = advanced_anomalies.get("temporal_anomalies", {})
                if temporal_anom.get("traffic_burst"):
                    burst = temporal_anom["traffic_burst"]
                    context += f"\n▓ RÁFAGAS DE TRÁFICO DETECTADAS ▓\n"
                    context += f"Máximo en 10s: {burst['max_packets_per_10s']:,} paquetes\n"
                    context += f"Promedio: {burst['average_packets_per_10s']:,} paquetes\n"
                    context += f"Ratio de ráfaga: {burst['burst_ratio']:.1f}x\n"
                    context += "🚨 POSIBLE ATAQUE DE RÁFAGA/DDoS\n"
                
                # Comunicaciones asimétricas
                asymm = advanced_anomalies.get("asymmetric_communications", {})
                if asymm.get("potential_spoofing"):
                    context += f"\n▓ COMUNICACIONES ASIMÉTRICAS DETECTADAS ▓\n"
                    for pair in asymm.get("suspicious_pairs", [])[:3]:  # Top 3
                        context += f"  • {pair['src_ip']} → {pair['dst_ip']}: {pair['outbound_packets']:,} out, {pair['inbound_packets']} in (ratio: {pair['asymmetry_ratio']})\n"
                    context += "⚠️  POSIBLE IP SPOOFING O ATAQUE DDoS\n"
            
            # Anomalías registradas en BD
            if anomalies.get("total_count", 0) > 0:
                context += f"""
📋 ANOMALÍAS REGISTRADAS EN BASE DE DATOS
Total de anomalías: {anomalies['total_count']:,}
"""
                for anom in anomalies.get("by_type", []):
                    context += f"  • {anom['type']}: {anom['count']} casos\n"
            
            context += f"""
═══════════════════════════════════════════════════════════════════════════════

INSTRUCCIONES PARA EL ANÁLISIS:
Basándote en TODA esta información detallada, debes:
1. Identificar patrones de ataque y amenazas de seguridad
2. Evaluar la severidad de las anomalías detectadas
3. Proporcionar recomendaciones de seguridad específicas
4. Explicar qué tipos de ataques están ocurriendo
5. Sugerir medidas de mitigación

IMPORTANTE: Tienes acceso a información muy detallada sobre:
- Distribución de protocolos y análisis TCP
- IPs más activas (atacantes/víctimas)
- Puertos atacados y servicios comprometidos
- Patrones temporales y ráfagas de tráfico
- Técnicas de escaneo y evasión
- Anomalías de red y comportamientos sospechosos

Usa TODA esta información para dar respuestas precisas y técnicamente detalladas.
"""            
            system_prompt += context
        
        return system_prompt
    
    def query(self, user_question: str, session_data: Optional[Dict[str, Any]] = None, user_preference: str = None) -> str:
        """Envía una consulta a Claude y obtiene respuesta, adaptando el prompt a la preferencia del usuario."""
        start_time = time.time()
        
        try:
            system_prompt = self.generate_system_prompt(session_data, user_preference)
            
            # Mantener historial limitado
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # Construir mensajes sin el system prompt
            messages_for_api = []
            messages_for_api.extend(self.conversation_history)
            messages_for_api.append({"role": "user", "content": user_question})
            
            # Preparar payload para la llamada a la API con system como parámetro top-level
            payload = {
                "model": self.model,
                "system": system_prompt, # <-- System prompt como parámetro separado
                "messages": messages_for_api, # <-- Mensajes sin el system prompt
                "max_tokens": self.max_tokens
            }
            
            # Realizar llamada directa a la API HTTP
            response = requests.post(
                f"{self.base_url}/messages", 
                headers=self.headers, 
                json=payload
            )
            
            # Calcular tiempo de respuesta
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                return f"Error en la llamada a la API de Claude: {response.status_code} - {response.text}"
            
            # Parsear respuesta
            result = response.json()
            
            # Manejar correctamente la estructura de la respuesta de Claude
            # La respuesta tiene un campo 'content' que es una lista de objetos
            content = result.get("content", [])
            if not content or not isinstance(content, list):
                return "Sin respuesta o formato de respuesta inesperado"
                
            # Extraer el texto del primer elemento de contenido
            answer = ""
            for item in content:
                if item.get("type") == "text":
                    answer += item.get("text", "")
            
            if not answer:
                return "No se pudo extraer texto de la respuesta"
            
            # Capturar métricas de la API si están disponibles
            if self.metrics:
                try:
                    usage = result.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    
                    query_metrics = self.metrics.record_query(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        response_time_ms=response_time_ms,
                        model=self.model,
                        user_question=user_question,
                        response=answer
                    )
                    
                    # Mostrar métricas si están disponibles
                    if query_metrics:
                        self.metrics.print_query_summary(query_metrics)
                        
                except Exception as e:
                    print(f"Warning: Error al capturar métricas: {e}")
            
            # Actualizar historial
            self.conversation_history.append({"role": "user", "content": user_question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            return answer
            
        except Exception as e:
            return f"Error al procesar la consulta: {str(e)}"
    
    def clear_conversation(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
    
    def get_session_metrics(self):
        """Obtiene las métricas de la sesión actual"""
        if self.metrics:
            return self.metrics.get_session_summary()
        return None
    
    def print_session_summary(self):
        """Imprime un resumen de las métricas de la sesión"""
        if self.metrics:
            self.metrics.print_session_summary()
        else:
            print("Métricas no disponibles")
