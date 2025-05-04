import os
import pyshark
import json
import subprocess
from datetime import datetime
import platform
import sys

def find_tshark_path():
    """
    Busca la ruta al ejecutable de TShark en ubicaciones comunes.
    
    Returns:
        str: Ruta al ejecutable de TShark o None si no se encuentra.
    """
    # Comprobar si está en el PATH
    tshark_command = "tshark.exe" if sys.platform == "win32" else "tshark"
    
    try:
        # Intentar ejecutar tshark para ver si está en el PATH
        subprocess.run([tshark_command, "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return tshark_command
    except (subprocess.SubprocessError, FileNotFoundError):
        # No está en el PATH, buscar en ubicaciones comunes
        common_paths = []
        
        if sys.platform == "win32":
            common_paths = [
                r"C:\Program Files\Wireshark\tshark.exe",
                r"C:\Program Files (x86)\Wireshark\tshark.exe",
                # Añadir más rutas comunes de Windows si es necesario
            ]
        else:
            common_paths = [
                "/usr/bin/tshark",
                "/usr/local/bin/tshark",
                "/opt/wireshark/bin/tshark",
                # Añadir más rutas comunes de Linux/Mac si es necesario
            ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
                
        return None

def get_interfaces():
    """
    Obtiene una lista de interfaces de red disponibles en el sistema.
    
    Returns:
        list: Lista de diccionarios con información de las interfaces.
    """
    try:
        # Buscar TShark
        tshark_path = find_tshark_path()
        if not tshark_path:
            print("Error: No se pudo encontrar TShark. Asegúrate de que Wireshark esté instalado.")
            print("Rutas comprobadas:")
            for path in [r"C:\Program Files\Wireshark\tshark.exe", r"C:\Program Files (x86)\Wireshark\tshark.exe"]:
                print(f"  - {path}: {'Existe' if os.path.isfile(path) else 'No existe'}")
            return []
        
        # Detectar el sistema operativo para adaptar el comando
        system = platform.system()
        
        if system == "Windows":
            # En Windows, usamos el comando de tshark para listar interfaces
            process = subprocess.Popen(
                [tshark_path, "-D"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"Error al ejecutar tshark: {stderr}")
                return []
            
            interfaces = []
            for line in stdout.splitlines():
                if line.strip():
                    parts = line.split('.')
                    if len(parts) >= 2:
                        index = parts[0].strip()
                        name = '.'.join(parts[1:]).strip()
                        interfaces.append({
                            "id": index,
                            "name": name
                        })
            return interfaces
        
        else:
            # En Unix/Linux, podemos usar directamente pyshark
            try:
                interfaces = []
                for iface in pyshark.LiveCapture().interfaces:
                    interfaces.append({
                        "id": iface,
                        "name": iface
                    })
                return interfaces
            except Exception as e:
                print(f"Error al obtener interfaces con PyShark: {e}")
                
                # Intentar con tshark como respaldo
                process = subprocess.Popen(
                    [tshark_path, "-D"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    print(f"Error al ejecutar tshark: {stderr}")
                    return []
                
                interfaces = []
                for line in stdout.splitlines():
                    if line.strip():
                        parts = line.split('.')
                        if len(parts) >= 2:
                            index = parts[0].strip()
                            name = '.'.join(parts[1:]).strip()
                            interfaces.append({
                                "id": index,
                                "name": name
                            })
                return interfaces
            
    except Exception as e:
        print(f"Error al obtener interfaces de red: {e}")
        return []

def capture_packets(interface_id, duration=60, output_file=None, packet_count=None, display_filter=None):
    """
    Captura paquetes de una interfaz de red específica.
    
    Args:
        interface_id (str): ID de la interfaz de red.
        duration (int): Duración de la captura en segundos (por defecto: 60).
        output_file (str, opcional): Ruta del archivo donde guardar la captura.
        packet_count (int, opcional): Número máximo de paquetes a capturar.
        display_filter (str, opcional): Filtro de visualización para la captura.
        
    Returns:
        str: Ruta al archivo PCAP generado o None si hubo un error.
    """
    try:
        # Buscar TShark
        tshark_path = find_tshark_path()
        if not tshark_path:
            print("Error: No se pudo encontrar TShark para la captura.")
            return None
            
        # Configurar el nombre del archivo si no se proporciona uno
        if output_file is None:
            # Asegurarse de que existe el directorio para guardar archivos PCAP
            pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
            os.makedirs(pcap_dir, exist_ok=True)
            
            # Crear un nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(pcap_dir, f"capture_{timestamp}.pcap")
        
        print(f"Usando TShark en: {tshark_path}")
        
        # Configurar opciones para la captura usando tshark directamente
        command = [tshark_path, "-i", interface_id, "-w", output_file]
        
        if display_filter:
            command.extend(["-f", display_filter])
            
        # Añadir límite de paquetes si se especifica
        if packet_count:
            command.extend(["-c", str(packet_count)])
            
        # Añadir límite de duración si se especifica y no hay límite de paquetes,
        # o si se especifican ambos (tshark se detendrá con la primera condición)
        if duration:
             command.extend(["-a", f"duration:{duration}"])
            
        print(f"Ejecutando comando: {' '.join(command)}")
        
        # Iniciar la captura con tshark
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Esperar a que termine la captura
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error durante la captura: {stderr.decode('utf-8', errors='replace')}")
            return None
            
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return output_file
        else:
            print("La captura no generó un archivo válido.")
            return None
        
    except Exception as e:
        print(f"Error durante la captura de paquetes: {e}")
        return None
