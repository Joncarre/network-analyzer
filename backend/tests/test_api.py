import os
import sys
import requests
import json
from urllib.parse import urljoin

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# URL base de la API
BASE_URL = "http://localhost:8000"

def test_api_root():
    """Prueba el endpoint raíz de la API"""
    print("\n--- Test: Endpoint raíz ---")
    
    try:
        response = requests.get(urljoin(BASE_URL, "/"))
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Respuesta:", json.dumps(response.json(), indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        print("⚠️ Asegúrate de que el servidor backend esté ejecutándose")
        return False

def test_interfaces_endpoint():
    """Prueba el endpoint de listar interfaces"""
    print("\n--- Test: Endpoint de interfaces ---")
    
    try:
        response = requests.get(urljoin(BASE_URL, "/api/capture/interfaces"))
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            interfaces = response.json()
            print(f"Se encontraron {len(interfaces)} interfaces:")
            for iface in interfaces[:3]:  # Mostrar solo las primeras 3
                print(f"  - {iface['name']}")
            
            if len(interfaces) > 3:
                print(f"  - ... y {len(interfaces) - 3} más")
                
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_sessions_endpoint():
    """Prueba el endpoint de listar sesiones de captura"""
    print("\n--- Test: Endpoint de sesiones ---")
    
    try:
        response = requests.get(urljoin(BASE_URL, "/api/database/sessions"))
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"Se encontraron {len(sessions)} sesiones:")
            for session in sessions[:3]:  # Mostrar solo las primeras 3
                print(f"  - ID: {session['id']}, Archivo: {session['file_name']}, Fecha: {session['capture_date']}")
            
            if len(sessions) > 3:
                print(f"  - ... y {len(sessions) - 3} más")
            
            # Si hay sesiones, guardar la primera para pruebas adicionales
            if sessions:
                first_session_id = sessions[0]['id']
                print(f"\nUsando sesión ID {first_session_id} para pruebas adicionales")
                test_session_details(first_session_id)
                test_analytics_endpoint(first_session_id)
                test_ai_endpoint(first_session_id)
                
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_session_details(session_id):
    """Prueba el endpoint de detalles de sesión"""
    print(f"\n--- Test: Detalles de sesión {session_id} ---")
    
    try:
        response = requests.get(urljoin(BASE_URL, f"/api/database/sessions/{session_id}"))
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            details = response.json()
            print("Resumen de la sesión:")
            print(f"  - Archivo: {details['file_name']}")
            print(f"  - Paquetes: {details['packet_count']}")
            print(f"  - Protocolos: {', '.join([f'{k}:{v}' for k, v in details.get('protocols', {}).items()])}")
            print(f"  - Anomalías: {details.get('anomaly_count', 0)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_analytics_endpoint(session_id):
    """Prueba el endpoint de análisis"""
    print(f"\n--- Test: Análisis de sesión {session_id} ---")
    
    try:
        response = requests.get(urljoin(BASE_URL, f"/api/database/analytics/{session_id}"))
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            analytics = response.json()
            print("Análisis de la sesión:")
            print(f"  - Duración: {analytics.get('duration', 0):.2f} segundos")
            print(f"  - Protocolos: {len(analytics.get('protocols', []))}")
            print(f"  - Top puertos TCP: {len(analytics.get('tcp_ports', []))}")
            print(f"  - Top puertos UDP: {len(analytics.get('udp_ports', []))}")
            print(f"  - Anomalías por tipo: {len(analytics.get('anomalies', {}).get('by_type', []))}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def test_ai_endpoint(session_id=None):
    """Prueba el endpoint de IA"""
    print(f"\n--- Test: Consulta a IA {'con' if session_id else 'sin'} contexto de sesión ---")
    
    try:
        data = {
            "message": "¿Puedes explicarme qué es un paquete TCP?",
            "session_id": session_id
        }
        
        response = requests.post(urljoin(BASE_URL, "/api/ai/chat"), json=data)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Respuesta de la IA:")
            print(f"  {result['response'][:150]}...")  # Mostrar solo los primeros 150 caracteres
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== PRUEBAS DE LA API ===")
    print(f"Servidor: {BASE_URL}")
    
    # Ejecutar pruebas
    root_ok = test_api_root()
    
    if root_ok:
        interfaces_ok = test_interfaces_endpoint()
        sessions_ok = test_sessions_endpoint()
    
    print("\nResumen de pruebas API:")
    print(f"- Endpoint raíz: {'✅ OK' if root_ok else '❌ FALLIDO'}")
    print(f"- Endpoints de interfaces: {'✅ OK' if 'interfaces_ok' in locals() and interfaces_ok else '❌ FALLIDO'}")
    print(f"- Endpoints de sesiones: {'✅ OK' if 'sessions_ok' in locals() and sessions_ok else '❌ FALLIDO'}")
