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

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f" {text} ".center(70, "="))
    print("=" * 70)

def get_table_count(cursor, table_name):
    """Obtiene el conteo de registros de una tabla"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def query_database(db_path):
    """Consulta y muestra información general de la base de datos"""
    if not os.path.exists(db_path):
        print(f"Error: La base de datos '{db_path}' no existe.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
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
                if capture_date and len(capture_date) > 19:
                    capture_date = capture_date[:19]  # Solo tomar los primeros 19 caracteres
                
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
                    ip_data[0], 
                    ip_data[1],
                    f"{percentage:.2f}%"
                ])
            print(src_ip_table)
        
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
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python db_query.py <ruta_de_la_base_de_datos>")
        print("\nEjemplo:")
        print("python db_query.py ./data/db_files/database_20250502_175614.db")
        
        # Listar bases de datos disponibles si no se proporciona una
        db_dir = os.getenv('DATABASE_DIRECTORY', './data/db_files')
        if os.path.exists(db_dir):
            print("\nBases de datos disponibles:")
            for file in sorted(os.listdir(db_dir), reverse=True):
                if file.endswith(".db"):
                    file_path = os.path.join(db_dir, file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    print(f"- {file} ({size:.2f} KB)")
        return 1
    
    db_path = sys.argv[1]
    success = query_database(db_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())