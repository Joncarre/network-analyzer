#!/usr/bin/env python3
"""
Benchmark para medir rendimiento del procesamiento de archivos PCAP
"""

import os
import sys
import time
import json
from datetime import datetime
import statistics

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing.pcap_processor import PCAPProcessor

class ProcessingBenchmark:
    def __init__(self):
        self.results = []
        self.pcap_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'pcap_files')
        
    def get_pcap_files(self):
        """Obtiene lista de archivos PCAP disponibles"""
        if not os.path.exists(self.pcap_dir):
            return []
        return [f for f in os.listdir(self.pcap_dir) if f.endswith(('.pcap', '.pcapng'))]
    
    def get_file_size(self, file_path):
        """Obtiene el tamaño de archivo en MB"""
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def benchmark_single_file(self, pcap_file, iterations=3):
        """Ejecuta benchmark en un archivo específico"""
        file_path = os.path.join(self.pcap_dir, pcap_file)
        file_size_mb = self.get_file_size(file_path)
        
        print(f"\n--- Benchmarking: {pcap_file} ({file_size_mb:.2f} MB) ---")
        
        times = []
        packet_counts = []
        
        for i in range(iterations):
            print(f"Iteración {i+1}/{iterations}...")
            
            start_time = time.time()
            try:
                processor = PCAPProcessor(pcap_file=file_path)
                session_id = processor.process_pcap_file(file_path)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                times.append(processing_time)
                
                # Obtener el conteo de paquetes desde la base de datos
                packet_count = 0
                if session_id:
                    try:
                        from sqlalchemy.orm import sessionmaker
                        from database.models import CaptureSession
                        
                        Session = sessionmaker(bind=processor.engine)
                        db_session = Session()
                        
                        capture_session = db_session.query(CaptureSession).filter(
                            CaptureSession.id == session_id
                        ).first()
                        
                        if capture_session:
                            packet_count = capture_session.packet_count or 0
                        
                        db_session.close()
                    except Exception as db_error:
                        print(f"    Error obteniendo conteo de paquetes: {db_error}")
                        packet_count = 0
                
                packet_counts.append(packet_count)
                
                print(f"  Tiempo: {processing_time:.2f}s | Paquetes: {packet_count}")
                
            except Exception as e:
                print(f"  Error en iteración {i+1}: {str(e)}")
                continue
        
        if times:
            avg_time = statistics.mean(times)
            avg_packets = statistics.mean(packet_counts)
            throughput = avg_packets / avg_time if avg_time > 0 else 0
            
            result = {
                'file': pcap_file,
                'file_size_mb': file_size_mb,
                'iterations': len(times),
                'avg_time_seconds': avg_time,
                'min_time_seconds': min(times),
                'max_time_seconds': max(times),
                'avg_packets': avg_packets,
                'throughput_packets_per_second': throughput,
                'throughput_mb_per_second': file_size_mb / avg_time if avg_time > 0 else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            print(f"Promedio: {avg_time:.2f}s | Throughput: {throughput:.0f} paquetes/s | {file_size_mb/avg_time:.2f} MB/s")
            return result
        
        return None
    
    def run_benchmark(self, iterations=3):
        """Ejecuta benchmark completo"""
        print("=== BENCHMARK DE PROCESAMIENTO PCAP ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        pcap_files = self.get_pcap_files()
        
        if not pcap_files:
            print("No se encontraron archivos PCAP para probar")
            return
        
        print(f"Archivos encontrados: {len(pcap_files)}")
        
        for pcap_file in pcap_files:
            self.benchmark_single_file(pcap_file, iterations)
        
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Guarda resultados en archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_processing_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'benchmark_type': 'pcap_processing',
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        
        print(f"\nResultados guardados en: {results_file}")
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        if not self.results:
            return
        
        print("\n=== RESUMEN ===")
        print(f"{'Archivo':<30} {'Tamaño(MB)':<12} {'Tiempo(s)':<10} {'Paquetes/s':<12} {'MB/s':<8}")
        print("-" * 80)
        
        for result in self.results:
            print(f"{result['file']:<30} {result['file_size_mb']:<12.2f} {result['avg_time_seconds']:<10.2f} {result['throughput_packets_per_second']:<12.0f} {result['throughput_mb_per_second']:<8.2f}")

if __name__ == "__main__":
    benchmark = ProcessingBenchmark()
    
    # Permitir especificar número de iteraciones
    iterations = 3
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            print("Uso: python benchmark_processing.py [iteraciones]")
            sys.exit(1)
    
    benchmark.run_benchmark(iterations)
