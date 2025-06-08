# Network Analyzer 🌐🔍

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 **Herramienta completa para captura, análisis y visualización de tráfico de red con IA**

Network Analyzer es una solución moderna y potente que combina tecnologías avanzadas de backend para la captura de paquetes con una interfaz web intuitiva y accesible. Perfecta para **profesionales de seguridad**, **administradores de red** y **estudiantes** que desean comprender y analizar el tráfico de red de manera eficiente.

## 🎯 ¿Qué hace Network Analyzer?

✨ **Captura paquetes de red** en tiempo real desde cualquier interfaz  
🧠 **Analiza con IA** el tráfico usando consultas en lenguaje natural  
📊 **Visualiza estadísticas** detalladas y comportamientos de red  
🛡️ **Detecta anomalías** y posibles amenazas automáticamente  
💾 **Almacena datos** estructuradamente para análisis posteriores  
🗣️ **Interactúa conversacionalmente** para explorar los resultados

## 🏗️ Arquitectura del Proyecto

El proyecto está construido con una **arquitectura moderna de microservicios** dividida en dos componentes principales:

### 🐍 Backend (Python/FastAPI)
> **El cerebro del sistema** - Maneja toda la lógica de procesamiento y análisis

| Módulo | Descripción | Tecnología |
|--------|-------------|------------|
| 📡 **Captura** | Interfaces con TShark para captura de paquetes | TShark/Wireshark |
| ⚙️ **Procesamiento** | Convierte archivos PCAP a estructuras analizables | Pandas/Python |
| 🗄️ **Base de datos** | Almacenamiento SQLite de sesiones y anomalías | SQLite |
| 🔌 **API REST** | Endpoints para todas las funcionalidades | FastAPI |
| 🤖 **Integración IA** | Conexión con Claude AI para análisis inteligente | Anthropic Claude |

### ⚛️ Frontend (React)
> **La cara amigable** - Interfaz visual moderna y responsiva

| Componente | Función | Tecnología |
|------------|---------|------------|
| 🎨 **Interfaz visual** | Diseño moderno y responsivo | React + TailwindCSS |
| 📥 **Captura** | Panel para iniciar capturas o subir PCAPs | React Components |
| 📊 **Análisis** | Visualización de paquetes y estadísticas | Chart.js |
| 💬 **Chat IA** | Interfaz conversacional para consultas | WebSocket + React |

## ✨ Funcionalidades Principales

> 🔥 **¡Todo lo que necesitas para análisis de red profesional!**

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

> ⚡ **Configuración mínima recomendada**

| Componente | Requisito | Versión Mínima | Recomendado |
|------------|-----------|----------------|-------------|
| 🐍 **Python** | Intérprete Python | 3.8+ | 3.10+ |
| 🟢 **Node.js** | Runtime JavaScript | 14.x+ | 18.x+ |
| 🦈 **TShark** | Analizador de paquetes | Última | Wireshark suite |
| 🌐 **Interfaz de red** | Acceso a adaptadores | Requerido | Permisos admin |
| 💾 **Memoria RAM** | Para procesamiento | 4GB+ | 8GB+ |
| 💿 **Espacio en disco** | Para almacenamiento | 1GB+ | 10GB+ |

## 🛠️ Instalación y Configuración

> 🚀 **¡Puesta en marcha en menos de 10 minutos!**

### 📥 Paso 1: Obtener el Código

```bash
# Clona el repositorio
git clone https://github.com/tu_usuario/network-analyzer.git
cd network-analyzer
```

### 🐍 Paso 2: Configurar el Backend

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

### ⚛️ Paso 3: Configurar el Frontend

```bash
# Navegar al directorio del frontend
cd ../frontend

# Instalar dependencias
npm install
```

## 🚀 Cómo Usar Network Analyzer

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

### 🎮 Modos de Uso

<details>
<summary><strong>🔴 Captura en Tiempo Real</strong></summary>

1. Ve a la sección **"Captura"**
2. Selecciona tu **interfaz de red**
3. Configura **duración** y **filtros**
4. Haz clic en **"Iniciar Captura"**
5. Observa los paquetes en tiempo real
</details>

<details>
<summary><strong>📁 Análisis de Archivo PCAP</strong></summary>

1. Ve a la sección **"Captura"**
2. Haz clic en **"Subir archivo PCAP"**
3. Selecciona tu archivo desde el disco
4. Espera a que se procese automáticamente
5. Explora los resultados en **"Análisis"**
</details>

## 🧪 Casos de Uso y Tipos de Pruebas

> 🎯 **Descubre todo lo que puedes hacer con Network Analyzer**

### 🔬 Análisis Básico
| Tipo | Descripción | Ideal para |
|------|-------------|-----------|
| **📊 Captura básica** | Monitoreo de tráfico durante tiempo determinado | Administradores de red |
| **🔍 Exploración general** | Análisis panorámico de protocolos y comunicaciones | Estudiantes y principiantes |
| **📈 Métricas de rendimiento** | Volúmenes, distribución de protocolos, tiempos | Optimización de red |

### 🛡️ Seguridad y Amenazas
| Tipo | Descripción | Ideal para |
|------|-------------|-----------|
| **🚨 Detección de vulnerabilidades** | Identificación de patrones y anomalías sospechosas | Profesionales de ciberseguridad |
| **🕵️ Análisis forense** | Investigación detallada de incidentes de seguridad | Equipos de respuesta a incidentes |
| **🎯 Detección de intrusiones** | Identificación de escaneos y actividad maliciosa | SOCs y equipos de seguridad |

