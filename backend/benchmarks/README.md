# Benchmarks del Network Analyzer

Este directorio contiene una suite completa de benchmarks para medir el rendimiento del Network Analyzer en diferentes aspectos: procesamiento de archivos PCAP, rendimiento de la API REST y operaciones de base de datos.

## 📋 Descripción de los Benchmarks

### 1. Benchmark de Procesamiento PCAP (`benchmark_processing.py`)
- **Propósito**: Mide el rendimiento del procesamiento de archivos PCAP
- **Métricas**:
  - Tiempo de procesamiento por archivo
  - Throughput en paquetes por segundo
  - Throughput en MB por segundo
  - Estadísticas por múltiples iteraciones

### 2. Benchmark de API REST (`benchmark_api.py`)
- **Propósito**: Evalúa el rendimiento de los endpoints de la API
- **Métricas**:
  - Tiempo de respuesta promedio
  - Requests por segundo (RPS)
  - Tasa de éxito
  - Rendimiento bajo carga concurrente

### 3. Benchmark de Base de Datos (`benchmark_database.py`)
- **Propósito**: Mide el rendimiento de las operaciones de base de datos SQLite
- **Métricas**:
  - Tiempo de respuesta de queries comunes
  - Rendimiento de operaciones de escritura
  - Throughput de inserción individual vs batch

### 4. Suite Completa (`run_benchmarks.py`)
- **Propósito**: Ejecuta todos los benchmarks y genera gráficos automáticamente
- **Características**:
  - Ejecución secuencial de todos los benchmarks
  - Generación automática de gráficos de rendimiento
  - Reporte HTML consolidado
  - Configuración flexible por argumentos

## 🚀 Instalación y Configuración

### Instalar Dependencias
```bash
# Desde el directorio benchmarks
pip install -r requirements.txt
```

### Dependencias Principales
- `matplotlib`: Generación de gráficos
- `pandas`: Manipulación de datos
- `seaborn`: Visualizaciones estadísticas
- `numpy`: Cálculos numéricos
- `requests`: Pruebas de API

## 📊 Uso de los Benchmarks

### Ejecutar Suite Completa (Recomendado)
```bash
# Ejecutar todos los benchmarks con configuración por defecto
python run_benchmarks.py

# Con parámetros personalizados
python run_benchmarks.py --processing-iterations 5 --api-url http://localhost:8000 --db-iterations 15

# Saltar benchmarks específicos
python run_benchmarks.py --skip-api --skip-database
```

### Ejecutar Benchmarks Individuales

#### Benchmark de Procesamiento
```bash
# Con 3 iteraciones por defecto
python benchmark_processing.py

# Con número personalizado de iteraciones
python benchmark_processing.py 5
```

#### Benchmark de API
```bash
# Con URL por defecto (localhost:8000)
python benchmark_api.py

# Con URL personalizada
python benchmark_api.py http://192.168.1.100:8000
```

#### Benchmark de Base de Datos
```bash
# Con 10 iteraciones por defecto
python benchmark_database.py

# Con número personalizado de iteraciones
python benchmark_database.py 20
```

## 📁 Estructura de Resultados

Los benchmarks generan varios tipos de archivos de salida:

### Archivos JSON de Resultados
- `benchmark_processing_YYYYMMDD_HHMMSS.json`
- `benchmark_api_YYYYMMDD_HHMMSS.json`
- `benchmark_database_YYYYMMDD_HHMMSS.json`

### Gráficos Generados (directorio `results/`)
- `processing_throughput.png`: Throughput de procesamiento PCAP
- `processing_time_vs_size.png`: Relación tiempo vs tamaño de archivo
- `api_performance.png`: Tiempos de respuesta y tasas de éxito de API
- `api_rps.png`: Requests por segundo por endpoint
- `database_query_performance.png`: Rendimiento de queries de DB
- `database_write_performance.png`: Rendimiento de escritura en DB

