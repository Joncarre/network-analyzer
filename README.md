# Network Analyzer

Aplicación web para análisis de tráfico de red con IA, enfocada en captura, procesamiento y visualización de paquetes de red utilizando lenguaje natural.

## Características

- Captura de tráfico de red y generación de archivos PCAP
- Procesamiento de archivos PCAP y almacenamiento en base de datos SQLite
- Consultas en lenguaje natural mediante IA (Anthropic Claude)
- Interfaz web intuitiva para visualización de datos
- Detección de anomalías y patrones sospechosos

## Requisitos del Sistema

- Python 3.10+
- Node.js 16+
- TShark/Wireshark
- Permisos de administrador (para la captura de paquetes)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/username/network-analyzer.git
cd network-analyzer
```

2. Configurar el entorno backend:
```bash
cd backend
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

3. Configurar el entorno frontend:
```bash
cd ../frontend
npm install
```

4. Copiar el archivo .env.example a .env y configurar las variables de entorno:
```bash
cp .env.example .env
# Editar el archivo .env con tus claves de API y configuraciones
```

## Uso

1. Iniciar el servidor backend:
```bash
cd backend
python main.py
```

2. Iniciar el servidor de desarrollo frontend:
```bash
cd frontend
npm run dev
```

3. Acceder a la aplicación web en http://localhost:5173

## Desarrollo

El proyecto está estructurado en fases progresivas:
- Fase 1: Configuración del proyecto
- Fase 2: Captura de tráfico
- Fase 3: Procesamiento y almacenamiento
- Fase 4: API backend
- Fase 5: Interfaz de usuario
- Fase 6: Integración y pruebas

## Licencia

[MIT](LICENSE)
