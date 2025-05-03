from ai.claude_integration import ClaudeAI
import os
import sqlite3
import glob
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# Encontrar el archivo de base de datos más reciente
db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
db_files = glob.glob(os.path.join(db_dir, 'database_*.db'))
if not db_files:
    print("No se encontró ninguna base de datos")
    exit(1)
latest_db = max(db_files, key=os.path.getmtime)
print(f"Usando base de datos: {latest_db}")

# Conectar a la base de datos
conn = sqlite3.connect(latest_db)
cursor = conn.cursor()

# Obtener IDs de sesiones disponibles
cursor.execute("SELECT id, file_name FROM capture_sessions")
sessions = cursor.fetchall()
print("Sesiones disponibles:")
for session_id, file_name in sessions:
    print(f"ID: {session_id}, Archivo: {file_name}")

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