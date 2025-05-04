from ai.claude_integration import ClaudeAI
import os
import sqlite3
import glob
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# Encontrar archivos de base de datos
db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
db_files = sorted(glob.glob(os.path.join(db_dir, 'database_*.db')), key=os.path.getmtime, reverse=True) # Ordenar por fecha, más reciente primero

if not db_files:
    print(f"No se encontró ninguna base de datos en el directorio: {db_dir}")
    exit(1)

# Listar bases de datos disponibles para selección
print("Bases de datos disponibles:")
for i, db_file in enumerate(db_files):
    print(f"{i + 1}: {os.path.basename(db_file)}") # Mostrar solo el nombre del archivo

# Solicitar selección al usuario
selected_db_index = -1
while selected_db_index < 0 or selected_db_index >= len(db_files):
    try:
        choice = input(f"\nSelecciona el número de la base de datos a usar (1-{len(db_files)}): ")
        selected_db_index = int(choice) - 1
        if selected_db_index < 0 or selected_db_index >= len(db_files):
            print("Selección inválida. Por favor, introduce un número de la lista.")
    except ValueError:
        print("Entrada inválida. Por favor, introduce un número.")

selected_db = db_files[selected_db_index]
print(f"\nUsando base de datos seleccionada: {selected_db}")

# Conectar a la base de datos seleccionada
conn = sqlite3.connect(selected_db)
cursor = conn.cursor()

# Obtener IDs de sesiones disponibles de la DB seleccionada
cursor.execute("SELECT id FROM capture_sessions")
sessions = cursor.fetchall()

# Formatear los IDs para mostrarlos
session_ids = [session[0] for session in sessions]
if len(session_ids) == 1:
    print(f"ID de sesiones disponibles: ({session_ids[0]})")
else:
    print(f"ID de sesiones disponibles: {tuple(session_ids)}")

# Seleccionar una sesión
session_id = int(input("\nIntroduce el ID de la sesión a consultar: "))

# Inicializar el cliente de Claude AI
claude_ai = ClaudeAI()

# Configurar contexto para la sesión seleccionada
cursor.execute("SELECT packet_count FROM capture_sessions WHERE id = ?", (session_id,))
packet_count = cursor.fetchone()[0]

# Obtener distribución de protocolos
cursor.execute("""
    SELECT protocol, COUNT(*) as count 
    FROM packets 
    WHERE session_id = ? 
    GROUP BY protocol
""", (session_id,))
protocols = cursor.fetchall()

# Construir el diccionario de datos de sesión
session_data = {
    "packet_count": packet_count,
    "protocols": {proto: count for proto, count in protocols},
    "anomaly_count": 0  # Podría obtenerse de la base de datos si existe esta información
}

print("\n--- Modo de chat con IA ---")
print("(Escribe 'salir' para terminar)")

# Bucle de chat
while True:
    query = input("\nTu pregunta: ")
    if query.lower() in ['salir', 'exit', 'quit']:
        break
        
    try:
        response = claude_ai.query(query, session_data)
        print("\nRespuesta del AI:")
        print(response)
    except Exception as e:
        print(f"Error al procesar la consulta: {str(e)}")

conn.close()
print("Sesión finalizada")