### Reporte HTML
- `results/benchmark_report.html`: Reporte consolidado con todas las métricas y gráficos

## 🔧 Requisitos Previos

### Para Benchmark de Procesamiento
- Archivos PCAP en `../data/pcap_files/`
- Módulo `PCAPProcessor` funcional

### Para Benchmark de API
- Servidor backend ejecutándose (por defecto en puerto 8000)
- Endpoints de API accesibles

### Para Benchmark de Base de Datos
- Archivos de base de datos SQLite en `../data/databases/`
- Esquema de BD compatible con las queries de prueba

## 📈 Interpretación de Resultados

### Métricas de Procesamiento
- **Throughput alto**: Mejor rendimiento en el procesamiento de paquetes
- **Tiempo vs Tamaño**: Relación lineal indica escalabilidad predecible
- **Consistencia**: Baja desviación estándar indica rendimiento estable

### Métricas de API
- **Tiempo de respuesta bajo**: Mejor experiencia de usuario
- **RPS alto**: Mayor capacidad de carga
- **Tasa de éxito 100%**: Estabilidad de la API

### Métricas de Base de Datos
- **Queries rápidas**: Mejor responsividad de la aplicación
- **Escritura eficiente**: Importante para captura en tiempo real
- **Escalabilidad**: Rendimiento constante con diferentes tamaños de BD

## 🎯 Casos de Uso

### Desarrollo y Optimización
- Identificar cuellos de botella en el rendimiento
- Comparar el impacto de cambios de código
- Validar optimizaciones

### Testing de Carga
- Verificar rendimiento bajo diferentes cargas de trabajo
- Planificar capacidad de hardware
- Establecer SLAs (Service Level Agreements)

### Monitoreo Continuo
- Detectar regresiones de rendimiento
- Mantener histórico de métricas
- Benchmarking antes de releases

## 🔍 Troubleshooting

### Errores Comunes

#### "No se encontraron archivos PCAP"
- Verificar que exista el directorio `../data/pcap_files/`
- Colocar archivos .pcap o .pcapng en el directorio

#### "API no disponible"
- Verificar que el backend esté ejecutándose
- Comprobar la URL y puerto correctos
- Verificar conectividad de red

#### "Error de importación de matplotlib"
- Instalar dependencias: `pip install -r requirements.txt`
- En algunas distribuciones Linux: `sudo apt-get install python3-tk`

#### "Permisos de escritura"
- Verificar permisos en el directorio actual
- El script necesita crear archivos JSON y el directorio `results/`

### Optimización de Rendimiento
- Usar SSD para mejor I/O de base de datos
- Aumentar RAM disponible para procesamiento de archivos grandes
- Considerar paralelización para múltiples archivos PCAP

## 📚 Extensión de Benchmarks

Para agregar nuevos benchmarks:

1. Crear nuevo archivo `benchmark_[nombre].py`
2. Seguir la estructura de los benchmarks existentes
3. Implementar métodos de medición y guardado de resultados
4. Agregar integración en `run_benchmarks.py`
5. Actualizar este README

### Ejemplo de Estructura de Benchmark
```python
class NewBenchmark:
    def __init__(self):
        self.results = []
    
    def benchmark_operation(self, iterations=10):
        # Implementar medición
        pass
    
    def run_benchmark(self):
        # Ejecutar todas las pruebas
        pass
    
    def save_results(self):
        # Guardar en JSON con timestamp
        pass
    
    def print_summary(self):
        # Mostrar resumen en consola
        pass
```

## 📞 Soporte

Para problemas específicos con los benchmarks:
1. Verificar los logs de salida de cada script
2. Comprobar que todos los prerequisitos estén instalados
3. Validar que los datos de prueba estén disponibles
4. Revisar los archivos JSON de resultados para más detalles

---

**Nota**: Los benchmarks están diseñados para ser no intrusivos y usar las APIs existentes del proyecto sin modificar el código principal.
