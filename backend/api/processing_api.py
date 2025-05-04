from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query
from typing import List, Optional
import os
import subprocess
import datetime
import uuid
import shutil
import concurrent.futures
from pathlib import Path
from starlette.responses import FileResponse

from processing.pcap_processor import PCAPProcessor
from database.models import init_db
from capture.network_interfaces import get_interfaces  # Corregir la importación

router = APIRouter(prefix="/api/processing", tags=["processing"])

# Directorio para almacenar los archivos PCAP
PCAP_DIRECTORY = os.getenv('PCAP_DIRECTORY', './data/pcap_files')
os.makedirs(PCAP_DIRECTORY, exist_ok=True)

# Función para ejecutar en un proceso separado
def process_pcap_in_separate_process(pcap_file, interface=None, filter_applied=None):
    """
    Procesa un archivo PCAP en un proceso separado para evitar conflictos con el bucle de eventos.
    
    Args:
        pcap_file: Ruta al archivo PCAP
        interface: Nombre de la interfaz de captura
        filter_applied: Filtro utilizado durante la captura
        
    Returns:
        str: Ruta a la base de datos generada
    """
    try:
        processor = PCAPProcessor()
        db_path = processor.db_path
        processor.process_pcap_file(pcap_file, interface, filter_applied)
        return db_path
    except Exception as e:
        print(f"Error en el procesamiento del archivo PCAP: {e}")
        import traceback
        traceback.print_exc()
        return None

@router.post("/upload-pcap/")
async def upload_pcap_file(
    file: UploadFile = File(...),
    process_immediately: bool = Form(True),
    interface_index: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Sube un archivo PCAP y opcionalmente lo procesa.
    
    Args:
        file: Archivo PCAP a subir
        process_immediately: Si es True, procesa el archivo inmediatamente
        interface_index: Índice de la interfaz de captura (opcional)
        background_tasks: Tareas en segundo plano
    
    Returns:
        dict: Información sobre el archivo subido y su procesamiento
    """
    # Verificar que es un archivo PCAP
    if not file.filename.lower().endswith('.pcap'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PCAP")
    
    # Comprobar si ya existe un archivo con el mismo nombre
    if os.path.exists(os.path.join(PCAP_DIRECTORY, file.filename)):
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe un archivo con el nombre '{file.filename}'. Por favor, elige otro nombre."
        )
    
    # Guardar el archivo
    file_path = os.path.join(PCAP_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Si se especifica un índice de interfaz, obtener el nombre de la interfaz
    interface = None
    if interface_index is not None:
        try:
            interfaces = get_interfaces()
            if interfaces and len(interfaces) > int(interface_index):
                interface = interfaces[int(interface_index)].get('name')
        except Exception as e:
            print(f"Error al obtener la interfaz: {e}")
    
    # Procesar el archivo si se solicita
    db_path = None
    file_size = None # Variable para guardar el tamaño antes de borrar
    if process_immediately:
        try:
            print(f"Procesando archivo: {file_path}")
            file_size = os.path.getsize(file_path) # Obtener tamaño ANTES de procesar/borrar
            
            # Usar concurrent.futures para ejecutar en un proceso separado
            with concurrent.futures.ProcessPoolExecutor() as executor:
                future = executor.submit(
                    process_pcap_in_separate_process,
                    file_path,
                    interface,
                    None  # filter_applied
                )
                db_path = future.result()  # Esperar a que termine el procesamiento
                
            if not db_path:
                print(f"⚠️ El procesamiento del archivo {file.filename} no generó una base de datos válida")
            else:
                # Eliminar el archivo PCAP original si el procesamiento fue exitoso
                try:
                    os.remove(file_path)
                    print(f"Archivo PCAP original '{file.filename}' eliminado después del procesamiento exitoso.")
                except OSError as e:
                    print(f"Error al eliminar el archivo PCAP '{file_path}': {e}")
                    
        except Exception as e:
            print(f"❌ Error al procesar el archivo {file.filename}: {e}")
            import traceback
            traceback.print_exc()
            # Si hubo error procesando, no borramos y file_size puede ser None o tener valor previo
            if file_size is None and os.path.exists(file_path):
                 file_size = os.path.getsize(file_path)

    # Si no se procesó inmediatamente, obtener tamaño ahora
    elif os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
    
    return {
        "file_name": file.filename,
        "file_path": file_path, 
        "size": file_size, # Usar el tamaño guardado
        "processed": process_immediately and db_path is not None,
        "db_path": db_path if db_path else None
    }
