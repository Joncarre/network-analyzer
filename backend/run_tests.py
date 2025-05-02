import os
import sys
import subprocess

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f" {text} ".center(60, "="))
    print("="*60)

def run_test_script(script_name):
    """Ejecuta un script de prueba y devuelve el código de salida"""
    print_header(f"EJECUTANDO {script_name}")
    
    # Ejecutar el script en un proceso separado
    result = subprocess.run(
        [sys.executable, os.path.join("tests", script_name)],
        capture_output=False
    )
    
    return result.returncode == 0

if __name__ == "__main__":
    print_header("PRUEBAS DEL BACKEND DE NETWORK ANALYZER")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("main.py"):
        print("❌ Error: Este script debe ejecutarse desde el directorio raíz del backend")
        print("   Navega a la carpeta backend y ejecuta: python run_tests.py")
        sys.exit(1)
    
    # Crear directorio de tests si no existe
    if not os.path.exists("tests"):
        os.makedirs("tests")
    
    # Lista de scripts de prueba
    test_scripts = [
        "test_simplified.py",
        "test_capture_simplified.py"
    ]
    
    # Resultado de pruebas
    results = {}
    
    # Preguntar qué pruebas ejecutar
    print("Selecciona las pruebas a ejecutar:")
    print("1. Pruebas básicas (entorno y conexiones)")
    print("2. Prueba de captura de tráfico")
    print("3. Todas las pruebas")
    
    try:
        option = int(input("\nOpción (1-3): "))
        
        if option == 1:
            test_scripts = ["test_simplified.py"]
        elif option == 2:
            test_scripts = ["test_capture_simplified.py"]
        elif option == 3:
            pass  # Mantener la lista completa
        else:
            print("❌ Opción inválida, ejecutando todas las pruebas")
            
    except ValueError:
        print("❌ Entrada inválida, ejecutando todas las pruebas")
    
    # Ejecutar cada script de prueba
    for script in test_scripts:
        results[script] = run_test_script(script)
    
    # Mostrar resumen de resultados
    print_header("RESUMEN DE RESULTADOS")
    all_passed = True
    
    for script, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{script}: {status}")
        if not passed:
            all_passed = False
    
    print("\nEstado general:", "✅ TODAS LAS PRUEBAS PASARON" if all_passed else "❌ ALGUNAS PRUEBAS FALLARON")
    
    print_header("FIN DE LAS PRUEBAS")
