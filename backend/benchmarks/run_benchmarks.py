#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los benchmarks y generar gráficos de rendimiento
"""

import os
import sys
import json
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
import numpy as np

class BenchmarkRunner:
    def __init__(self):
        self.benchmark_dir = os.path.dirname(os.path.abspath(__file__))
        self.results_dir = os.path.join(self.benchmark_dir, 'results')
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Configurar estilo de gráficos
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
    
    def run_processing_benchmark(self, iterations=3):
        """Ejecuta el benchmark de procesamiento"""
        print("🔄 Ejecutando benchmark de procesamiento PCAP...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.benchmark_dir, 'benchmark_processing.py'),
                str(iterations)
            ], capture_output=True, text=True, cwd=self.benchmark_dir)
            
            if result.returncode == 0:
                print("✅ Benchmark de procesamiento completado")
                return True
            else:
                print(f"❌ Error en benchmark de procesamiento: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando benchmark de procesamiento: {e}")
            return False
    
    def run_api_benchmark(self, base_url="http://localhost:8000"):
        """Ejecuta el benchmark de API"""
        print("🔄 Ejecutando benchmark de API REST...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.benchmark_dir, 'benchmark_api.py'),
                base_url
            ], capture_output=True, text=True, cwd=self.benchmark_dir)
            
            if result.returncode == 0:
                print("✅ Benchmark de API completado")
                return True
            else:
                print(f"❌ Error en benchmark de API: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando benchmark de API: {e}")
            return False
    
    def run_database_benchmark(self, iterations=10):
        """Ejecuta el benchmark de base de datos"""
        print("🔄 Ejecutando benchmark de base de datos...")
        
        try:
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.benchmark_dir, 'benchmark_database.py'),
                str(iterations)
            ], capture_output=True, text=True, cwd=self.benchmark_dir)
            
            if result.returncode == 0:
                print("✅ Benchmark de base de datos completado")
                return True
            else:
                print(f"❌ Error en benchmark de base de datos: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando benchmark de base de datos: {e}")
            return False
    
    def find_latest_results(self):
        """Encuentra los archivos de resultados más recientes"""
        result_files = {
            'processing': None,
            'api': None,
            'database': None
        }
        
        for file in os.listdir(self.benchmark_dir):
            if file.startswith('benchmark_processing_') and file.endswith('.json'):
                if not result_files['processing'] or file > result_files['processing']:
                    result_files['processing'] = file
            elif file.startswith('benchmark_api_') and file.endswith('.json'):
                if not result_files['api'] or file > result_files['api']:
                    result_files['api'] = file
            elif file.startswith('benchmark_database_') and file.endswith('.json'):
                if not result_files['database'] or file > result_files['database']:
                    result_files['database'] = file
        
        return result_files
    
    def load_results(self, result_files):
        """Carga los resultados de los archivos JSON"""
        results = {}
        
        for benchmark_type, filename in result_files.items():
            if filename:
                try:
                    with open(os.path.join(self.benchmark_dir, filename), 'r') as f:
                        results[benchmark_type] = json.load(f)
                except Exception as e:
                    print(f"Error cargando {filename}: {e}")
        
        return results
    
    def create_processing_graphs(self, processing_data):
        """Crea gráficos para el benchmark de procesamiento"""
        if 'results' not in processing_data or not processing_data['results']:
            return
        
        results = processing_data['results']
        
        # Gráfico de throughput por archivo
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        files = [r['file'] for r in results]
        throughput_packets = [r['throughput_packets_per_second'] for r in results]
        throughput_mb = [r['throughput_mb_per_second'] for r in results]
        
        ax1.bar(files, throughput_packets, color='skyblue', alpha=0.8)
        ax1.set_title('Throughput - Paquetes por Segundo')
        ax1.set_ylabel('Paquetes/s')
        ax1.tick_params(axis='x', rotation=45)
        
        ax2.bar(files, throughput_mb, color='lightcoral', alpha=0.8)
        ax2.set_title('Throughput - MB por Segundo')
        ax2.set_ylabel('MB/s')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'processing_throughput.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico de tiempos de procesamiento
        fig, ax = plt.subplots(figsize=(12, 6))
        
        file_sizes = [r['file_size_mb'] for r in results]
        processing_times = [r['avg_time_seconds'] for r in results]
        
        scatter = ax.scatter(file_sizes, processing_times, s=100, alpha=0.7, c=range(len(files)), cmap='viridis')
        
        for i, file in enumerate(files):
            ax.annotate(file, (file_sizes[i], processing_times[i]), 
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax.set_xlabel('Tamaño del archivo (MB)')
        ax.set_ylabel('Tiempo de procesamiento (s)')
        ax.set_title('Relación Tamaño vs Tiempo de Procesamiento')
        ax.grid(True, alpha=0.3)
        
        plt.colorbar(scatter, label='Archivo')
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'processing_time_vs_size.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_api_graphs(self, api_data):
        """Crea gráficos para el benchmark de API"""
        if 'results' not in api_data or not api_data['results']:
            return
        
        # Filtrar solo los resultados de endpoints normales (no concurrentes)
        endpoint_results = [r for r in api_data['results'] if r.get('test_type') != 'concurrent']
        
        if not endpoint_results:
            return
        
        # Gráfico de tiempos de respuesta
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        endpoints = [r['endpoint'] for r in endpoint_results]
        response_times = [r['avg_response_time'] * 1000 for r in endpoint_results]  # Convertir a ms
        success_rates = [r['success_rate'] * 100 for r in endpoint_results]
        
        ax1.barh(endpoints, response_times, color='lightgreen', alpha=0.8)
        ax1.set_title('Tiempo de Respuesta Promedio')
        ax1.set_xlabel('Tiempo (ms)')
        
        ax2.barh(endpoints, success_rates, color='gold', alpha=0.8)
        ax2.set_title('Tasa de Éxito')
        ax2.set_xlabel('Porcentaje (%)')
        ax2.set_xlim(0, 100)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'api_performance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico de requests por segundo
        fig, ax = plt.subplots(figsize=(12, 6))
        
        rps_values = [r['requests_per_second'] for r in endpoint_results]
        
        bars = ax.bar(endpoints, rps_values, color='mediumpurple', alpha=0.8)
        ax.set_title('Requests por Segundo por Endpoint')
        ax.set_ylabel('RPS')
        ax.tick_params(axis='x', rotation=45)
        
        # Añadir valores encima de las barras
        for bar, rps in zip(bars, rps_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{rps:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'api_rps.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_database_graphs(self, db_data):
        """Crea gráficos para el benchmark de base de datos"""
        if 'results' not in db_data or not db_data['results']:
            return
        
        # Separar resultados de queries y escritura
        query_results = [r for r in db_data['results'] if 'database' in r]
        write_results = [r for r in db_data['results'] if r.get('test_type') == 'write_performance']
        
        # Gráfico de rendimiento de queries
        if query_results:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            all_queries = []
            all_times = []
            all_databases = []
            
            for db_result in query_results:
                db_name = db_result['database']
                for query_result in db_result['query_results']:
                    all_queries.append(query_result['query_name'])
                    all_times.append(query_result['avg_time_seconds'] * 1000)  # ms
                    all_databases.append(db_name)
            
            if all_queries:
                # Crear DataFrame para mejor manejo
                df = pd.DataFrame({
                    'Query': all_queries,
                    'Time_ms': all_times,
                    'Database': all_databases
                })
                
                # Gráfico de barras agrupadas si hay múltiples DBs
                unique_queries = df['Query'].unique()
                unique_dbs = df['Database'].unique()
                
                if len(unique_dbs) > 1:
                    pivot_df = df.pivot(index='Query', columns='Database', values='Time_ms')
                    pivot_df.plot(kind='bar', ax=ax, alpha=0.8)
                else:
                    ax.bar(df['Query'], df['Time_ms'], alpha=0.8, color='lightblue')
                
                ax.set_title('Tiempo de Respuesta de Queries')
                ax.set_ylabel('Tiempo (ms)')
                ax.tick_params(axis='x', rotation=45)
                ax.legend()
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.results_dir, 'database_query_performance.png'), dpi=300, bbox_inches='tight')
                plt.close()
        
        # Gráfico de rendimiento de escritura
        if write_results:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            write_result = write_results[0]  # Tomar el primero
            categories = ['Inserción\nIndividual', 'Inserción\nen Lote']
            values = [
                write_result['individual_insert']['inserts_per_second'],
                write_result['batch_insert']['inserts_per_second']
            ]
            
            bars = ax.bar(categories, values, color=['orange', 'green'], alpha=0.8)
            ax.set_title('Rendimiento de Escritura en Base de Datos')
            ax.set_ylabel('Inserciones por Segundo')
            
            # Añadir valores encima de las barras
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + value*0.01,
                       f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.results_dir, 'database_write_performance.png'), dpi=300, bbox_inches='tight')
            plt.close()
    
    def create_summary_report(self, results):
        """Crea un reporte resumen HTML"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Network Analyzer - Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        img {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; }}
        .graphs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .graphs {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <h1>Network Analyzer - Reporte de Rendimiento</h1>
    <p><strong>Fecha del benchmark:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="summary">
        <h2>Resumen Ejecutivo</h2>
"""
        
        # Agregar métricas clave si están disponibles
        if 'processing' in results:
            processing_results = results['processing'].get('results', [])
            if processing_results:
                avg_throughput = np.mean([r['throughput_packets_per_second'] for r in processing_results])
                html_content += f"""
        <div class="metric">
            <div class="metric-value">{avg_throughput:.0f}</div>
            <div class="metric-label">Paquetes/s<br>(Promedio)</div>
        </div>
"""
        
        if 'api' in results:
            api_results = [r for r in results['api'].get('results', []) if r.get('test_type') != 'concurrent']
            if api_results:
                avg_response = np.mean([r['avg_response_time'] for r in api_results]) * 1000
                html_content += f"""
        <div class="metric">
            <div class="metric-value">{avg_response:.1f}</div>
            <div class="metric-label">ms<br>(Respuesta API)</div>
        </div>
"""
        
        html_content += """
    </div>
    
    <h2>Gráficos de Rendimiento</h2>
    <div class="graphs">
"""
        
        # Agregar imágenes de gráficos
        graph_files = [
            ('processing_throughput.png', 'Throughput de Procesamiento PCAP'),
            ('processing_time_vs_size.png', 'Tiempo vs Tamaño de Archivo'),
            ('api_performance.png', 'Rendimiento de API'),
            ('api_rps.png', 'Requests por Segundo'),
            ('database_query_performance.png', 'Rendimiento de Queries'),
            ('database_write_performance.png', 'Rendimiento de Escritura')
        ]
        
        for graph_file, title in graph_files:
            graph_path = os.path.join(self.results_dir, graph_file)
            if os.path.exists(graph_path):
                html_content += f"""
        <div>
            <h3>{title}</h3>
            <img src="{graph_file}" alt="{title}">
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # Guardar reporte HTML
        report_path = os.path.join(self.results_dir, 'benchmark_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Reporte HTML generado: {report_path}")
        return report_path
    
    def run_all_benchmarks(self, processing_iterations=3, api_url="http://localhost:8000", db_iterations=10):
        """Ejecuta todos los benchmarks y genera gráficos"""
        print("🚀 EJECUTANDO SUITE COMPLETA DE BENCHMARKS")
        print("=" * 50)
        
        # Ejecutar benchmarks
        success_count = 0
        
        if self.run_processing_benchmark(processing_iterations):
            success_count += 1
        
        if self.run_api_benchmark(api_url):
            success_count += 1
        
        if self.run_database_benchmark(db_iterations):
            success_count += 1
        
        print(f"\n📈 Benchmarks completados: {success_count}/3")
        
        # Generar gráficos
        print("\n🎨 Generando gráficos de rendimiento...")
        
        result_files = self.find_latest_results()
        results = self.load_results(result_files)
        
        if 'processing' in results:
            self.create_processing_graphs(results['processing'])
            print("✅ Gráficos de procesamiento generados")
        
        if 'api' in results:
            self.create_api_graphs(results['api'])
            print("✅ Gráficos de API generados")
        
        if 'database' in results:
            self.create_database_graphs(results['database'])
            print("✅ Gráficos de base de datos generados")
        
        # Generar reporte HTML
        report_path = self.create_summary_report(results)
        
        print(f"\n🎉 Suite de benchmarks completada!")
        print(f"📁 Resultados en: {self.results_dir}")
        print(f"📊 Reporte: {report_path}")
        
        return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecuta suite completa de benchmarks')
    parser.add_argument('--processing-iterations', type=int, default=3, help='Iteraciones para benchmark de procesamiento')
    parser.add_argument('--api-url', default='http://localhost:8000', help='URL base de la API')
    parser.add_argument('--db-iterations', type=int, default=10, help='Iteraciones para benchmark de base de datos')
    parser.add_argument('--skip-processing', action='store_true', help='Saltar benchmark de procesamiento')
    parser.add_argument('--skip-api', action='store_true', help='Saltar benchmark de API')
    parser.add_argument('--skip-database', action='store_true', help='Saltar benchmark de base de datos')
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    
    if args.skip_processing and args.skip_api and args.skip_database:
        print("❌ No se puede saltar todos los benchmarks")
        sys.exit(1)
    
    # Modificar el runner para saltar benchmarks si se especifica
    if not args.skip_processing or not args.skip_api or not args.skip_database:
        runner.run_all_benchmarks(
            processing_iterations=args.processing_iterations,
            api_url=args.api_url,
            db_iterations=args.db_iterations
        )
    else:
        # Solo generar gráficos de resultados existentes
        print("🎨 Generando gráficos de resultados existentes...")
        result_files = runner.find_latest_results()
        results = runner.load_results(result_files)
        
        if results:
            if 'processing' in results:
                runner.create_processing_graphs(results['processing'])
            if 'api' in results:
                runner.create_api_graphs(results['api'])
            if 'database' in results:
                runner.create_database_graphs(results['database'])
            
            runner.create_summary_report(results)
            print("✅ Gráficos regenerados")
        else:
            print("❌ No se encontraron resultados previos")
