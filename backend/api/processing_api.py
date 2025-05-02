from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import os
import shutil
from datetime import datetime
import time  # Import time module

# Cambiar imports relativos a absolutos
from processing.pcap_processor import PCAPProcessor
from database.models import init_db

router = APIRouter(prefix="/api/processing", tags=["processing"])

@router.post("/upload-pcap")
async def upload_pcap_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    process_now: bool = Form(False),
    interface: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Sube un archivo PCAP y opcionalmente lo procesa.
    """
    try:
        # Verificar que es un archivo PCAP
        if not file.filename.endswith(('.pcap', '.pcapng')):
            raise HTTPException(status_code=400, detail="El archivo debe tener extensión .pcap o .pcapng")
            
        # Guardar el archivo en el directorio de PCAP
        pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
        os.makedirs(pcap_dir, exist_ok=True)
        
        # Usar el nombre original del archivo
        filename = file.filename
        file_path = os.path.join(pcap_dir, filename)
        
        # Verificar si el archivo ya existe y rechazar la subida en ese caso
        if os.path.exists(file_path):
            raise HTTPException(
                status_code=409, # Conflict - código HTTP adecuado para recursos duplicados
                detail=f"Ya existe un archivo con el nombre '{filename}'."
            )
        
        # Guardar el archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        response = {
            "message": f"Archivo {filename} subido correctamente",
            "file_path": file_path,
            "file_name": filename
        }
        
        # Procesar el archivo si se solicita
        if process_now:
            background_tasks.add_task(
                process_pcap_file_task,
                file_path=file_path,
                interface=interface
            )
            response["processing"] = "Procesamiento iniciado en segundo plano"
        
        return response
        
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

@router.post("/process-pcap")
async def process_pcap(
    background_tasks: BackgroundTasks,
    file_path: str,
    interface: Optional[str] = None
) -> Dict[str, str]:
    """
    Procesa un archivo PCAP ya existente.
    """
    try:
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {file_path}")
            
        # Iniciar procesamiento en segundo plano
        background_tasks.add_task(
            process_pcap_file_task,
            file_path=file_path,
            interface=interface
        )
        
        return {
            "message": "Procesamiento iniciado en segundo plano",
            "file_path": file_path,
            "file_name": os.path.basename(file_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar procesamiento: {str(e)}")

@router.get("/status")
async def get_processing_status() -> Dict[str, Any]:
    """
    Obtiene el estado del procesamiento (a implementar en una fase posterior).
    """
    return {"message": "Estado de procesamiento no implementado aún"}

# Función para ejecutar en segundo plano
async def process_pcap_file_task(file_path: str, interface: Optional[str] = None):
    """
    Tarea en segundo plano para procesar un archivo PCAP.
    """
    start_time = time.time()  # Use time.time() for better precision
    session_id = None
    db_path_used = None  # Variable to store the actual db path used
    try:
        # Get the database path that will be used by the processor
        # This relies on PCAPProcessor using the same logic (env var or default)
        db_path_used = os.getenv('DATABASE_PATH', './data/db_files/network_analyzer.db')

        # Ensure the directory exists (although PCAPProcessor might do this too)
        os.makedirs(os.path.dirname(db_path_used), exist_ok=True)

        # Initialize processor (it will use the db_path_used internally via its default logic)
        processor = PCAPProcessor()

        print(f"Procesando archivo: {file_path}")  # Log start

        # Procesar el archivo
        session_id = processor.process_pcap_file(
            pcap_file=file_path,
            interface=interface
        )

        end_time = time.time()
        duration = end_time - start_time

        # Updated success log message
        print(f"✅ Procesamiento completado en {duration:.2f}s")
        print(f"ID de sesión: {session_id}")
        print(f"Base de datos: {db_path_used}")  # Explicitly state the DB file used

    except FileNotFoundError:
        print(f"❌ Error: Archivo no encontrado - {file_path}")
    except Exception as e:
        # Updated error log message
        print(f"❌ Error en el procesamiento en segundo plano para '{os.path.basename(file_path)}': {e}")
        # Consider adding traceback for debugging if needed:
        # import traceback
        # print(traceback.format_exc())
