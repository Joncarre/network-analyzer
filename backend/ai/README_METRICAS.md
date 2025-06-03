# Métricas de Claude AI

Este sistema de métricas captura información detallada sobre el uso de la API de Claude AI de forma completamente independiente del proyecto principal.

## Archivos del sistema de métricas:

- `claude_metrics.py` - Clase principal para capturar métricas
- `analyze_metrics.py` - Script para analizar métricas históricas
- `claude_metrics_YYYYMMDD_HHMMSS.json` - Archivos de métricas por sesión

## Métricas capturadas:

### Por consulta individual:
- **Tokens**: entrada, salida y total
- **Timing**: tiempo de respuesta en milisegundos
- **Performance**: tokens por segundo
- **Costos**: costo por tokens de entrada/salida y total
- **Metadata**: timestamp, modelo, longitud de pregunta/respuesta

### Por sesión completa:
- **Totales**: consultas, tokens, tiempo, costos
- **Promedios**: tokens por consulta, tiempo por consulta, costo por consulta
- **Distribución**: porcentaje de tokens de entrada vs salida

## Uso automático:

Las métricas se capturan automáticamente cuando usas `test_claude_ai.py`. Durante la conversación verás información como:

```
📊 Métricas de la consulta:
   🔢 Tokens: 1,234 entrada + 567 salida = 1,801 total
   ⏱️  Tiempo: 2,145ms (264.2 tokens/seg)
   💰 Costo: $0.018510 + $0.042525 = $0.061035
```

### Comandos adicionales en el chat:
- `/metricas` - Muestra resumen de métricas de la sesión actual
- `/salir` - Termina la sesión y muestra resumen final

## Análisis de métricas históricas:

Usa el script `analyze_metrics.py` para analizar datos históricos:

```bash
# Listar todas las sesiones
python ai/analyze_metrics.py --list

# Ver detalles de una sesión específica
python ai/analyze_metrics.py --session 3

# Ver estadísticas agregadas
python ai/analyze_metrics.py --aggregate

# Ver todo (comportamiento por defecto)
python ai/analyze_metrics.py
```

## Costos de Claude 3 Opus:

- **Tokens de entrada**: $15 por millón de tokens
- **Tokens de salida**: $75 por millón de tokens

## Archivo de métricas (JSON):

Cada sesión genera un archivo JSON con la estructura:

```json
{
  "session_info": {
    "session_start": "2025-06-03T18:45:23.123456",
    "model": "claude-3-opus-20240229",
    "pricing": {
      "input_cost_per_million_tokens": 15.0,
      "output_cost_per_million_tokens": 75.0
    }
  },
  "queries": [
    {
      "timestamp": "2025-06-03T18:45:30.456789",
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801,
      "response_time_ms": 2145.6,
      "tokens_per_second": 264.2,
      "input_cost_usd": 0.018510,
      "output_cost_usd": 0.042525,
      "total_cost_usd": 0.061035,
      "model": "claude-3-opus-20240229",
      "user_question_length": 89,
      "response_length": 1456
    }
  ],
  "session_summary": {
    "session_start": "2025-06-03T18:45:23.123456",
    "total_queries": 5,
    "total_input_tokens": 6789,
    "total_output_tokens": 3210,
    "total_tokens": 9999,
    "total_response_time_ms": 8765.4,
    "total_cost_usd": 0.342675,
    "avg_tokens_per_query": 1999.8,
    "avg_response_time_ms": 1753.1,
    "avg_cost_per_query_usd": 0.068535
  }
}
```

## Características de seguridad:

- **Completamente opcional**: Si falla, el chat funciona normalmente
- **Importación segura**: No afecta al proyecto si hay errores
- **Archivos separados**: No interfiere con la funcionalidad existente
- **Manejo de errores**: Todas las operaciones tienen try/except

## Desactivar métricas:

Si quieres desactivar las métricas temporalmente, puedes:

1. Pasar `enable_metrics=False` al crear `ClaudeAI()`
2. O simplemente ignorar los mensajes de métricas

Las métricas nunca interrumpen el funcionamiento normal del sistema.
