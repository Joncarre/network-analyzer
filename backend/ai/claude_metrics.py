import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class QueryMetrics:
    """Métricas de una consulta individual"""
    timestamp: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    response_time_ms: float
    tokens_per_second: float
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    model: str
    user_question_length: int
    response_length: int

@dataclass
class SessionMetrics:
    """Métricas acumuladas de toda la sesión"""
    session_start: str
    total_queries: int
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_response_time_ms: float
    total_cost_usd: float
    avg_tokens_per_query: float
    avg_response_time_ms: float
    avg_cost_per_query_usd: float

class ClaudeMetrics:
    """Clase para capturar y almacenar métricas de uso de Claude API"""
    
    # Precios de Claude 3 Opus (por millón de tokens)
    INPUT_COST_PER_MILLION = 15.0    # $15 por millón de tokens de entrada
    OUTPUT_COST_PER_MILLION = 75.0   # $75 por millón de tokens de salida
    
    def __init__(self, metrics_file_path: str = None):
        """Inicializa el sistema de métricas"""
        if metrics_file_path is None:
            # Crear archivo en el directorio ai/ con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file_path = os.path.join(
                os.path.dirname(__file__), 
                f"claude_metrics_{timestamp}.json"
            )
        
        self.metrics_file = metrics_file_path
        self.session_start = datetime.now().isoformat()
        self.queries = []
        
        # Crear archivo si no existe
        self._initialize_metrics_file()
    
    def _initialize_metrics_file(self):
        """Inicializa el archivo de métricas"""
        try:
            if not os.path.exists(self.metrics_file):
                initial_data = {
                    "session_info": {
                        "session_start": self.session_start,
                        "model": "claude-3-opus-20240229",
                        "pricing": {
                            "input_cost_per_million_tokens": self.INPUT_COST_PER_MILLION,
                            "output_cost_per_million_tokens": self.OUTPUT_COST_PER_MILLION
                        }
                    },
                    "queries": [],
                    "session_summary": {}
                }
                with open(self.metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: No se pudo inicializar archivo de métricas: {e}")
    
    def calculate_costs(self, input_tokens: int, output_tokens: int) -> tuple:
        """Calcula los costos basados en los tokens"""
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
        total_cost = input_cost + output_cost
        return input_cost, output_cost, total_cost
    
    def record_query(self, 
                    input_tokens: int, 
                    output_tokens: int, 
                    response_time_ms: float,
                    model: str,
                    user_question: str = "",
                    response: str = "") -> QueryMetrics:
        """Registra las métricas de una consulta"""
        try:
            # Calcular métricas
            total_tokens = input_tokens + output_tokens
            tokens_per_second = output_tokens / (response_time_ms / 1000) if response_time_ms > 0 else 0
            input_cost, output_cost, total_cost = self.calculate_costs(input_tokens, output_tokens)
            
            # Crear objeto de métricas
            metrics = QueryMetrics(
                timestamp=datetime.now().isoformat(),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                response_time_ms=response_time_ms,
                tokens_per_second=tokens_per_second,
                input_cost_usd=input_cost,
                output_cost_usd=output_cost,
                total_cost_usd=total_cost,
                model=model,
                user_question_length=len(user_question),
                response_length=len(response)
            )
            
            # Almacenar en memoria
            self.queries.append(metrics)
            
            # Guardar en archivo
            self._save_to_file(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Warning: Error al registrar métricas: {e}")
            return None
    
    def _save_to_file(self, query_metrics: QueryMetrics):
        """Guarda las métricas en el archivo JSON"""
        try:
            # Leer archivo existente
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Añadir nueva consulta
            data["queries"].append(asdict(query_metrics))
            
            # Actualizar resumen de sesión
            data["session_summary"] = asdict(self.get_session_summary())
            
            # Escribir archivo actualizado
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Error al guardar métricas en archivo: {e}")
    
    def get_session_summary(self) -> SessionMetrics:
        """Obtiene un resumen de las métricas de la sesión actual"""
        if not self.queries:
            return SessionMetrics(
                session_start=self.session_start,
                total_queries=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                total_response_time_ms=0.0,
                total_cost_usd=0.0,
                avg_tokens_per_query=0.0,
                avg_response_time_ms=0.0,
                avg_cost_per_query_usd=0.0
            )
        
        total_queries = len(self.queries)
        total_input = sum(q.input_tokens for q in self.queries)
        total_output = sum(q.output_tokens for q in self.queries)
        total_tokens = sum(q.total_tokens for q in self.queries)
        total_time = sum(q.response_time_ms for q in self.queries)
        total_cost = sum(q.total_cost_usd for q in self.queries)
        
        return SessionMetrics(
            session_start=self.session_start,
            total_queries=total_queries,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_tokens=total_tokens,
            total_response_time_ms=total_time,
            total_cost_usd=total_cost,
            avg_tokens_per_query=total_tokens / total_queries,
            avg_response_time_ms=total_time / total_queries,
            avg_cost_per_query_usd=total_cost / total_queries
        )
    
    def print_query_summary(self, metrics: QueryMetrics):
        """Imprime un resumen de la consulta actual"""
        if not metrics:
            return
            
        print(f"\n📊 Métricas de la consulta:")
        print(f"   🔢 Tokens: {metrics.input_tokens:,} entrada + {metrics.output_tokens:,} salida = {metrics.total_tokens:,} total")
        print(f"   ⌛ Tiempo: {metrics.response_time_ms:.0f}ms ({metrics.tokens_per_second:.1f} tokens/seg)")
        print(f"   💰 Costo: ${metrics.input_cost_usd:.6f} + ${metrics.output_cost_usd:.6f} = ${metrics.total_cost_usd:.6f}")
    
    def print_session_summary(self):
        """Imprime un resumen completo de la sesión"""
        summary = self.get_session_summary()
        
        print(f"\n📈 Resumen de la sesión:")
        print(f"   📝 Consultas realizadas: {summary.total_queries}")
        print(f"   🔢 Tokens totales: {summary.total_input_tokens:,} entrada + {summary.total_output_tokens:,} salida = {summary.total_tokens:,}")
        print(f"   ⌛ Tiempo total: {summary.total_response_time_ms/1000:.1f} segundos")
        print(f"   💰 Costo total: ${summary.total_cost_usd:.6f}")
        print(f"   📊 Promedios: {summary.avg_tokens_per_query:.0f} tokens/consulta, {summary.avg_response_time_ms:.0f}ms/consulta, ${summary.avg_cost_per_query_usd:.6f}/consulta")
        print(f"   📁 Métricas guardadas en: {self.metrics_file}")