import os
import sys
import time
from datetime import datetime  # Import datetime

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.pcap_processor import PCAPProcessor

def test_process_pcap_file():
    """Prueba el procesamiento de un archivo PCAP"""
    print("\n--- Test: Procesar archivo PCAP ---")
    
    # Comprobar archivos PCAP disponibles
    pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
    if not os.path.exists(pcap_dir):
        print(f"⚠️ El directorio {pcap_dir} no existe")
        return False
    
    pcap_files = [f for f in os.listdir(pcap_dir) if f.endswith(('.pcap', '.pcapng'))]
    if not pcap_files:
        print(f"⚠️ No se encontraron archivos PCAP en {pcap_dir}")
        return False
    
    # Mostrar archivos disponibles para selección
    print("Archivos PCAP disponibles:")
    for i, file in enumerate(pcap_files):
        file_path = os.path.join(pcap_dir, file)
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"{i+1}. {file} ({file_size:.2f} KB)")
    
    # Seleccionar archivo
    try:
        selection = int(input("\nSelecciona un archivo (número): ")) - 1
        if selection < 0 or selection >= len(pcap_files):
            print("⚠️ Selección inválida")
            return False
            
        selected_file = os.path.join(pcap_dir, pcap_files[selection])
    except ValueError:
        print("⚠️ Entrada inválida")
        return False
    
    print(f"\nProcesando archivo: {selected_file}")
    
    # Inicializar el procesador
    try:
        # --- Remove custom DB path generation ---
        # db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'db_files'))
        # os.makedirs(db_dir, exist_ok=True)
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # db_filename = f"database_{timestamp}.db"
        # db_path = os.path.join(db_dir, db_filename)
        # print(f"   - Usando base de datos de prueba: {db_path}")
        # -----------------------------------------

        # Inicializar procesador - it will find/create the latest DB itself
        # No need to call init_db() here anymore
        processor = PCAPProcessor() 
        
        # Medir tiempo de procesamiento
        start_time = time.time()
        session_id = processor.process_pcap_file(selected_file)
        elapsed_time = time.time() - start_time
        
        if session_id:
            print(f"✅ Procesamiento completado en {elapsed_time:.2f}s")
            print(f"   - ID de sesión: {session_id}")
            # Use the db_path stored within the processor instance
            print(f"   - Base de datos: {processor.db_path}") 
            return True
        else:
            print("❌ Error en el procesamiento: no se devolvió ID de sesión")
            return False
            
    except Exception as e:
        print(f"❌ Error en el procesamiento: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== PRUEBAS DE PROCESAMIENTO DE ARCHIVOS PCAP ===")
    
    # Ejecutar prueba
    processing_ok = test_process_pcap_file()
    
    print("\nResumen de pruebas:")
    print(f"- Procesamiento de PCAP: {'✅ OK' if processing_ok else '❌ FALLIDO'}")
