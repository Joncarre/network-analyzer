# Benchmarks del Network Analyzer

Scripts para medir el rendimiento del Network Analyzer y generar gráficos de performance.

## Scripts Disponibles

### `benchmark_processing.py`
Mide el rendimiento del procesamiento de archivos PCAP.
- **Información que muestra**: Tiempo de procesamiento, throughput en paquetes/segundo y MB/segundo
- **Ejecución**: `python benchmark_processing.py [iteraciones]`

### `benchmark_api.py`
Evalúa el rendimiento de los endpoints de la API REST.
- **Información que muestra**: Tiempo de respuesta, requests por segundo (RPS), tasa de éxito
- **Ejecución**: `python benchmark_api.py [url]`

### `benchmark_database.py`
Mide el rendimiento de las operaciones de base de datos SQLite.
- **Información que muestra**: Tiempo de respuesta de queries, rendimiento de escritura
- **Ejecución**: `python benchmark_database.py [iteraciones]`

### `run_benchmarks.py`
Ejecuta todos los benchmarks y genera gráficos automáticamente.
- **Información que muestra**: Reporte HTML consolidado con todas las métricas y gráficos
- **Ejecución**: `python run_benchmarks.py`

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales**: matplotlib, pandas, seaborn, numpy, requests

## Ejemplos de Uso

```bash
# Ejecutar todos los benchmarks
python run_benchmarks.py

# Benchmark de procesamiento con 5 iteraciones
python benchmark_processing.py 5

# Benchmark de API con URL personalizada
python benchmark_api.py http://localhost:8000

# Benchmark de base de datos con 20 iteraciones
python benchmark_database.py 20
```

## Archivos Generados

- Archivos JSON con resultados: `benchmark_[tipo]_[fecha]_[hora].json`
- Gráficos en directorio `results/`: throughput, tiempos de respuesta, performance
- Reporte HTML: `results/benchmark_report.html`
