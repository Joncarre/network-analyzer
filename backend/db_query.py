#!/usr/bin/env python
"""
Script para consultar información general de bases de datos SQLite generadas por el Network Analyzer.
Uso: python db_query.py <ruta_de_la_base_de_datos>
"""

import os
import sys
import sqlite3
from prettytable import PrettyTable
from datetime import datetime
import argparse

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def get_table_count(cursor, table_name):
    """Obtiene el conteo de registros de una tabla"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def get_column_names(cursor, table_name):
    """Obtiene los nombres de las columnas de una tabla"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]

def format_value(value):
    """Formatea un valor para su presentación"""
    if value is None:
        return "NULL"
    elif isinstance(value, bool):
        return "✓" if value else "✗"
    elif isinstance(value, (int, float)):
        return f"{value}"
    else:
        # Truncar strings largos
        value_str = str(value)
        if len(value_str) > 50:
            return value_str[:47] + "..."
        return value_str

def query_database(db_path, detailed=False, limit=10):
    """Consulta y muestra información general de la base de datos"""
    if not os.path.exists(db_path):
        print(f"Error: La base de datos '{db_path}' no existe.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        cursor = conn.cursor()
        
        # Información general del archivo de la base de datos
        file_size = os.path.getsize(db_path) / 1024  # KB
        
        print_header("INFORMACIÓN GENERAL DE LA BASE DE DATOS")
        print(f"Ruta: {db_path}")
        print(f"Tamaño: {file_size:.2f} KB")
        
        # Verificar si es una base de datos válida del sistema
        try:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='capture_sessions'")
            if cursor.fetchone()[0] == 0:
                print("Error: Esta no parece ser una base de datos válida del Network Analyzer.")
                return False
        except sqlite3.Error:
            print("Error: Esta no es una base de datos SQLite válida.")
            return False
        
        # Resumen de tablas y registros
        print_header("RESUMEN DE TABLAS")
        table_info = PrettyTable()
        table_info.field_names = ["Tabla", "Registros"]
        
        tables = ["capture_sessions", "packets", "tcp_info", "udp_info", "icmp_info", "anomalies"]
        for table in tables:
            count = get_table_count(cursor, table)
            table_info.add_row([table, count])
        
        print(table_info)
        
        # Información de sesiones de captura
        print_header("SESIONES DE CAPTURA")
        cursor.execute("""
            SELECT 
                id, file_name, interface, filter_applied, 
                capture_date, packet_count
            FROM 
                capture_sessions
            ORDER BY 
                capture_date DESC
        """)
        
        sessions = cursor.fetchall()
        if not sessions:
            print("No hay sesiones de captura en esta base de datos.")
        else:
            sessions_table = PrettyTable()
            sessions_table.field_names = ["ID", "Archivo", "Interfaz", "Filtro", "Fecha", "Paquetes"]
            for session in sessions:
                # Formatear la fecha si es necesario
                capture_date = session[4]
                if capture_date and len(str(capture_date)) > 19:
                    capture_date = str(capture_date)[:19]  # Solo tomar los primeros 19 caracteres
                
                sessions_table.add_row([
                    session[0], 
                    session[1], 
                    session[2] or "N/A", 
                    session[3] or "N/A",
                    capture_date,
                    session[5] or 0
                ])
            print(sessions_table)
        
        # Resumen de protocolos
        print_header("DISTRIBUCIÓN DE PROTOCOLOS")
        cursor.execute("""
            SELECT 
                protocol, COUNT(*) as count
            FROM 
                packets
            GROUP BY 
                protocol
            ORDER BY 
                count DESC
        """)
        
        protocols = cursor.fetchall()
        if protocols:
            protocol_table = PrettyTable()
            protocol_table.field_names = ["Protocolo", "Paquetes", "Porcentaje"]
            
            total_packets = sum(p[1] for p in protocols)
            for protocol in protocols:
                percentage = (protocol[1] / total_packets) * 100 if total_packets > 0 else 0
                protocol_table.add_row([
                    protocol[0] or "Desconocido", 
                    protocol[1],
                    f"{percentage:.2f}%"
                ])
            print(protocol_table)
        
        # Top IP de origen
        print_header("TOP 10 DIRECCIONES IP DE ORIGEN")
        cursor.execute("""
            SELECT 
                src_ip, COUNT(*) as count
            FROM 
                packets
            GROUP BY 
                src_ip
            ORDER BY 
                count DESC
            LIMIT 10
        """)
        
        top_src_ips = cursor.fetchall()
        if top_src_ips:
            src_ip_table = PrettyTable()
            src_ip_table.field_names = ["IP Origen", "Paquetes", "Porcentaje"]
            
            total_packets = get_table_count(cursor, "packets")
            for ip_data in top_src_ips:
                percentage = (ip_data[1] / total_packets) * 100 if total_packets > 0 else 0
                src_ip_table.add_row([
                    ip_data[0] or "N/A", 
                    ip_data[1],
                    f"{percentage:.2f}%"
                ])
            print(src_ip_table)

        # Top puertos de destino
        print_header("TOP 10 PUERTOS DE DESTINO")
        cursor.execute("""
            SELECT 
                dst_port, transport_protocol, COUNT(*) as count
            FROM 
                packets
            WHERE
                dst_port IS NOT NULL
            GROUP BY 
                dst_port, transport_protocol
            ORDER BY 
                count DESC
            LIMIT 10
        """)
        
        top_ports = cursor.fetchall()
        if top_ports:
            port_table = PrettyTable()
            port_table.field_names = ["Puerto Destino", "Protocolo", "Paquetes", "Porcentaje"]
            
            total_with_ports = sum(p[2] for p in top_ports)
            for port_data in top_ports:
                percentage = (port_data[2] / total_with_ports) * 100 if total_with_ports > 0 else 0
                port_table.add_row([
                    port_data[0], 
                    port_data[1] or "N/A",
                    port_data[2],
                    f"{percentage:.2f}%"
                ])
            print(port_table)
            
        # Estadísticas de HTTP (si hay tráfico HTTP)
        cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol = 'HTTP'")
        if cursor.fetchone()[0] > 0:
            print_header("ESTADÍSTICAS HTTP")
            
            # Métodos HTTP
            cursor.execute("""
                SELECT 
                    http_method, COUNT(*) as count
                FROM 
                    packets
                WHERE 
                    http_method IS NOT NULL
                GROUP BY 
                    http_method
                ORDER BY 
                    count DESC
            """)
            
            methods = cursor.fetchall()
            if methods:
                method_table = PrettyTable()
                method_table.field_names = ["Método HTTP", "Cantidad"]
                for method in methods:
                    method_table.add_row([method[0], method[1]])
                print(method_table)
                
            # Códigos de respuesta HTTP
            cursor.execute("""
                SELECT 
                    http_response_code, COUNT(*) as count
                FROM 
                    packets
                WHERE 
                    http_response_code IS NOT NULL
                GROUP BY 
                    http_response_code
                ORDER BY 
                    count DESC
            """)
            
            responses = cursor.fetchall()
            if responses:
                response_table = PrettyTable()
                response_table.field_names = ["Código HTTP", "Descripción", "Cantidad"]
                for resp in responses:
                    # Descripción del código HTTP
                    desc = ""
                    code = resp[0]
                    if code >= 100 and code < 200:
                        desc = "Informativo"
                    elif code >= 200 and code < 300:
                        desc = "Éxito"
                    elif code >= 300 and code < 400:
                        desc = "Redirección"
                    elif code >= 400 and code < 500:
                        desc = "Error cliente"
                    elif code >= 500 and code < 600:
                        desc = "Error servidor"
                        
                    response_table.add_row([code, desc, resp[1]])
                print("\nCódigos de respuesta HTTP:")
                print(response_table)
                
        # Estadísticas DNS (si hay tráfico DNS)
        cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol = 'DNS'")
        if cursor.fetchone()[0] > 0:
            print_header("ESTADÍSTICAS DNS")
            
            # Tipos de consulta DNS
            cursor.execute("""
                SELECT 
                    dns_query_type, COUNT(*) as count
                FROM 
                    packets
                WHERE 
                    dns_query_type IS NOT NULL
                GROUP BY 
                    dns_query_type
                ORDER BY 
                    count DESC
            """)
            
            dns_types = cursor.fetchall()
            if dns_types:
                dns_type_table = PrettyTable()
                dns_type_table.field_names = ["Tipo de Consulta", "Cantidad"]
                for dns_type in dns_types:
                    dns_type_table.add_row([dns_type[0], dns_type[1]])
                print(dns_type_table)
                
            # Top dominios consultados
            cursor.execute("""
                SELECT 
                    dns_query_name, COUNT(*) as count
                FROM 
                    packets
                WHERE 
                    dns_query_name IS NOT NULL
                GROUP BY 
                    dns_query_name
                ORDER BY 
                    count DESC
                LIMIT 10
            """)
            
            domains = cursor.fetchall()
            if domains:
                domain_table = PrettyTable()
                domain_table.field_names = ["Dominio", "Consultas"]
                for domain in domains:
                    domain_table.add_row([domain[0], domain[1]])
                print("\nTop 10 dominios consultados:")
                print(domain_table)
                
        # Estadísticas TCP
        print_header("ESTADÍSTICAS DE BANDERAS TCP")
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tcp_flag_syn = 1 THEN 1 ELSE 0 END) as syn,
                SUM(CASE WHEN tcp_flag_ack = 1 THEN 1 ELSE 0 END) as ack,
                SUM(CASE WHEN tcp_flag_fin = 1 THEN 1 ELSE 0 END) as fin,
                SUM(CASE WHEN tcp_flag_rst = 1 THEN 1 ELSE 0 END) as rst,
                SUM(CASE WHEN tcp_flag_psh = 1 THEN 1 ELSE 0 END) as psh,
                SUM(CASE WHEN tcp_flag_urg = 1 THEN 1 ELSE 0 END) as urg,
                SUM(CASE WHEN tcp_flag_ece = 1 THEN 1 ELSE 0 END) as ece,
                SUM(CASE WHEN tcp_flag_cwr = 1 THEN 1 ELSE 0 END) as cwr,
                SUM(CASE WHEN tcp_flag_ns = 1 THEN 1 ELSE 0 END) as ns,
                COUNT(*) as total_tcp
            FROM 
                packets
            WHERE 
                protocol = 'TCP'
        """)
        
        tcp_stats = cursor.fetchone()
        if tcp_stats and tcp_stats['total_tcp'] > 0:
            flags_table = PrettyTable()
            flags_table.field_names = ["Flag", "Cantidad", "Porcentaje"]
            
            for flag in ["syn", "ack", "fin", "rst", "psh", "urg", "ece", "cwr", "ns"]:
                count = tcp_stats[flag] or 0
                percentage = (count / tcp_stats['total_tcp']) * 100
                flags_table.add_row([
                    flag.upper(), 
                    count,
                    f"{percentage:.2f}%"
                ])
            print(flags_table)
            
        # Anomalías detectadas
        print_header("ANOMALÍAS DETECTADAS")
        cursor.execute("""
            SELECT 
                a.type, a.description, a.severity, COUNT(*) as count
            FROM 
                anomalies a
            GROUP BY 
                a.type, a.description, a.severity
            ORDER BY 
                count DESC
        """)
        
        anomalies = cursor.fetchall()
        if not anomalies:
            print("No se detectaron anomalías en esta captura.")
        else:
            anomaly_table = PrettyTable()
            anomaly_table.field_names = ["Tipo", "Descripción", "Severidad", "Ocurrencias"]
            for anomaly in anomalies:
                anomaly_table.add_row(anomaly)
            print(anomaly_table)
            
        # Ya no mostramos la sección de muestra de paquetes
        return True
        
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Consulta información de bases de datos del Network Analyzer")
    parser.add_argument("db_path", nargs="?", help="Ruta de la base de datos a consultar")
    parser.add_argument("-d", "--detailed", action="store_true", help="Mostrar información detallada de los paquetes")
    parser.add_argument("-l", "--limit", type=int, default=5, help="Límite de paquetes a mostrar en modo detallado (por defecto: 5)")
    
    args = parser.parse_args()
    
    # Si no se proporciona una ruta de base de datos
    if not args.db_path:
        # Listar bases de datos disponibles
        db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
        if os.path.exists(db_dir):
            db_files = []
            print("\nBases de datos disponibles:")
            for file in sorted(os.listdir(db_dir), reverse=True):
                if file.endswith(".db"):
                    file_path = os.path.join(db_dir, file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    db_files.append((file, file_path, size, mod_time))
            
            # Mostrar tabla de bases de datos disponibles
            if db_files:
                db_table = PrettyTable()
                db_table.field_names = ["#", "Archivo", "Tamaño (KB)", "Fecha modificación"]
                for i, (file, path, size, mod_time) in enumerate(db_files):
                    db_table.add_row([i+1, file, f"{size:.2f}", mod_time])
                print(db_table)
                
                # Permitir selección interactiva
                try:
                    choice = input("\nSelecciona el número de la base de datos o presiona Enter para salir: ")
                    if choice and choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(db_files):
                            args.db_path = db_files[idx][1]
                            print(f"\nSeleccionada: {db_files[idx][0]}")
                        else:
                            print("Selección no válida.")
                            return 1
                    else:
                        print("Operación cancelada.")
                        return 1
                except (ValueError, IndexError):
                    print("Selección no válida.")
                    return 1
            else:
                print("No se encontraron bases de datos.")
                return 1
        else:
            print(f"El directorio de bases de datos '{db_dir}' no existe.")
            print("Uso: python db_query.py <ruta_de_la_base_de_datos> [--detailed] [--limit N]")
            return 1
    
    success = query_database(args.db_path, args.detailed, args.limit)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())