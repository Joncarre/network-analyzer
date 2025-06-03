#!/usr/bin/env python3
"""
Benchmark para medir rendimiento de operaciones de base de datos SQLite
"""

import os
import sys
import time
import json
import sqlite3
import statistics
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base, CaptureSession, Packet
from sqlalchemy import create_engine

class DatabaseBenchmark:
    def __init__(self):
        self.results = []
        self.db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'db_files')
        
    def get_database_files(self):
        """Obtiene lista de archivos de base de datos disponibles"""
        if not os.path.exists(self.db_dir):
            return []
        return [f for f in os.listdir(self.db_dir) if f.endswith('.db')]
    
    def get_database_stats(self, db_path):
        """Obtiene estadísticas básicas de la base de datos"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Contar registros en tablas principales
            stats = {}
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
              # Tamaño del archivo
            stats['file_size_mb'] = os.path.getsize(db_path) / (1024 * 1024)
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de {db_path}: {e}")
            return {}
    
    def benchmark_query_performance(self, db_path, iterations=10):
        """Benchmark de consultas comunes"""
        print(f"\n--- Benchmarking DB: {os.path.basename(db_path)} ---")
        
        stats = self.get_database_stats(db_path)
        print(f"Estadísticas DB: {stats}")
        
        queries = [
            ("SELECT COUNT(*) FROM capture_sessions", "count_sessions"),
            ("SELECT * FROM capture_sessions LIMIT 100", "select_sessions_100"),
            ("SELECT COUNT(*) FROM packets", "count_packets"),
            ("SELECT * FROM packets LIMIT 1000", "select_packets_1000"),
            ("SELECT transport_protocol, COUNT(*) FROM packets GROUP BY transport_protocol", "group_by_protocol"),
            ("SELECT src_ip, dst_ip, COUNT(*) FROM packets GROUP BY src_ip, dst_ip LIMIT 50", "group_by_ips"),
        ]
        
        db_results = {
            'database': os.path.basename(db_path),
            'database_stats': stats,
            'query_results': []
        }
        
        try:
            conn = sqlite3.connect(db_path)
            
            for query, query_name in queries:
                print(f"  Ejecutando: {query_name}")
                times = []
                row_counts = []
                
                for i in range(iterations):
                    start_time = time.time()
                    
                    try:
                        cursor = conn.cursor()
                        cursor.execute(query)
                        results = cursor.fetchall()
                        
                        end_time = time.time()
                        query_time = end_time - start_time
                        
                        times.append(query_time)
                        row_counts.append(len(results))
                        
                    except Exception as e:
                        print(f"    Error en iteración {i+1}: {e}")
                        continue
                
                if times:
                    avg_time = statistics.mean(times)
                    avg_rows = statistics.mean(row_counts)
                    
                    query_result = {
                        'query_name': query_name,
                        'query': query,
                        'iterations': len(times),
                        'avg_time_seconds': avg_time,
                        'min_time_seconds': min(times),
                        'max_time_seconds': max(times),
                        'avg_rows_returned': avg_rows,
                        'rows_per_second': avg_rows / avg_time if avg_time > 0 else 0
                    }
                    
                    db_results['query_results'].append(query_result)
                    print(f"    Promedio: {avg_time:.4f}s | Filas: {avg_rows:.0f} | Filas/s: {avg_rows/avg_time:.0f}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            return None
        
        self.results.append(db_results)
        return db_results
    
    def benchmark_write_performance(self, iterations=5):
        """Benchmark de operaciones de escritura (INSERT)"""
        print(f"\n--- Benchmark de Escritura ---")
        
        # Crear DB temporal para pruebas de escritura
        temp_db = os.path.join(self.db_dir, 'benchmark_temp.db')
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Crear tabla de prueba
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    src_ip TEXT,
                    dst_ip TEXT,
                    protocol TEXT,
                    size INTEGER,
                    data TEXT
                )
            ''')
            conn.commit()
            
            # Test de inserción individual
            individual_times = []
            for i in range(iterations):
                start_time = time.time()
                
                cursor.execute('''
                    INSERT INTO test_packets (timestamp, src_ip, dst_ip, protocol, size, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (time.time(), '192.168.1.1', '192.168.1.2', 'TCP', 1500, 'test_data'))
                conn.commit()
                
                end_time = time.time()
                individual_times.append(end_time - start_time)
            
            # Test de inserción en lote
            batch_times = []
            batch_size = 1000
            
            for i in range(3):  # Menos iteraciones para lotes
                start_time = time.time()
                
                batch_data = [
                    (time.time(), '192.168.1.1', '192.168.1.2', 'TCP', 1500, f'batch_data_{j}')
                    for j in range(batch_size)
                ]
                
                cursor.executemany('''
                    INSERT INTO test_packets (timestamp, src_ip, dst_ip, protocol, size, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', batch_data)
                conn.commit()
                
                end_time = time.time()
                batch_times.append(end_time - start_time)
            
            conn.close()
            
            # Limpiar archivo temporal
            if os.path.exists(temp_db):
                os.remove(temp_db)
            
            write_result = {
                'test_type': 'write_performance',
                'individual_insert': {
                    'iterations': len(individual_times),
                    'avg_time_seconds': statistics.mean(individual_times),
                    'inserts_per_second': 1 / statistics.mean(individual_times)
                },
                'batch_insert': {
                    'batch_size': batch_size,
                    'iterations': len(batch_times),
                    'avg_time_seconds': statistics.mean(batch_times),
                    'inserts_per_second': batch_size / statistics.mean(batch_times)
                }
            }
            
            self.results.append(write_result)
            
            print(f"  Inserción individual: {write_result['individual_insert']['inserts_per_second']:.1f} inserts/s")
            print(f"  Inserción en lote: {write_result['batch_insert']['inserts_per_second']:.1f} inserts/s")
            
            return write_result
            
        except Exception as e:
            print(f"Error en benchmark de escritura: {e}")
            return None
    
    def run_benchmark(self, iterations=10):
        """Ejecuta benchmark completo de la base de datos"""
        print("=== BENCHMARK DE BASE DE DATOS ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Crear directorio de DBs si no existe
        os.makedirs(self.db_dir, exist_ok=True)
        
        db_files = self.get_database_files()
        
        if not db_files:
            print("No se encontraron archivos de base de datos para probar")
            print(f"Directorio de DBs: {self.db_dir}")
        else:
            print(f"Bases de datos encontradas: {len(db_files)}")
            
            for db_file in db_files:
                db_path = os.path.join(self.db_dir, db_file)
                self.benchmark_query_performance(db_path, iterations)
        
        # Benchmark de escritura
        self.benchmark_write_performance()
        
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Guarda resultados en archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_database_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'benchmark_type': 'database',
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        
        print(f"\nResultados guardados en: {results_file}")
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        if not self.results:
            return
        
        print("\n=== RESUMEN DATABASE ===")
        
        for result in self.results:
            if 'database' in result:
                print(f"\nBase de datos: {result['database']}")
                print(f"{'Query':<25} {'Tiempo(s)':<12} {'Filas':<10} {'Filas/s':<10}")
                print("-" * 60)
                
                for query_result in result['query_results']:
                    name = query_result['query_name']
                    time_s = query_result['avg_time_seconds']
                    rows = query_result['avg_rows_returned']
                    rows_per_s = query_result['rows_per_second']
                    
                    print(f"{name:<25} {time_s:<12.4f} {rows:<10.0f} {rows_per_s:<10.0f}")
            
            elif result.get('test_type') == 'write_performance':
                print(f"\nRendimiento de Escritura:")
                print(f"  Inserción individual: {result['individual_insert']['inserts_per_second']:.1f} inserts/s")
                print(f"  Inserción en lote: {result['batch_insert']['inserts_per_second']:.1f} inserts/s")

if __name__ == "__main__":
    benchmark = DatabaseBenchmark()
    
    # Permitir especificar número de iteraciones
    iterations = 10
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print("Uso: python benchmark_database.py [iteraciones]")
            sys.exit(1)
    
    benchmark.run_benchmark(iterations)
