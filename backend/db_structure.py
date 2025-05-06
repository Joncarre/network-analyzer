import sys
import sqlite3

if len(sys.argv) != 2:
    print("Uso: python backend/db_structure.py <ruta_base_de_datos>")
    sys.exit(1)

ruta_db = sys.argv[1]

try:
    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tablas = cursor.fetchall()

    if not tablas:
        print("No se encontraron tablas en la base de datos.")
        sys.exit(0)

    # Diccionario de descripciones por nombre de tabla
    descripciones = {
        'packets': 'Contiene información detallada de cada paquete capturado en la red.',
        'sessions': 'Agrupa los paquetes en sesiones de comunicación entre hosts.',
        'anomalies': 'Registra eventos o patrones detectados como anómalos en el tráfico.',
        'files': 'Almacena información sobre los archivos procesados o capturados.',
        'hosts': 'Lista los dispositivos o direcciones IP detectados en la red.',
        'protocols': 'Define los protocolos de red identificados en el tráfico.',
        # Puedes añadir más descripciones según las tablas habituales de tu proyecto
    }

    print(f"Estructura de la base de datos: {ruta_db}\n")
    for (tabla,) in tablas:
        descripcion = descripciones.get(tabla, 'Contiene datos relacionados con la funcionalidad principal del sistema.')
        print(f"Tabla: {tabla}")
        print(f"  > {descripcion}")
        cursor.execute(f"PRAGMA table_info('{tabla}')")
        columnas = cursor.fetchall()
        for col in columnas:
            # col: (cid, name, type, notnull, dflt_value, pk)
            print(f"  - {col[1]} ({col[2]})")
        print()

except sqlite3.Error as e:
    print(f"Error al abrir la base de datos: {e}")
finally:
    if 'conn' in locals():
        conn.close()
