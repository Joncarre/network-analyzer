import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from api.capture_api import router as capture_router
from api.processing_api import router as processing_router
from api.database_api import router as database_router
from api.ai_api import router as ai_router

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación FastAPI
app = FastAPI(
    title="Network Analyzer API",
    description="API para análisis de tráfico de red con IA",
    version="0.1.0",
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de desarrollo de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(capture_router)
app.include_router(processing_router)
app.include_router(database_router)
app.include_router(ai_router)

@app.get("/")
async def root():
    return {"mensaje": "API de Network Analyzer", "estado": "funcionando"}

# Configurar directorio estático para archivos PCAP
pcap_dir = os.getenv("PCAP_DIRECTORY", "./data/pcap_files/")
os.makedirs(pcap_dir, exist_ok=True)
app.mount("/pcap-files", StaticFiles(directory=pcap_dir), name="pcap-files")
