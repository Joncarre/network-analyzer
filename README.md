# Network Analyzer

## Descripción
Network Analyzer es una herramienta de análisis de tráfico de red que permite capturar, procesar y analizar paquetes de red. La aplicación incluye una interfaz web interactiva para visualizar los datos capturados, detectar anomalías y consultar detalles sobre el tráfico de red mediante un asistente de IA integrado.

## Funcionalidades principales
- Captura de paquetes de red en interfaces seleccionadas
- Carga y procesamiento de archivos PCAP existentes
- Análisis estadístico de tráfico de red
- Detección de anomalías en el tráfico
- Visualización detallada de paquetes y conexiones
- Filtrado de paquetes y anomalías por diversos criterios
- Asistente de IA para responder preguntas sobre los datos capturados

## Estructura del proyecto
El proyecto se divide en dos componentes principales:

### Backend (Python con FastAPI)
- API RESTful para gestionar las funcionalidades del sistema
- Captura y procesamiento de paquetes mediante bibliotecas especializadas
- Almacenamiento de datos en bases de datos SQLite
- Integración con IA para análisis y consultas sobre los datos

### Frontend (React)
- Interfaz de usuario moderna y responsive
- Visualización de datos de capturas y análisis
- Filtrado interactivo de datos
- Interfaz de chat para consultas a la IA

## Requisitos previos
### Para el backend
- Python 3.10 o superior
- Bibliotecas Python (ver `backend/requirements.txt`)
- Privilegios de administrador o root (necesarios para la captura de paquetes)
- Librerías del sistema: libpcap (Linux/macOS) o Npcap/Winpcap (Windows)

### Para el frontend
- Node.js 16 o superior
- NPM 7 o superior

## Instalación

### Configuración del backend
1. Clona el repositorio:
```
git clone https://github.com/[usuario]/network-analyzer.git
cd network-analyzer
```

2. Crea y activa un entorno virtual de Python:
```
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias del backend:
```
cd backend
pip install -r requirements.txt
```

### Configuración del frontend
1. Navega al directorio del frontend:
```
cd ../frontend
```

2. Instala las dependencias del frontend:
```
npm install
```

## Uso

### Iniciar el backend
En el directorio `backend`, ejecuta:
```
python run.py
```
El servidor backend estará disponible en `http://localhost:8000`

### Iniciar el frontend
En el directorio `frontend`, ejecuta:
```
npm run dev
```
La aplicación frontend estará disponible en `http://localhost:5173`

## Instrucciones de uso

### Página de captura
1. Selecciona una interfaz de red de la lista desplegable
2. Establece la duración de la captura y el límite de paquetes
3. Haz clic en "Iniciar Captura" para comenzar a capturar paquetes
4. Alternativamente, puedes subir un archivo PCAP existente

### Página de análisis
1. Selecciona una sesión de captura de la lista
2. Explora las estadísticas generales, paquetes capturados y anomalías detectadas
3. Utiliza los filtros disponibles para refinar la visualización de datos
4. Utiliza el chat con IA para realizar consultas sobre los datos

## Dependencias principales

### Backend
- **FastAPI**: Framework web para APIs
- **Scapy**: Manipulación de paquetes de red
- **SQLAlchemy**: ORM para base de datos
- **Anthropic SDK**: Integración con Claude AI
- **Pandas**: Análisis de datos

### Frontend
- **React**: Biblioteca para interfaces de usuario
- **Tailwind CSS**: Framework CSS para estilos
- **Axios**: Cliente HTTP para peticiones a la API
- **React Router**: Enrutamiento para aplicación SPA
- **Lodash**: Utilidades JavaScript

## Seguridad
- La captura de paquetes requiere privilegios elevados
- Los datos sensibles no deben ser subidos a repositorios públicos
- Utiliza el archivo `.gitignore` para evitar compartir datos confidenciales
- Considera cifrar los archivos PCAP si contienen información sensible

## Licencia
[Especificar la licencia del proyecto]

## Contacto
[Información de contacto del mantenedor]
