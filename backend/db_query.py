#!/usr/bin/env python
"""
Script para consultar información general de bases de datos SQLite generadas por el Network Analyzer.
Uso: python db_query.py [ruta_de_la_base_de_datos] [opciones]

Opciones:
  -d, --detailed     Mostrar información detallada de los paquetes
  -l, --limit N      Límite de paquetes a mostrar en modo detallado (por defecto: 5)
  -s, --session ID   Muestra solo información de la sesión especificada
  -p, --packet ID    Muestra información completa de un paquete específico
  -a, --anomalies    Muestra solo paquetes con anomalías detectadas
  --raw-sql QUERY    Ejecuta una consulta SQL personalizada
"""

import os
import sys
import sqlite3
from prettytable import PrettyTable, SINGLE_BORDER
from datetime import datetime
import argparse
import json

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80)

def print_subheader(text):
    """Imprime un subencabezado formateado"""
    print("\n" + "-" * 80)
    print(f" {text} ".center(80, "-"))
    print("-" * 80)

def get_table_count(cursor, table_name, condition=None):
    """Obtiene el conteo de registros de una tabla con condición opcional"""
    query = f"SELECT COUNT(*) FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    cursor.execute(query)
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
        # Procesar posibles objetos JSON almacenados como texto
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict) and len(parsed) > 2:
                    return f"{{{len(parsed)} keys}}"
                elif isinstance(parsed, list) and len(parsed) > 2:
                    return f"[{len(parsed)} items]"
                else:
                    value_str = json.dumps(parsed, ensure_ascii=False)
                    if len(value_str) > 50:
                        return value_str[:47] + "..."
                    return value_str
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Truncar strings largos
        value_str = str(value)
        if len(value_str) > 50:
            return value_str[:47] + "..."
        return value_str

