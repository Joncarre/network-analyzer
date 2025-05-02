import os
import sys
from datetime import datetime # Import datetime

# Añadir el directorio actual al path de Python para poder usar imports absolutos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Generate timestamped database path ---
db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'db_files'))
os.makedirs(db_dir, exist_ok=True) # Ensure the directory exists
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db_filename = f"database_{timestamp}.db"
db_path = os.path.join(db_dir, db_filename)

# --- Set DATABASE_PATH environment variable ---
os.environ['DATABASE_PATH'] = db_path
print(f"[INFO] Using database: {db_path}") # Log the database path being used
# -----------------------------------------

# Importar y ejecutar la aplicación principal (AFTER setting env var)
from main import app
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    # Initialize the database (optional, but good practice)
    # This will now use the DATABASE_PATH set above
    from database.models import init_db
    init_db()

    uvicorn.run("main:app", host=host, port=port, reload=debug)
