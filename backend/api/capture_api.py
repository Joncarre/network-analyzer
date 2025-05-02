from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import os
from datetime import datetime

from capture.network_interfaces import get_interfaces, capture_packets

router = APIRouter(prefix="/api/capture", tags=["capture"])

@router.get("/interfaces")
async def list_interfaces() -> List[Dict[str, Any]]:
    """
    Lista las interfaces de red disponibles para captura.
    """
    interfaces = get_interfaces()
    if not interfaces:
        raise HTTPException(status_code=500, detail="No se pudieron obtener las interfaces de red")
    return interfaces

@router.post("/start")
async def start_capture(
    interface_id: str,
    duration: int = Query(60, description="Duración de la captura en segundos"),
    packet_count: Optional[int] = Query(None, description="Número de paquetes a capturar")
) -> Dict[str, str]:
    """
    Inicia una captura de paquetes en la interfaz especificada.
    """
    try:
        # Configurar el nombre del archivo
        pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
        os.makedirs(pcap_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(pcap_dir, f"capture_{timestamp}.pcap")
        
        # Iniciar la captura
        result_file = capture_packets(
            interface_id=interface_id,
            duration=duration,
            output_file=output_file,
            packet_count=packet_count
        )
        
        if not result_file:
            raise HTTPException(status_code=500, detail="Error al realizar la captura")
            
        return {
            "message": "Captura completada con éxito",
            "file_path": result_file,
            "file_name": os.path.basename(result_file)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la captura: {str(e)}")

@router.get("/files")
async def list_pcap_files() -> List[Dict[str, Any]]:
    """
    Lista los archivos PCAP disponibles.
    """
    try:
        pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
        os.makedirs(pcap_dir, exist_ok=True)
        
        files = []
        for file in os.listdir(pcap_dir):
            if file.endswith(".pcap"):
                file_path = os.path.join(pcap_dir, file)
                file_stats = os.stat(file_path)
                files.append({
                    "name": file,
                    "path": file_path,
                    "size": file_stats.st_size,
                    "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                })
        
        return files
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar archivos PCAP: {str(e)}")
