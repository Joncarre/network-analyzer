import os
import sys
import time

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capture.network_interfaces import get_interfaces, capture_packets

def test_capture():
    """Prueba la captura de paquetes"""
    print("\n---- Test: Captura de paquetes ----")
    
    # Obtener interfaces disponibles
    interfaces = get_interfaces()
    if not interfaces:
        print("⚠️ No hay interfaces disponibles para capturar")
        return False
    
    # Mostrar interfaces disponibles para selección
    print("✅ Interfaces disponibles:")
    for i, iface in enumerate(interfaces):
        print(f"{i+1}. {iface['name']} (ID: {iface['id']})")
    
    # Seleccionar interfaz
    try:
        selection = int(input("\nSelecciona una interfaz (número): ")) - 1
        if selection < 0 or selection >= len(interfaces):
            print("⚠️ Selección inválida")
            return False
            
        selected_iface = interfaces[selection]['id']
    except ValueError:
        print("⚠️ Entrada inválida")
        return False
    
    # Configurar duración de la captura
    try:
        duration = int(input("Duración de la captura en segundos (5-30): "))
        if duration < 5 or duration > 30:
            duration = 10
            print(f"⚠️ Valor fuera de rango, usando duración: {duration}s")
    except ValueError:
        duration = 10
        print(f"⚠️ Entrada inválida, usando duración: {duration}s")
    
    print(f"\nIniciando captura en interfaz {selected_iface} por {duration} segundos...")
    
    # Iniciar captura
    try:
        start_time = time.time()
        output_file = capture_packets(
            interface_id=selected_iface,
            duration=duration
        )
        elapsed_time = time.time() - start_time
        
        if output_file and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Captura completada en {elapsed_time:.2f}s")
            print(f"   - Archivo: {output_file}")
            print(f"   - Tamaño: {file_size / 1024:.2f} KB")
            return True
        else:
            print("❌ Error en la captura: no se generó el archivo")
            return False
            
    except Exception as e:
        print(f"❌ Error en la captura: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== PRUEBAS DE CAPTURA DE TRÁFICO ===")
    
    # Ejecutar pruebas
    capture_ok = test_capture()
    
    print("\nResumen de pruebas:")
    print(f"- Captura de paquetes: {'✅ OK' if capture_ok else '❌ FALLIDO'}")