### 🔬 Investigación Avanzada
| Tipo | Descripción | Ideal para |
|------|-------------|-----------|
| **🧪 Comportamientos anómalos** | Análisis de tráfico inusual o fuera de patrones | Investigadores de seguridad |
| **🔍 Investigación específica** | Filtrado y consultas dirigidas mediante IA | Analistas especializados |
| **📊 Análisis de tendencias** | Patrones temporales y correlaciones complejas | Data scientists |

## 💬 Ejemplos de Consultas Inteligentes

> 🤖 **Pregúntale cualquier cosa a tu IA asistente**

### 🔍 Consultas Básicas
```
💭 "¿Cuáles son los protocolos más utilizados en esta captura?"
💭 "¿Qué IPs han generado más tráfico?"
💭 "Muéstrame un resumen de la actividad de red"
💭 "¿Cuántos paquetes se capturaron en total?"
```

### 🛡️ Análisis de Seguridad
```
🚨 "¿Hay indicios de escaneos de puertos en esta sesión?"
🚨 "¿Puedes identificar alguna actividad sospechosa?"
🚨 "¿Hay patrones de comunicación anómalos?"
🚨 "¿Detectas algún intento de intrusión?"
```

### 📊 Análisis Estadístico
```
📈 "¿Cuáles son las comunicaciones más frecuentes entre hosts?"
📈 "¿Qué puertos están siendo más utilizados?"
📈 "¿Hay algún pico de tráfico inusual?"
📈 "Analiza la distribución de protocolos por tiempo"
```

### 🔬 Investigación Forense
```
🕵️ "¿Qué hizo la IP 192.168.1.100 durante la captura?"
🕵️ "¿Hay transferencias de archivos sospechosas?"
🕵️ "¿Qué dispositivos se conectaron durante este período?"
🕵️ "Analiza las conexiones salientes no autorizadas"
```

## 🔧 Resolución de Problemas

> 🚑 **Soluciones rápidas a problemas comunes**

### ❌ Problemas de Instalación

<details>
<summary><strong>🐍 Error con dependencias de Python</strong></summary>

**Problema:** Fallos durante `pip install -r requirements.txt`
```bash
# Soluciones:
1. Actualizar pip: python -m pip install --upgrade pip
2. Instalar individualmente: pip install fastapi uvicorn pandas
3. Usar virtual environment: python -m venv venv && source venv/bin/activate
```
</details>

<details>
<summary><strong>🟢 Error con dependencias de Node.js</strong></summary>

**Problema:** Fallos durante `npm install`
```bash
# Soluciones:
1. Limpiar cache: npm cache clean --force
2. Eliminar node_modules: rm -rf node_modules && npm install
3. Usar yarn: yarn install
```
</details>

### 🔌 Problemas de Conectividad

<details>
<summary><strong>🦈 TShark no encontrado</strong></summary>

**Problema:** Error "TShark not found" o similar

**Soluciones:**
- **Windows:** Instalar Wireshark desde [wireshark.org](https://wireshark.org)
- **Linux:** `sudo apt install tshark` o `sudo yum install wireshark`
- **macOS:** `brew install wireshark`
- Verificar: `tshark --version`
</details>

<details>
<summary><strong>🔐 Problemas de permisos</strong></summary>

**Problema:** Sin acceso a interfaces de red

**Soluciones:**
- **Windows:** Ejecutar como administrador
- **Linux/macOS:** `sudo python run.py` o configurar permisos de captura
- Verificar interfaces: `tshark -D`
</details>

### 🤖 Problemas con IA

<details>
<summary><strong>🔑 Error de API Key</strong></summary>

**Problema:** "Invalid API key" o "Authentication failed"

**Soluciones:**
1. Verificar clave en archivo `.env`
2. Regenerar API key en [Anthropic Console](https://console.anthropic.com)
3. Comprobar formato: `ANTHROPIC_API_KEY=sk-...`
</details>

### 📞 ¿Necesitas Más Ayuda?

Si los problemas persisten:
1. 📧 **Email:** jonathan.carrero@alumnos.ui1.es
2. 📋 **Issues:** Abre un issue en GitHub con detalles del error
3. 📚 **Logs:** Incluye siempre los logs completos del error

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT** - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto y Soporte

> 💬 **¡Estamos aquí para ayudarte!**

### 👨‍💼 Desarrollador Principal
**Jonathan Carrero**  
📧 **Email:** jonathan.carrero@alumnos.ui1.es  
🎓 **Institución:** Universidad Isabel I  

### 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Por favor:
1. 🍴 **Fork** el proyecto
2. 🌟 **Crea** una rama para tu feature
3. 💾 **Commit** tus cambios  
4. 📤 **Push** a la rama
5. 📝 **Abre** un Pull Request

### 🐛 Reportar Bugs
Encontraste un problema? Ayúdanos a mejorarlo:
- 📋 **Issues:** [GitHub Issues](https://github.com/tu_usuario/network-analyzer/issues)
- 📧 **Email directo:** Para problemas críticos o dudas específicas

---

<div align="center">

**⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub ⭐**

[![GitHub stars](https://img.shields.io/github/stars/tu_usuario/network-analyzer.svg?style=social&label=Star&maxAge=2592000)](https://github.com/tu_usuario/network-analyzer/stargazers/)

*Desarrollado con ❤️ para la comunidad de análisis de red*

</div>

---