def query_database(db_path, detailed=False, limit=10, session_id=None, packet_id=None, 
                  only_anomalies=False, raw_sql=None):
    """Consulta y muestra información de la base de datos"""
    if not os.path.exists(db_path):
        print(f"Error: La base de datos '{db_path}' no existe.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        cursor = conn.cursor()
        
        # Si es una consulta SQL personalizada, ejecutarla y salir
        if raw_sql:
            try:
                print_header("CONSULTA SQL PERSONALIZADA")
                print(f"Ejecutando: {raw_sql}")
                cursor.execute(raw_sql)
                results = cursor.fetchall()
                if not results:
                    print("La consulta no devolvió resultados.")
                    return True
                
                # Crear tabla para mostrar resultados
                result_table = PrettyTable()
                columns = [description[0] for description in cursor.description]
                result_table.field_names = columns
                
                # Añadir filas
                for row in results:
                    formatted_row = [format_value(row[i]) for i in range(len(columns))]
                    result_table.add_row(formatted_row)
                
                print(f"Resultados ({len(results)} filas):")
                print(result_table)
                return True
            except sqlite3.Error as e:
                print(f"Error al ejecutar la consulta SQL: {e}")
                return False
        
        # Si se especificó un ID de paquete, mostrar información detallada de ese paquete
        if packet_id:
            return show_packet_detail(cursor, packet_id)
            
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

        # Condición para filtrar por sesión si es necesario
        session_condition = f"session_id = {session_id}" if session_id else None
        
        # Resumen de tablas y registros
        print_header("RESUMEN DE TABLAS")
        table_info = PrettyTable()
        table_info.field_names = ["Tabla", "Total Registros", "Registros Filtrados"]
        
        tables = ["capture_sessions", "packets", "tcp_info", "udp_info", "icmp_info", "anomalies"]
        for table in tables:
            total_count = get_table_count(cursor, table)
            filtered_count = get_table_count(cursor, table, session_condition) if session_condition else total_count
            table_info.add_row([table, total_count, filtered_count if session_condition else "N/A"])
        
        print(table_info)
        
        # Información de sesiones de captura
        print_header("SESIONES DE CAPTURA")
        
        # Consulta específica para una sesión o todas
        if session_id:
            cursor.execute("""
                SELECT 
                    id, file_name, interface, filter_applied, 
                    start_time, end_time, capture_date, packet_count,
                    status, pcap_file, file_path
                FROM 
                    capture_sessions
                WHERE 
                    id = ?
            """, (session_id,))
        else:
            cursor.execute("""
                SELECT 
                    id, file_name, interface, filter_applied, 
                    start_time, end_time, capture_date, packet_count,
                    status, pcap_file, file_path
                FROM 
                    capture_sessions
                ORDER BY 
                    capture_date DESC
            """)
        
        sessions = cursor.fetchall()
        if not sessions:
            print("No hay sesiones de captura en esta base de datos." + 
                  (f" con ID={session_id}" if session_id else ""))
        else:
            sessions_table = PrettyTable()
            sessions_table.field_names = ["ID", "Archivo", "Interfaz", "Filtro", 
                                         "Inicio", "Fin", "Estado", "Paquetes"]
            for session in sessions:
                # Formatear fechas si es necesario
                start_time = session["start_time"]
                end_time = session["end_time"]
                
                sessions_table.add_row([
                    session["id"], 
                    session["file_name"], 
                    session["interface"] or "N/A", 
                    session["filter_applied"] or "N/A",
                    start_time if start_time else "N/A",
                    end_time if end_time else "N/A",
                    session["status"],
                    session["packet_count"] or 0
                ])
            print(sessions_table)
            
            # Si estamos viendo una sola sesión, mostrar información completa
            if session_id and sessions:
                session = sessions[0]
                print_subheader(f"INFORMACIÓN DETALLADA DE LA SESIÓN {session_id}")
                
                for key, value in dict(session).items():
                    if key not in ["id"]:  # Excluimos id porque ya se mostró arriba
                        print(f"{key.replace('_', ' ').title()}: {value or 'N/A'}")
        
        # Filtro de condición para consultas posteriores
        where_clause = ""
        if session_id:
            where_clause = f"WHERE p.session_id = {session_id}"
        
        if only_anomalies:
            if where_clause:
                where_clause += " AND p.id IN (SELECT packet_id FROM anomalies)"
            else:
                where_clause = "WHERE p.id IN (SELECT packet_id FROM anomalies)"
        
        # Si se solicitó información detallada, mostrar estadísticas globales y agrupadas
        if detailed and not only_anomalies:
            print_header("ESTADÍSTICAS GLOBALES DE LOS PAQUETES")
            # 1. Distribución de protocolos (solo hasta capa 3)
            print_subheader("Distribución de protocolos de red (L3)")
            cursor.execute(f"""
                SELECT ip_version, COUNT(*) as count
                FROM packets
                {where_clause}
                WHERE ip_version IS NOT NULL
                GROUP BY ip_version
                ORDER BY count DESC
            """)
            ip_vers = cursor.fetchall()
            if ip_vers:
                table = PrettyTable()
                table.field_names = ["Versión IP", "Cantidad"]
                for row in ip_vers:
                    table.add_row([f"IPv{row['ip_version']}", row['count']])
                print(table)

            # 2. Top IPs origen
            print_subheader("Top 10 IP Origen")
            cursor.execute(f"""
                SELECT src_ip, COUNT(*) as count
                FROM packets
                {where_clause}
                WHERE src_ip IS NOT NULL
                GROUP BY src_ip
                ORDER BY count DESC
                LIMIT 10
            """)
            src_ips = cursor.fetchall()
            if src_ips:
                table = PrettyTable()
                table.field_names = ["IP Origen", "Cantidad"]
                for row in src_ips:
                    table.add_row(row)
                print(table)

            # 3. Top IPs destino
            print_subheader("Top 10 IP Destino")
            cursor.execute(f"""
                SELECT dst_ip, COUNT(*) as count
                FROM packets
                {where_clause}
                WHERE dst_ip IS NOT NULL
                GROUP BY dst_ip
                ORDER BY count DESC
                LIMIT 10
            """)
            dst_ips = cursor.fetchall()
            if dst_ips:
                table = PrettyTable()
                table.field_names = ["IP Destino", "Cantidad"]
                for row in dst_ips:
                    table.add_row(row)
                print(table)

            # 4. Distribución de tamaños de paquetes
            print_subheader("Distribución de tamaños de paquetes")
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN packet_length < 100 THEN '<100'
                        WHEN packet_length < 500 THEN '100-499'
                        WHEN packet_length < 1000 THEN '500-999'
                        WHEN packet_length < 1500 THEN '1000-1499'
                        ELSE '>=1500'
                    END as size_range,
                    COUNT(*) as count
                FROM packets
                {where_clause}
                GROUP BY size_range
                ORDER BY count DESC
            """)
            sizes = cursor.fetchall()
            if sizes:
                table = PrettyTable()
                table.field_names = ["Rango (bytes)", "Cantidad"]
                for row in sizes:
                    table.add_row(row)
                print(table)

            # 5. Top combinaciones IP origen/destino
            print_subheader("Top 10 pares IP Origen/Destino")
            cursor.execute(f"""
                SELECT src_ip, dst_ip, COUNT(*) as count
                FROM packets
                {where_clause}
                WHERE src_ip IS NOT NULL AND dst_ip IS NOT NULL
                GROUP BY src_ip, dst_ip
                ORDER BY count DESC
                LIMIT 10
            """)
            pairs = cursor.fetchall()
            if pairs:
                table = PrettyTable()
                table.field_names = ["IP Origen", "IP Destino", "Cantidad"]
                for row in pairs:
                    table.add_row(row)
                print(table)

            # 6. Distribución temporal de paquetes (por minuto)
            print_subheader("Paquetes por minuto (primeros 20 min)")
            cursor.execute(f"""
                SELECT strftime('%Y-%m-%d %H:%M', datetime(timestamp, 'unixepoch')) as minuto, COUNT(*) as count
                FROM packets
                {where_clause}
                GROUP BY minuto
                ORDER BY minuto ASC
                LIMIT 20
            """)
            per_min = cursor.fetchall()
            if per_min:
                table = PrettyTable()
                table.field_names = ["Minuto", "Paquetes"]
                for row in per_min:
                    table.add_row(row)
                print(table)

            # 7. Estadísticas de ARP
            print_subheader("Estadísticas ARP")
            cursor.execute(f"""
                SELECT arp_opcode, COUNT(*) as count
                FROM packets
                {where_clause}
                WHERE arp_opcode IS NOT NULL
                GROUP BY arp_opcode
                ORDER BY count DESC
            """)
            arps = cursor.fetchall()
            if arps:
                table = PrettyTable()
                table.field_names = ["ARP Opcode", "Cantidad"]
                for row in arps:
                    table.add_row(row)
                print(table)

            # 8. Bytes totales y duración
            print_subheader("Resumen de bytes y tiempo")
            cursor.execute(f"SELECT SUM(packet_length) as total_bytes, MIN(timestamp) as t0, MAX(timestamp) as t1 FROM packets {where_clause}")
            row = cursor.fetchone()
            if row:
                total_bytes = row[0] or 0
                t0 = row[1] or 0
                t1 = row[2] or 0
                duration = t1 - t0 if t1 and t0 else 0
                print(f"Total de bytes: {total_bytes:,}")
                print(f"Duración de la captura: {duration:.2f} segundos")

            print("\nPara ver información completa de un paquete específico, use:")
            print(f"python db_query.py {db_path} -p <ID_PAQUETE>")

        print("\nAnálisis de base de datos completado.")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Error al consultar la base de datos: {e}")
        return False

def show_packet_detail(cursor, packet_id):
    """Muestra información detallada de un paquete específico"""
    try:
        # Verificar que el paquete existe
        cursor.execute("SELECT COUNT(*) FROM packets WHERE id = ?", (packet_id,))
        if cursor.fetchone()[0] == 0:
            print(f"Error: No existe un paquete con ID {packet_id}.")
            return False
            
        print_header(f"INFORMACIÓN DETALLADA DEL PAQUETE {packet_id}")
        
        # Obtener todos los campos del paquete
        cursor.execute("PRAGMA table_info(packets)")
        packet_columns = [row[1] for row in cursor.fetchall()]
        
        # Obtener valores del paquete
        cursor.execute(f"SELECT * FROM packets WHERE id = {packet_id}")
        packet = cursor.fetchone()
        
        # Crear tabla para mostrar la información del paquete
        main_table = PrettyTable()
        main_table.field_names = ["Campo", "Valor"]
        main_table.align["Valor"] = "l"  # Alinear valores a la izquierda
        
        # Añadir filas para cada campo del paquete
        for column in packet_columns:
            if packet[column] is not None and column != 'id':  # Excluir campos nulos e ID (ya lo mostramos en el título)
                value = packet[column]
                
                # Formatear valores especiales
                if isinstance(value, bool):
                    value = "✓" if value else "✗"
                elif isinstance(value, str) and len(value) > 80:
                    value = value[:77] + "..."
                
                main_table.add_row([column, value])
                
        print(main_table)
        
        # Verificar si tiene TCP info asociada
        cursor.execute("SELECT COUNT(*) FROM tcp_info WHERE packet_id = ?", (packet_id,))
        has_tcp_info = cursor.fetchone()[0] > 0
        
        if has_tcp_info:
            print_subheader("INFORMACIÓN TCP DETALLADA")
            cursor.execute(f"SELECT * FROM tcp_info WHERE packet_id = {packet_id}")
            tcp_info = cursor.fetchone()
            
            if tcp_info:
                tcp_table = PrettyTable()
                tcp_table.field_names = ["Campo TCP", "Valor"]
                tcp_table.align["Valor"] = "l"  # Alinear valores a la izquierda
                
                for key, value in dict(tcp_info).items():
                    if key != 'id' and key != 'packet_id' and value is not None:
                        tcp_table.add_row([key, value])
                        
                print(tcp_table)
        
        # Verificar si tiene UDP info asociada
        cursor.execute("SELECT COUNT(*) FROM udp_info WHERE packet_id = ?", (packet_id,))
        has_udp_info = cursor.fetchone()[0] > 0
        
        if has_udp_info:
            print_subheader("INFORMACIÓN UDP DETALLADA")
            cursor.execute(f"SELECT * FROM udp_info WHERE packet_id = {packet_id}")
            udp_info = cursor.fetchone()
            
            if udp_info:
                udp_table = PrettyTable()
                udp_table.field_names = ["Campo UDP", "Valor"]
                udp_table.align["Valor"] = "l"  # Alinear valores a la izquierda
                
                for key, value in dict(udp_info).items():
                    if key != 'id' and key != 'packet_id' and value is not None:
                        udp_table.add_row([key, value])
                        
                print(udp_table)
                
        # Verificar si tiene ICMP info asociada
        cursor.execute("SELECT COUNT(*) FROM icmp_info WHERE packet_id = ?", (packet_id,))
        has_icmp_info = cursor.fetchone()[0] > 0
        
        if has_icmp_info:
            print_subheader("INFORMACIÓN ICMP DETALLADA")
            cursor.execute(f"SELECT * FROM icmp_info WHERE packet_id = {packet_id}")
            icmp_info = cursor.fetchone()
            
            if icmp_info:
                icmp_table = PrettyTable()
                icmp_table.field_names = ["Campo ICMP", "Valor"]
                icmp_table.align["Valor"] = "l"  # Alinear valores a la izquierda
                
                for key, value in dict(icmp_info).items():
                    if key != 'id' and key != 'packet_id' and value is not None:
                        icmp_table.add_row([key, value])
                        
                print(icmp_table)
        
        # Verificar si tiene anomalías asociadas
        cursor.execute("""
            SELECT 
                type, description, severity, detection_method, detection_time
            FROM 
                anomalies 
            WHERE 
                packet_id = ?
            ORDER BY 
                severity
        """, (packet_id,))
        
        anomalies = cursor.fetchall()
        if anomalies:
            print_subheader("ANOMALÍAS DETECTADAS EN ESTE PAQUETE")
            anomaly_table = PrettyTable()
            anomaly_table.field_names = ["Tipo", "Descripción", "Severidad", "Método Detección", "Tiempo"]
            
            for anomaly in anomalies:
                anomaly_table.add_row([
                    anomaly["type"],
                    anomaly["description"],
                    anomaly["severity"],
                    anomaly["detection_method"] or "N/A",
                    anomaly["detection_time"]
                ])
                
            print(anomaly_table)
            
        return True
        
    except sqlite3.Error as e:
        print(f"Error al obtener detalles del paquete: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Consulta información de bases de datos del Network Analyzer")
    parser.add_argument("db_path", nargs="?", help="Ruta de la base de datos a consultar")
    parser.add_argument("-d", "--detailed", action="store_true", help="Mostrar información detallada de los paquetes")
    parser.add_argument("-l", "--limit", type=int, default=10, help="Límite de paquetes a mostrar en modo detallado (por defecto: 10)")
    parser.add_argument("-s", "--session", type=int, help="ID de la sesión específica a consultar")
    parser.add_argument("-p", "--packet", type=int, help="ID del paquete específico a mostrar en detalle")
    parser.add_argument("-a", "--anomalies", action="store_true", help="Mostrar solo paquetes con anomalías")
    parser.add_argument("--raw-sql", type=str, help="Ejecutar una consulta SQL personalizada en la base de datos")
    
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
            print("Uso: python db_query.py [ruta_de_la_base_de_datos] [opciones]")
            return 1
    
    success = query_database(
        args.db_path, 
        args.detailed, 
        args.limit,
        args.session,
        args.packet,
        args.anomalies,
        args.raw_sql
    )
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())