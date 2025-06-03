#!/usr/bin/env python3
"""
Benchmark para medir rendimiento de la API REST
"""

import requests
import time
import json
import statistics
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

class APIBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def test_api_availability(self):
        """Verifica que la API esté disponible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def benchmark_endpoint(self, endpoint, method="GET", data=None, iterations=10):
        """Benchmark de un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        times = []
        success_count = 0
        
        print(f"\nBenchmarking {method} {endpoint} ({iterations} iteraciones)...")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if method.upper() == "GET":
                    response = requests.get(url, timeout=30)
                elif method.upper() == "POST":
                    response = requests.post(url, json=data, timeout=30)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    times.append(response_time)
                    success_count += 1
                    print(f"  Iteración {i+1}: {response_time:.3f}s - OK")
                else:
                    print(f"  Iteración {i+1}: Error {response.status_code}")
                    
            except Exception as e:
                print(f"  Iteración {i+1}: Error - {str(e)}")
        
        if times:
            result = {
                'endpoint': endpoint,
                'method': method,
                'iterations': iterations,
                'success_count': success_count,
                'success_rate': success_count / iterations,
                'avg_response_time': statistics.mean(times),
                'min_response_time': min(times),
                'max_response_time': max(times),
                'median_response_time': statistics.median(times),
                'requests_per_second': success_count / sum(times) if times else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(result)
            
            print(f"  Promedio: {result['avg_response_time']:.3f}s")
            print(f"  Éxito: {success_count}/{iterations} ({result['success_rate']*100:.1f}%)")
            print(f"  RPS: {result['requests_per_second']:.1f}")
            
            return result
        
        return None
    
    def benchmark_concurrent_requests(self, endpoint, concurrent_users=5, requests_per_user=10):
        """Benchmark con múltiples usuarios concurrentes"""
        print(f"\nBenchmark concurrente: {concurrent_users} usuarios, {requests_per_user} requests c/u")
        
        def user_requests():
            times = []
            for _ in range(requests_per_user):
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
                    end_time = time.time()
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                except:
                    pass
            return times
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(user_requests) for _ in range(concurrent_users)]
            all_times = []
            for future in futures:
                all_times.extend(future.result())
        
        total_time = time.time() - start_time
        
        if all_times:
            result = {
                'endpoint': endpoint,
                'test_type': 'concurrent',
                'concurrent_users': concurrent_users,
                'requests_per_user': requests_per_user,
                'total_requests': len(all_times),
                'total_time': total_time,
                'avg_response_time': statistics.mean(all_times),
                'throughput_rps': len(all_times) / total_time,
                'timestamp': datetime.now().isoformat()            }
            
            self.results.append(result)
            
            print(f"  Total requests: {len(all_times)}")
            print(f"  Tiempo total: {total_time:.2f}s")
            print(f"  Throughput: {result['throughput_rps']:.1f} RPS")
            
            return result
        
        return None
    
    def run_benchmark(self):
        """Ejecuta benchmark completo de la API"""
        print("=== BENCHMARK DE API REST ===")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL base: {self.base_url}")
        
        if not self.test_api_availability():
            print("❌ API no disponible. Asegúrate de que el backend esté ejecutándose.")
            return
        
        print("✅ API disponible")
          # Endpoints básicos
        self.benchmark_endpoint("/", iterations=20)
        self.benchmark_endpoint("/api/capture/interfaces", iterations=15)
        self.benchmark_endpoint("/api/database/list-db-files", iterations=15)  # Usando endpoint que funciona
        
        # Endpoint con datos (si hay DBs disponibles)
        try:
            db_response = requests.get(f"{self.base_url}/api/database/list-db-files")
            if db_response.status_code == 200:
                db_files = db_response.json()
                if db_files:
                    # Usar la primera DB disponible
                    first_db = db_files[0]['name']  # Cambiado de 'filename' a 'name'
                    self.benchmark_endpoint(f"/api/database/sessions?db_file={first_db}", iterations=10)
        except Exception as e:
            print(f"Error al obtener información de bases de datos: {e}")
        
        # Test concurrente en endpoint ligero
        self.benchmark_concurrent_requests("/", concurrent_users=5, requests_per_user=10)
        
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """Guarda resultados en archivo JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_api_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'benchmark_type': 'api_rest',
                'base_url': self.base_url,
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        
        print(f"\nResultados guardados en: {results_file}")
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        if not self.results:
            return
        
        print("\n=== RESUMEN ===")
        print(f"{'Endpoint':<40} {'Método':<8} {'Promedio(s)':<12} {'RPS':<8} {'Éxito %':<8}")
        print("-" * 80)
        
        for result in self.results:
            if result.get('test_type') != 'concurrent':
                endpoint = result['endpoint']
                method = result['method']
                avg_time = result['avg_response_time']
                rps = result['requests_per_second']
                success = result['success_rate'] * 100
                
                print(f"{endpoint:<40} {method:<8} {avg_time:<12.3f} {rps:<8.1f} {success:<8.1f}")

if __name__ == "__main__":
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    benchmark = APIBenchmark(base_url)
    benchmark.run_benchmark()
