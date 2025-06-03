# Network Analyzer 🌐

Network Analyzer es una herramienta completa para captura, análisis y visualización de tráfico de red con capacidades avanzadas de procesamiento e interpretación mediante IA. El proyecto combina potentes tecnologías de backend para la captura de paquetes con una interfaz web moderna y accesible.

## Descripción

Esta herramienta permite capturar paquetes de red en tiempo real, procesarlos, almacenarlos estructuradamente y analizarlos mediante consultas en lenguaje natural. Está pensada tanto para profesionales de seguridad como para administradores de red que quieran entender mejor su tráfico y detectar posibles amenazas o comportamientos anómalos.

## Estructura del proyecto

El proyecto está dividido en dos componentes principales:

### Backend (Python/FastAPI)
- **Captura**: Interfaces con TShark para la captura de paquetes
- **Procesamiento**: Conversión de archivos PCAP a estructuras de datos analizables
- **Base de datos**: Almacenamiento SQLite de sesiones, paquetes y anomalías
- **API REST**: Endpoints para todas las funcionalidades
- **Integración IA**: Conexión con Claude AI para análisis en lenguaje natural

### Frontend (React)
- **Interfaz visual**: Diseño moderno y responsivo usando TailwindCSS
- **Captura**: Panel para iniciar capturas o subir archivos PCAP
- **Análisis**: Visualización de paquetes, anomalías y estadísticas
- **Chat IA**: Interfaz conversacional para consultas sobre el tráfico

## Funcionalidades principales ✨

- Captura de paquetes en tiempo real desde cualquier interfaz de red
- Procesamiento y análisis de archivos PCAP existentes
- Almacenamiento estructurado en bases de datos SQLite
- Detección automática de anomalías en el tráfico
- Visualización estadística del tráfico capturado (protocolos, IPs, puertos)
- Interfaz conversacional con IA para consultar y analizar los datos capturados
- Diferentes modos de respuesta (corto, normal, detallado) para la IA

## Requisitos técnicos

- Python 3.8 o superior
- Node.js 14.x o superior
- TShark (parte de Wireshark)
- Acceso a una interfaz de red para captura

## Instalación y configuración 🛠️

### Configuración del backend

1. Clona el repositorio:
```
git clone https://github.com/tu_usuario/network-analyzer.git
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

4. Crea un archivo `.env` en la carpeta `backend` con las siguientes variables (modifica según tu configuración):
```
ANTHROPIC_API_KEY=tu_clave_api_de_anthropic
HOST=localhost
PORT=8000
DEBUG=true
DATABASE_DIRECTORY=./data/db_files
PCAP_DIRECTORY=./data/pcap_files
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

## Uso 🚀

### Iniciar el backend

En el directorio `backend`, ejecuta:
```
python run.py
```

El servidor se iniciará en `http://localhost:8000` por defecto.

### Iniciar el frontend

En el directorio `frontend`, ejecuta:
```
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

### Flujo de trabajo típico

1. Ve a la sección "Captura" para iniciar una captura de red o subir un archivo PCAP existente
2. Espera a que se procese la captura
3. En la sección "Análisis", selecciona la base de datos y sesión de captura deseada
4. Explora los paquetes capturados, anomalías detectadas y estadísticas generadas
5. Utiliza la interfaz de chat para hacer preguntas sobre el tráfico capturado

## Tipos de pruebas posibles

El sistema permite realizar diversos tipos de pruebas:

- **Captura básica**: Permite capturar paquetes durante un tiempo determinado
- **Análisis de vulnerabilidades**: Identifica patrones y anomalías que podrían indicar problemas de seguridad
- **Análisis de rendimiento**: Examina volúmenes de tráfico, distribución de protocolos y tiempos de respuesta
- **Detección de comportamientos anómalos**: Identifica tráfico inusual o sospechoso en la red
- **Investigación específica**: Permite filtrar y consultar paquetes según criterios específicos mediante consultas a la IA

## Ejemplos de consultas para la IA

- "¿Cuáles son los protocolos más utilizados en esta captura?"
- "¿Hay indicios de escaneos de puertos en esta sesión?"
- "¿Qué IPs han generado más tráfico?"
- "¿Puedes identificar alguna actividad sospechosa en esta captura?"
- "¿Cuáles son las comunicaciones más frecuentes entre hosts?"

## Resolución de problemas

- Si tienes problemas con la captura, asegúrate de que TShark esté instalado correctamente
- La mayoría de los errores de instalación se resuelven asegurando compatibilidad de versiones de dependencias
- Para problemas de permisos en Linux/macOS, puede ser necesario ejecutar la aplicación con permisos elevados para acceder a las interfaces de red

## Licencia

Este proyecto está licenciado bajo la licencia MIT.

## Contacto

Para cualquier consulta o sugerencia, puedes contactar a:
jonathan.carrero@alumnos.ui1.es

---
<<<<<<< HEAD
=======

>>>>>>> 3dfef019c701bea09a909c19cede314dba2dbdb8
