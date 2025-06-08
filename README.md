# Network Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Herramienta completa para captura, análisis y visualización de tráfico de red con IA**

Network Analyzer es una solución moderna y potente que combina tecnologías avanzadas de backend para la captura de paquetes con una interfaz web intuitiva y accesible. Perfecta para **profesionales de seguridad**, **administradores de red** y **estudiantes** que desean comprender y analizar el tráfico de red de manera eficiente.

## 🚀 ¿Qué funcionalidades ofrece Network Analyzer?

**Captura paquetes de red** en tiempo real desde cualquier interfaz  
**Analiza con IA** el tráfico usando consultas en lenguaje natural  
**Visualiza estadísticas** detalladas y comportamientos de red  
 **Detecta anomalías** y posibles amenazas automáticamente  
**Almacena datos** estructuradamente para análisis posteriores  
**Interactúa conversacionalmente** para explorar los resultados

## 🏗️ Arquitectura del Proyecto

El proyecto está construido con una **arquitectura moderna de microservicios** dividida en dos componentes principales:

#### Backend (Python/FastAPI)
> **El cerebro del sistema** - Maneja toda la lógica de procesamiento y análisis

| Módulo | Descripción | Tecnología |
|--------|-------------|------------|
| 📡 **Captura** | Interfaces con TShark para captura de paquetes | TShark/Wireshark |
| ⚙️ **Procesamiento** | Convierte archivos PCAP a estructuras analizables | Pandas/Python |
| 🗄️ **Base de datos** | Almacenamiento SQLite de sesiones y anomalías | SQLite |
| 🔌 **API REST** | Endpoints para todas las funcionalidades | FastAPI |
| 🤖 **Integración IA** | Conexión con Claude AI para análisis inteligente | Anthropic Claude |

#### Frontend (React)
> **La cara amigable** - Interfaz visual moderna y responsiva

| Componente | Función | Tecnología |
|------------|---------|------------|
| 🎨 **Interfaz visual** | Diseño moderno y responsivo | React + TailwindCSS |
| 📥 **Captura** | Panel para iniciar capturas o subir PCAPs | React Components |
| 📊 **Análisis** | Visualización de paquetes y estadísticas | Chart.js |
| 💬 **Chat IA** | Interfaz conversacional para consultas | WebSocket + React |

## ✨ Funcionalidades Principales

> **Todo lo que necesitas para análisis de red profesional**

### 📡 Captura y Procesamiento
- 🔴 **Captura en tiempo real** desde cualquier interfaz de red
- 📁 **Procesamiento de archivos PCAP** existentes
- 💾 **Almacenamiento inteligente** en bases de datos SQLite optimizadas
- 🔍 **Detección automática** de anomalías y patrones sospechosos

### 📊 Análisis y Visualización
- 📈 **Estadísticas avanzadas** de tráfico (protocolos, IPs, puertos)
- 🎯 **Visualización interactiva** de datos de red
- 🚨 **Alertas inteligentes** para comportamientos anómalos
- 📋 **Reportes detallados** exportables

### 🤖 Inteligencia Artificial
- 💬 **Chat conversacional** para consultas en lenguaje natural
- 🎛️ **Modos de respuesta configurables** (corto, normal, detallado)
- 🧠 **Análisis inteligente** de patrones de tráfico
- 🔮 **Predicción de amenazas** basada en comportamientos

## 💻 Requisitos del Sistema

>  **Configuración mínima recomendada**

| Componente | Requisito | Versión Mínima | Recomendado |
|------------|-----------|----------------|-------------|
| 🐍 **Python** | Intérprete Python | 3.8+ | 3.10+ |
| 🟢 **Node.js** | Runtime JavaScript | 14.x+ | 18.x+ |
| 🦈 **TShark** | Analizador de paquetes | Última | Wireshark suite |
| 🌐 **Interfaz de red** | Acceso a adaptadores | Requerido | Permisos admin |
| 💾 **Memoria RAM** | Para procesamiento | 4GB+ | 8GB+ |
| 💿 **Espacio en disco** | Para almacenamiento | 1GB+ | 10GB+ |

## 🛠️ Instalación y Configuración

> **Puesta en marcha de manera rápida y sencilla**

### Paso 1: Obtener el Código

```bash
# Clona el repositorio
git clone https://github.com/tu_usuario/network-analyzer.git
cd network-analyzer
```

### Paso 2: Configurar el Backend

