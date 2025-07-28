#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Reparación Rápida - Columna llamados_atendidos Faltante
Sistema de Emergencias Villa Allende v2.0

Este script agrega la columna faltante 'llamados_atendidos' en la tabla usuarios.
"""

import sqlite3
import os
from datetime import datetime

def print_banner():
    print("=" * 60)
    print("🔧 REPARACIÓN RÁPIDA - Columna llamados_atendidos")
    print("   Sistema de Emergencias Villa Allende v2.0")
    print("=" * 60)
    print()

def check_column_exists(conn, table_name, column_name):
    """Verificar si una columna existe en una tabla"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def add_missing_column(conn):
    """Agregar la columna llamados_atendidos si no existe"""
    print("🔍 Verificando columna llamados_atendidos en tabla usuarios...")
    
    if check_column_exists(conn, 'usuarios', 'llamados_atendidos'):
        print("✅ La columna 'llamados_atendidos' ya existe")
        return True
    
    try:
        print("➕ Agregando columna 'llamados_atendidos'...")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE usuarios ADD COLUMN llamados_atendidos INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Columna 'llamados_atendidos' agregada exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error agregando columna: {e}")
        return False

def verify_all_columns(conn):
    """Verificar que todas las columnas necesarias existan"""
    print("\n🔍 Verificando todas las columnas de la tabla usuarios...")
    
    required_columns = [
        'id', 'username', 'password_hash', 'nombre', 'apellido', 
        'email', 'telefono', 'rol', 'activo', 'fecha_creacion', 
        'ultimo_login', 'llamados_atendidos', 'intentos_login', 'bloqueado_hasta'
    ]
    
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(usuarios)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    missing_columns = []
    for col in required_columns:
        if col in existing_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANTE")
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n⚠️ Columnas faltantes: {', '.join(missing_columns)}")
        return False
    else:
        print("\n✅ Todas las columnas requeridas están presentes")
        return True

def create_admin_user_if_not_exists(conn):
    """Crear usuario admin si no existe"""
    print("\n👤 Verificando usuario administrador...")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    if admin_count > 0:
        print(f"✅ Usuario admin ya existe ({admin_count} registros)")
        return True
    
    try:
        print("➕ Creando usuario administrador...")
        from werkzeug.security import generate_password_hash
        
        password_hash = generate_password_hash('123456')
        cursor.execute("""
            INSERT INTO usuarios (
                username, password_hash, nombre, apellido, email, rol, 
                activo, llamados_atendidos, intentos_login
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'admin', password_hash, 'Administrador', 'Sistema', 
            'admin@villaallende.gov.ar', 'admin', 1, 0, 0
        ))
        
        conn.commit()
        print("✅ Usuario admin creado exitosamente")
        print("   Usuario: admin")
        print("   Contraseña: 123456")
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")
        return False

def main():
    """Función principal"""
    print_banner()
    
    # Verificar que existe la base de datos
    if not os.path.exists('emergency_system.db'):
        print("❌ Base de datos 'emergency_system.db' no encontrada")
        print("   Ejecute primero: python migrate_database.py")
        return 1
    
    # Hacer backup por seguridad
    backup_name = f"emergency_system.db.backup_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        import shutil
        shutil.copy2('emergency_system.db', backup_name)
        print(f"📁 Backup creado: {backup_name}")
    except Exception as e:
        print(f"⚠️ No se pudo crear backup: {e}")
    
    # Conectar a la base de datos
    try:
        conn = sqlite3.connect('emergency_system.db')
        print("✅ Conectado a la base de datos")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return 1
    
    # Agregar columna faltante
    if not add_missing_column(conn):
        conn.close()
        return 1
    
    # Verificar todas las columnas
    if not verify_all_columns(conn):
        conn.close()
        return 1
    
    # Crear usuario admin si no existe
    if not create_admin_user_if_not_exists(conn):
        conn.close()
        return 1
    
    conn.close()
    
    # Mensaje de éxito
    print("\n" + "=" * 60)
    print("✅ REPARACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("🎉 La base de datos ha sido reparada completamente")
    print("📊 Cambios realizados:")
    print("   ✅ Columna 'llamados_atendidos' agregada a tabla usuarios")
    print("   ✅ Usuario admin verificado/creado")
    print("   ✅ Estructura de base de datos completa")
    print()
    print("🚀 Próximo paso:")
    print("   Ejecutar: python run.py")
    print()
    print("🔗 Luego abrir navegador en: http://localhost:5000")
    print("👤 Iniciar sesión con: admin / 123456")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())