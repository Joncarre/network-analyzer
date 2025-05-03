import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()

class ClaudeAI:
    """Clase para integrar con la API de Anthropic Claude"""
    
    def __init__(self):
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
    
    def generate_system_prompt(self, session_data: Dict[str, Any] = None) -> str:
        """Genera el prompt del sistema que define el comportamiento del asistente."""
        system_prompt = """Eres un experto analista de ciberseguridad especializado en análisis de tráfico de red.
Tu tarea es ayudar a interpretar y analizar datos de tráfico de red, detectar posibles amenazas y responder preguntas sobre el tráfico capturado.

Tienes acceso a datos de paquetes de red que incluyen información de las capas 3 (Red) y 4 (Transporte) del modelo OSI.
No tienes acceso a datos de capas superiores como contenido de aplicaciones o datos de usuario.

Al responder:
- Sé claro y preciso, utilizando terminología técnica cuando sea necesario pero explicando conceptos complejos.
- Cuando identifiques posibles amenazas o comportamientos sospechosos, explica por qué son preocupantes.
- Incluye recomendaciones prácticas cuando sea apropiado.
- Si no tienes suficiente información para responder, indícalo y sugiere qué datos adicionales serían útiles.
- Responde en español y usa un lenguaje técnico pero accesible para usuarios con conocimientos básicos de redes."""

        if session_data:
            packet_count = session_data.get("packet_count", 0)
            protocols = session_data.get("protocols", {})
            anomaly_count = session_data.get("anomaly_count", 0)
            
            protocols_str = ", ".join([f"{proto}: {count}" for proto, count in protocols.items()]) if protocols else "No disponible"
            
            context = f"""
Información sobre la sesión actual de captura:
- Total de paquetes: {packet_count}
- Protocolos detectados: {protocols_str}
- Anomalías detectadas: {anomaly_count}"""
            system_prompt += context
        
        return system_prompt
    
    def query(self, user_question: str, session_data: Optional[Dict[str, Any]] = None) -> str:
        """Envía una consulta a Claude y obtiene respuesta."""
        try:
            system_prompt = self.generate_system_prompt(session_data)
            
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
            
            # Actualizar historial
            self.conversation_history.append({"role": "user", "content": user_question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            return answer
            
        except Exception as e:
            return f"Error al procesar la consulta: {str(e)}"
    
    def clear_conversation(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
