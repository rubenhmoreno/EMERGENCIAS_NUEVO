#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Diagnóstico Completo de Base de Datos

Este script verifica exactamente qué está pasando con la base de datos
y por qué SQLAlchemy no puede encontrar la columna llamados_atendidos.
"""

import sqlite3
import os
from datetime import datetime

def print_banner():
    print("=" * 60)
    print("DIAGNOSTICO COMPLETO DE BASE DE DATOS")
    print("Sistema de Emergencias Villa Allende v2.0")
    print("=" * 60)
    print()

def check_database_file():
    """Verificar archivo de base de datos"""
    print("1. VERIFICANDO ARCHIVO DE BASE DE DATOS")
    print("-" * 40)
    
    if not os.path.exists('emergency_system.db'):
        print("ERROR: emergency_system.db no existe")
        return False
    
    size = os.path.getsize('emergency_system.db')
    print(f"OK: emergency_system.db existe ({size} bytes)")
    
    # Verificar permisos
    if os.access('emergency_system.db', os.R_OK):
        print("OK: Archivo es legible")
    else:
        print("ERROR: No se puede leer el archivo")
        return False
        
    if os.access('emergency_system.db', os.W_OK):
        print("OK: Archivo es escribible")
    else:
        print("AVISO: Archivo es solo lectura")
    
    return True

def inspect_table_structure(conn, table_name):
    """Inspeccionar estructura detallada de una tabla"""
    print(f"\n2. INSPECCIONANDO TABLA '{table_name}'")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    if not cursor.fetchone():
        print(f"ERROR: Tabla '{table_name}' no existe")
        return False
    
    print(f"OK: Tabla '{table_name}' existe")
    
    # Obtener información detallada de columnas
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"Columnas encontradas ({len(columns)}):")
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"  [{cid}] {name:<20} {type_:<15} "
              f"{'NOT NULL' if notnull else 'NULL':<8} "
              f"DEFAULT: {default if default else 'None':<10} "
              f"{'PK' if pk else ''}")
    
    # Verificar específicamente la columna problemática
    column_names = [col[1] for col in columns]
    if table_name == 'usuarios':
        critical_columns = ['llamados_atendidos', 'intentos_login', 'bloqueado_hasta']
        print(f"\nVerificacion de columnas criticas:")
        for col in critical_columns:
            if col in column_names:
                print(f"  OK: {col} existe")
            else:
                print(f"  ERROR: {col} NO existe")
    
    return True

def test_direct_sql_query(conn):
    """Probar consulta SQL directa"""
    print(f"\n3. PROBANDO CONSULTAS SQL DIRECTAS")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # Probar consulta simple
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"OK: Consulta basica exitosa - {count} usuarios en la tabla")
        
        # Probar consulta con columna problemática
        cursor.execute("SELECT username, llamados_atendidos FROM usuarios LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(f"OK: Consulta con 'llamados_atendidos' exitosa - {result}")
        else:
            print("AVISO: No hay usuarios en la tabla")
        
        return True
        
    except sqlite3.OperationalError as e:
        print(f"ERROR: {e}")
        return False

def test_sqlalchemy_connection():
    """Probar conexión con SQLAlchemy"""
    print(f"\n4. PROBANDO CONEXION SQLALCHEMY")
    print("-" * 40)
    
    try:
        from sqlalchemy import create_engine, text
        
        # Crear engine
        engine = create_engine('sqlite:///emergency_system.db')
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM usuarios"))
            count = result.fetchone()[0]
            print(f"OK: SQLAlchemy conecta correctamente - {count} usuarios")
            
            # Probar consulta problemática
            try:
                result = conn.execute(text("SELECT username, llamados_atendidos FROM usuarios LIMIT 1"))
                row = result.fetchone()
                if row:
                    print(f"OK: SQLAlchemy puede leer 'llamados_atendidos' - {row}")
                else:
                    print("AVISO: No hay datos en usuarios")
                return True
            except Exception as e:
                print(f"ERROR SQLAlchemy: {e}")
                return False
                
    except Exception as e:
        print(f"ERROR importando SQLAlchemy: {e}")
        return False

def check_database_integrity(conn):
    """Verificar integridad de la base de datos"""
    print(f"\n5. VERIFICANDO INTEGRIDAD DE BASE DE DATOS")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # PRAGMA integrity_check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == 'ok':
            print("OK: Integridad de base de datos correcta")
        else:
            print(f"ERROR: Problemas de integridad - {result[0]}")
            return False
        
        # PRAGMA foreign_key_check
        cursor.execute("PRAGMA foreign_key_check")
        fk_errors = cursor.fetchall()
        if not fk_errors:
            print("OK: No hay errores de claves foráneas")
        else:
            print(f"AVISO: {len(fk_errors)} errores de claves foráneas")
        
        return True
        
    except Exception as e:
        print(f"ERROR verificando integridad: {e}")
        return False

def suggest_solution():
    """Sugerir solución basada en los resultados"""
    print(f"\n6. SUGERENCIAS DE SOLUCION")
    print("-" * 40)
    
    print("Basado en el diagnóstico, las posibles soluciones son:")
    print()
    print("A) RECREAR BASE DE DATOS DESDE CERO:")
    print("   1. Hacer backup: copy emergency_system.db emergency_system.db.backup")
    print("   2. Eliminar BD actual: del emergency_system.db")
    print("   3. Ejecutar: python fix_migration.py")
    print()
    print("B) REPARAR TABLA USUARIOS:")
    print("   1. Ejecutar: python fix_missing_column.py")
    print("   2. Si falla, usar opción A")
    print()
    print("C) VERIFICAR CACHE SQLALCHEMY:")
    print("   1. Reiniciar completamente Python")
    print("   2. Eliminar archivos __pycache__")
    print("   3. Ejecutar: python run.py")

def main():
    """Función principal"""
    print_banner()
    
    # Verificar archivo
    if not check_database_file():
        return 1
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect('emergency_system.db')
        print("OK: Conexión SQLite exitosa")
    except Exception as e:
        print(f"ERROR: No se puede conectar a la base de datos - {e}")
        return 1
    
    # Inspeccionar tabla usuarios
    usuarios_ok = inspect_table_structure(conn, 'usuarios')
    
    # Inspeccionar tabla personas
    personas_ok = inspect_table_structure(conn, 'personas')
    
    # Probar consultas directas
    sql_ok = test_direct_sql_query(conn)
    
    # Verificar integridad
    integrity_ok = check_database_integrity(conn)
    
    conn.close()
    
    # Probar SQLAlchemy
    sqlalchemy_ok = test_sqlalchemy_connection()
    
    # Mostrar resumen
    print(f"\n" + "=" * 60)
    print("RESUMEN DEL DIAGNOSTICO")
    print("=" * 60)
    
    print(f"Archivo BD:        {'OK' if True else 'ERROR'}")
    print(f"Tabla usuarios:    {'OK' if usuarios_ok else 'ERROR'}")
    print(f"Tabla personas:    {'OK' if personas_ok else 'ERROR'}")
    print(f"Consultas SQL:     {'OK' if sql_ok else 'ERROR'}")
    print(f"Integridad BD:     {'OK' if integrity_ok else 'ERROR'}")
    print(f"SQLAlchemy:        {'OK' if sqlalchemy_ok else 'ERROR'}")
    
    if all([usuarios_ok, personas_ok, sql_ok, integrity_ok, sqlalchemy_ok]):
        print("\nOK: Base de datos parece estar correcta")
        print("    El problema puede ser de cache o configuración")
    else:
        print("\nERROR: Se encontraron problemas en la base de datos")
        suggest_solution()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())