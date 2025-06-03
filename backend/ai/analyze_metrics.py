#!/usr/bin/env python3
"""
Script para analizar métricas históricas de Claude AI
Permite visualizar y analizar el uso de la API a lo largo del tiempo
"""

import json
import os
import glob
from datetime import datetime
from typing import List, Dict
import argparse

def load_metrics_files(directory: str = None) -> List[Dict]:
    """Carga todos los archivos de métricas disponibles"""
    if directory is None:
        directory = os.path.dirname(__file__)
    
    pattern = os.path.join(directory, "claude_metrics_*.json")
    files = glob.glob(pattern)
    
    metrics_data = []
    for file_path in sorted(files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['file_path'] = file_path
                metrics_data.append(data)
        except Exception as e:
            print(f"Error al cargar {file_path}: {e}")
    
    return metrics_data

def print_session_list(metrics_data: List[Dict]):
    """Muestra una lista de todas las sesiones disponibles"""
    print("\n📋 Sesiones disponibles:")
    print("-" * 80)
    
    for i, session in enumerate(metrics_data, 1):
        session_info = session.get('session_info', {})
        session_summary = session.get('session_summary', {})
        queries = session.get('queries', [])
        
        start_time = session_info.get('session_start', 'N/A')
        total_queries = len(queries)
        total_cost = session_summary.get('total_cost_usd', 0)
        total_tokens = session_summary.get('total_tokens', 0)
        
        # Formatear fecha
        try:
            dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            date_str = start_time
        
        print(f"{i:2d}. {date_str} | {total_queries:3d} consultas | {total_tokens:6,} tokens | ${total_cost:.6f}")
    
    print("-" * 80)

def print_detailed_session(session_data: Dict):
    """Muestra información detallada de una sesión"""
    session_info = session_data.get('session_info', {})
    session_summary = session_data.get('session_summary', {})
    queries = session_data.get('queries', [])
    
    print(f"\n📊 Análisis detallado de la sesión")
    print("=" * 60)
    
    # Información general
    start_time = session_info.get('session_start', 'N/A')
    try:
        dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        date_str = start_time
    
    print(f"📅 Fecha: {date_str}")
    print(f"🤖 Modelo: {session_info.get('model', 'N/A')}")
    print(f"📁 Archivo: {os.path.basename(session_data.get('file_path', 'N/A'))}")
    
    # Resumen de la sesión
    if session_summary:
        print(f"\n📈 Resumen de la sesión:")
        print(f"   📝 Total de consultas: {session_summary.get('total_queries', 0)}")
        print(f"   🔢 Tokens de entrada: {session_summary.get('total_input_tokens', 0):,}")
        print(f"   🔢 Tokens de salida: {session_summary.get('total_output_tokens', 0):,}")
        print(f"   🔢 Tokens totales: {session_summary.get('total_tokens', 0):,}")
        print(f"   ⏱️  Tiempo total: {session_summary.get('total_response_time_ms', 0)/1000:.1f} segundos")
        print(f"   💰 Costo total: ${session_summary.get('total_cost_usd', 0):.6f}")
        print(f"   📊 Promedio por consulta:")
        print(f"      • {session_summary.get('avg_tokens_per_query', 0):.0f} tokens")
        print(f"      • {session_summary.get('avg_response_time_ms', 0):.0f}ms")
        print(f"      • ${session_summary.get('avg_cost_per_query_usd', 0):.6f}")
    
    # Análisis de consultas individuales
    if queries:
        print(f"\n📋 Consultas individuales:")
        print("-" * 60)
        for i, query in enumerate(queries, 1):
            timestamp = query.get('timestamp', 'N/A')
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%H:%M:%S')
            except:
                time_str = timestamp
            
            input_tokens = query.get('input_tokens', 0)
            output_tokens = query.get('output_tokens', 0)
            total_tokens = query.get('total_tokens', 0)
            response_time = query.get('response_time_ms', 0)
            cost = query.get('total_cost_usd', 0)
            
            print(f"{i:2d}. {time_str} | {input_tokens:4d}+{output_tokens:4d}={total_tokens:4d} tokens | {response_time:5.0f}ms | ${cost:.6f}")

def print_aggregate_stats(metrics_data: List[Dict]):
    """Muestra estadísticas agregadas de todas las sesiones"""
    if not metrics_data:
        print("No hay datos de métricas disponibles.")
        return
    
    print(f"\n📊 Estadísticas agregadas ({len(metrics_data)} sesiones)")
    print("=" * 60)
    
    total_sessions = len(metrics_data)
    total_queries = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    total_time = 0.0
    
    earliest_session = None
    latest_session = None
    
    for session in metrics_data:
        session_summary = session.get('session_summary', {})
        session_info = session.get('session_info', {})
        
        queries_count = session_summary.get('total_queries', 0)
        total_queries += queries_count
        total_input_tokens += session_summary.get('total_input_tokens', 0)
        total_output_tokens += session_summary.get('total_output_tokens', 0)
        total_cost += session_summary.get('total_cost_usd', 0)
        total_time += session_summary.get('total_response_time_ms', 0) / 1000
        
        # Fechas
        start_time = session_info.get('session_start')
        if start_time:
            if earliest_session is None or start_time < earliest_session:
                earliest_session = start_time
            if latest_session is None or start_time > latest_session:
                latest_session = start_time
    
    # Formatear fechas
    try:
        earliest_dt = datetime.fromisoformat(earliest_session.replace('Z', '+00:00'))
        earliest_str = earliest_dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        earliest_str = earliest_session or 'N/A'
    
    try:
        latest_dt = datetime.fromisoformat(latest_session.replace('Z', '+00:00'))
        latest_str = latest_dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        latest_str = latest_session or 'N/A'
    
    total_tokens = total_input_tokens + total_output_tokens
    
    print(f"📅 Periodo: {earliest_str} - {latest_str}")
    print(f"📝 Total de sesiones: {total_sessions}")
    print(f"📝 Total de consultas: {total_queries:,}")
    print(f"🔢 Total de tokens: {total_tokens:,} ({total_input_tokens:,} entrada + {total_output_tokens:,} salida)")
    print(f"⏱️  Tiempo total: {total_time:.1f} segundos")
    print(f"💰 Costo total: ${total_cost:.6f}")
    
    if total_queries > 0:
        print(f"\n📊 Promedios:")
        print(f"   • {total_queries/total_sessions:.1f} consultas por sesión")
        print(f"   • {total_tokens/total_queries:.0f} tokens por consulta")
        print(f"   • {total_time*1000/total_queries:.0f}ms por consulta")
        print(f"   • ${total_cost/total_queries:.6f} por consulta")
    
    # Distribución de tokens
    if total_tokens > 0:
        input_percentage = (total_input_tokens / total_tokens) * 100
        output_percentage = (total_output_tokens / total_tokens) * 100
        print(f"\n🔢 Distribución de tokens:")
        print(f"   • Entrada: {input_percentage:.1f}%")
        print(f"   • Salida: {output_percentage:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Analizador de métricas de Claude AI')
    parser.add_argument('--list', '-l', action='store_true', help='Lista todas las sesiones disponibles')
    parser.add_argument('--session', '-s', type=int, help='Muestra detalles de una sesión específica (número)')
    parser.add_argument('--aggregate', '-a', action='store_true', help='Muestra estadísticas agregadas')
    parser.add_argument('--directory', '-d', type=str, help='Directorio donde buscar archivos de métricas')
    
    args = parser.parse_args()
    
    # Cargar datos de métricas
    metrics_data = load_metrics_files(args.directory)
    
    if not metrics_data:
        print("❌ No se encontraron archivos de métricas.")
        print("   Asegúrate de haber ejecutado consultas con Claude AI primero.")
        return
    
    if args.list:
        print_session_list(metrics_data)
    elif args.session:
        if 1 <= args.session <= len(metrics_data):
            print_detailed_session(metrics_data[args.session - 1])
        else:
            print(f"❌ Sesión {args.session} no encontrada. Usa --list para ver sesiones disponibles.")
    elif args.aggregate:
        print_aggregate_stats(metrics_data)
    else:
        # Comportamiento por defecto: mostrar todo
        print_session_list(metrics_data)
        print_aggregate_stats(metrics_data)

if __name__ == "__main__":
    main()
