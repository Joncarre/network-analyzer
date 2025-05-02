import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(text):
    """Imprime un paso de configuración con formato"""
    print(f"\n🔹 {text}")

def print_success(text):
    """Imprime un mensaje de éxito con formato"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime un mensaje de error con formato"""
    print(f"❌ {text}")

def print_warning(text):
    """Imprime un mensaje de advertencia con formato"""
    print(f"⚠️ {text}")

def check_python_version():
    """Verifica que la versión de Python sea compatible"""
    print_step("Verificando versión de Python")
    
    if sys.version_info < (3, 10):
        print_error(f"Se requiere Python 3.10 o superior. Versión actual: {sys.version}")
        return False
    
    print_success(f"Python {sys.version.split()[0]} detectado")
    return True

def check_install_dependencies():
    """Verifica e instala las dependencias necesarias"""
    print_step("Verificando dependencias")
    
    # Verificar si existe requirements.txt
    if not os.path.exists("requirements.txt"):
        print_error("No se encontró el archivo requirements.txt")
        return False
    
    try:
        # Instalar dependencias
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al instalar dependencias: {e}")
        return False

def check_wireshark():
    """Verifica que Wireshark/TShark esté instalado"""
    print_step("Verificando instalación de Wireshark/TShark")
    
    # Comprobar si tshark está en el PATH
    tshark_path = shutil.which("tshark")
    if tshark_path:
        print_success(f"TShark encontrado en: {tshark_path}")
        return True
    
    print_warning("TShark no encontrado en el PATH")
    
    # Comprobar ubicaciones comunes en Windows
    windows_paths = [
        r"C:\Program Files\Wireshark\tshark.exe",
        r"C:\Program Files (x86)\Wireshark\tshark.exe"
    ]
    
    for path in windows_paths:
        if os.path.exists(path):
            print_success(f"TShark encontrado en: {path}")
            print_warning("Pero no está en el PATH. Considera añadirlo al PATH del sistema.")
            return True
    
    print_error("Wireshark/TShark no encontrado. Por favor instálalo desde: https://www.wireshark.org/download.html")
    return False

def check_env_file():
    """Verifica y crea el archivo .env si no existe"""
    print_step("Verificando archivo .env")
    
    if os.path.exists(".env"):
        print_success("Archivo .env encontrado")
        
        # Verificar si tiene la clave API de Anthropic
        with open(".env", "r") as f:
            env_content = f.read()
            if "ANTHROPIC_API_KEY" in env_content:
                print_success("ANTHROPIC_API_KEY configurada en .env")
            else:
                print_warning("ANTHROPIC_API_KEY no encontrada en .env. Las pruebas de IA fallarán.")
                
        return True
    
    print_warning("Archivo .env no encontrado, creando uno de ejemplo...")
    
    # Crear directorios para archivos
    data_dir = Path("./data/pcap_files")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear archivo .env de ejemplo
    with open(".env", "w") as f:
        f.write("""# API de Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configuraciones de la aplicación
DEBUG=True
HOST=localhost
PORT=8000

# Configuraciones de la base de datos
DATABASE_PATH=./data/network_analyzer.db

# Directorio para guardar archivos PCAP
PCAP_DIRECTORY=./data/pcap_files/
""")
    
    print_warning("Se ha creado un archivo .env de ejemplo.")
    print_warning("Por favor, edita el archivo .env y configura ANTHROPIC_API_KEY con tu clave API.")
    
    return True

def create_directories():
    """Crea los directorios necesarios si no existen"""
    print_step("Creando directorios necesarios")
    
    # Directorios a crear
    directories = [
        "./data",
        "./data/pcap_files",
        "./tests"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print_success("Directorios creados correctamente")
    return True

def check_admin_privileges():
    """Verifica si el script se está ejecutando con privilegios de administrador"""
    print_step("Verificando privilegios de administrador")
    
    try:
        is_admin = False
        
        if os.name == 'nt':  # Windows
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:  # Unix/Linux/Mac
            is_admin = os.geteuid() == 0
            
        if is_admin:
            print_success("Ejecutando con privilegios de administrador")
        else:
            print_warning("No se están utilizando privilegios de administrador")
            print_warning("La captura de paquetes puede requerir permisos de administrador")
            print_warning("Considera ejecutar como administrador: ")
            print_warning("   En Windows: Clic derecho en PowerShell/CMD -> Ejecutar como administrador")
            print_warning("   En Linux/Mac: sudo python setup_tests.py")
        
        return True
            
    except Exception as e:
        print_warning(f"No se pudo determinar el nivel de privilegios: {e}")
        return True

def main():
    """Función principal"""
    print("\n" + "="*50)
    print("CONFIGURACIÓN PARA PRUEBAS DE NETWORK ANALYZER")
    print("="*50 + "\n")
    
    # Ejecutar todas las verificaciones
    python_ok = check_python_version()
    deps_ok = check_install_dependencies()
    wireshark_ok = check_wireshark()
    env_ok = check_env_file()
    dirs_ok = create_directories()
    admin_check = check_admin_privileges()
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE CONFIGURACIÓN")
    print("="*50)
    
    all_ok = python_ok and deps_ok and wireshark_ok and env_ok and dirs_ok
    
    print(f"\nVersión de Python: {'✅ OK' if python_ok else '❌ ERROR'}")
    print(f"Dependencias: {'✅ OK' if deps_ok else '❌ ERROR'}")
    print(f"Wireshark/TShark: {'✅ OK' if wireshark_ok else '❌ ERROR'}")
    print(f"Archivo .env: {'✅ OK' if env_ok else '❌ ERROR'}")
    print(f"Directorios: {'✅ OK' if dirs_ok else '❌ ERROR'}")
    
    print("\n" + "="*50)
    
    if all_ok:
        print("\n✅ CONFIGURACIÓN COMPLETA. Puede ejecutar las pruebas con:")
        print("   python run_tests.py")
    else:
        print("\n❌ HAY PROBLEMAS DE CONFIGURACIÓN. Corrígelos antes de continuar.")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