<details>
<summary>🔧 <strong>Configuración detallada del backend</strong></summary>

#### 2.1 Crear entorno virtual
```bash
# En Windows 🪟
python -m venv venv
venv\Scripts\activate

# En Linux/macOS 🐧🍎
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Instalar dependencias
```bash
cd backend
pip install -r requirements.txt
```

#### 2.3 Configurar variables de entorno
Crea un archivo `.env` en la carpeta `backend` con:
```env
# 🔑 Configuración de IA
ANTHROPIC_API_KEY=tu_clave_api_de_anthropic

# 🌐 Configuración del servidor
HOST=localhost
PORT=8000
DEBUG=true

# 📁 Configuración de directorios
DATABASE_DIRECTORY=./data/db_files
PCAP_DIRECTORY=./data/pcap_files
```
</details>

### Paso 3: Configurar el Frontend

```bash
# Navegar al directorio del frontend
cd ../frontend

# Instalar dependencias
npm install
```

## Cómo Usar Network Analyzer

> 💡 **¡Es más fácil de lo que piensas!**

### 🟢 Iniciar el Sistema

#### Backend (Servidor API)
```bash
cd backend
python run.py
```
🌐 **Servidor disponible en:** `http://localhost:8000`

#### Frontend (Interfaz Web)
```bash
cd frontend  
npm run dev
```
🎨 **Interfaz disponible en:** `http://localhost:5173`

### 📋 Flujo de Trabajo Típico

> 🎯 **Sigue estos pasos para un análisis completo**

| Paso | Acción | Descripción |
|------|--------|-------------|
| **1️⃣** | 🎯 **Inicializar** | Accede a la interfaz web y selecciona tu modo de trabajo |
| **2️⃣** | 📡 **Capturar** | Inicia captura en vivo o sube un archivo PCAP existente |
| **3️⃣** | ⏳ **Procesar** | Espera mientras el sistema procesa y analiza los datos |
| **4️⃣** | 🔍 **Explorar** | Navega por paquetes, anomalías y estadísticas generadas |
| **5️⃣** | 💬 **Consultar** | Usa el chat IA para hacer preguntas específicas |
| **6️⃣** | 📊 **Analizar** | Revisa gráficos, métricas y reportes detallados |
| **7️⃣** | 📋 **Exportar** | Guarda resultados y reportes para uso posterior |


## 💬 Ejemplos de onsultas

> **Pregúntale cualquier cosa a tu IA asistente**

### Consultas Básicas
```
 "¿Cuáles son los protocolos más utilizados en esta captura?"
 "¿Qué IPs han generado más tráfico?"
 "Muéstrame un resumen de la actividad de red"
 "¿Cuántos paquetes se capturaron en total?"
```

### Análisis de Seguridad
```
 "¿Hay indicios de escaneos de puertos en esta sesión?"
 "¿Puedes identificar alguna actividad sospechosa?"
 "¿Hay patrones de comunicación anómalos?"
 "¿Detectas algún intento de intrusión?"
```

### Análisis Estadístico
```
 "¿Cuáles son las comunicaciones más frecuentes entre hosts?"
 "¿Qué puertos están siendo más utilizados?"
 "¿Hay algún pico de tráfico inusual?"
 "Analiza la distribución de protocolos por tiempo"
```

###  Investigación Forense
```
 "¿Qué hizo la IP 192.168.1.100 durante la captura?"
 "¿Hay transferencias de archivos sospechosas?"
 "¿Qué dispositivos se conectaron durante este período?"
 "Analiza las conexiones salientes no autorizadas"
```

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto y Soporte

> 💬 **¡Estamos aquí para ayudarte!**

### 👨‍💼 Desarrollador Principal
**Jonathan Carrero**  
📧 **Email:** jonathan.carrero@alumnos.ui1.es  
🎓 **Institución:** Universidad Isabel I  

### 🤝 Contribuciones
¡Las contribuciones son siempre bienvenidas, pero por favor:
1.  **Fork** el proyecto
2.  **Crea** una rama para tu feature
3.  **Commit** tus cambios  
4.  **Push** a la rama
5.  **Abre** un Pull Request

---

<div align="center">

**⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub ⭐**

[![GitHub stars](https://img.shields.io/github/stars/tu_usuario/network-analyzer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/tu_usuario/network-analyzer/stargazers/)

*Desarrollado con ❤️ para todos aquellos interesados en el área de la Ciberseguridad*

</div>

---
