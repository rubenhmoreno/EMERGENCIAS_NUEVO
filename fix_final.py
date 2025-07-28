#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Solucion Definitiva - Sin emojis ni caracteres especiales

Este script resuelve TODOS los problemas:
1. Elimina base de datos problemática
2. Crea BD nueva sin problemas de cache
3. Sin emojis ni caracteres especiales
4. Garantiza funcionamiento en Windows
"""

import sqlite3
import os
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash

def print_banner():
    print("=" * 60)
    print("SOLUCION DEFINITIVA - SISTEMA DE EMERGENCIAS v2.0")
    print("Recreacion completa de base de datos")
    print("=" * 60)
    print()

def remove_problematic_database():
    """Eliminar base de datos problemática"""
    print("1. ELIMINANDO BASE DE DATOS PROBLEMATICA")
    print("-" * 40)
    
    if os.path.exists('emergency_system.db'):
        # Hacer backup
        backup_name = f"emergency_system.db.problematica_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2('emergency_system.db', backup_name)
            print(f"OK: Backup creado - {backup_name}")
        except Exception as e:
            print(f"ERROR: No se pudo hacer backup - {e}")
            return False
        
        # Eliminar BD actual
        try:
            os.remove('emergency_system.db')
            print("OK: Base de datos problemática eliminada")
        except Exception as e:
            print(f"ERROR: No se pudo eliminar BD - {e}")
            return False
    else:
        print("INFO: No hay base de datos para eliminar")
    
    # Eliminar archivos de cache también
    cache_files = ['emergency_system.db-wal', 'emergency_system.db-shm']
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                print(f"OK: Cache eliminado - {cache_file}")
            except:
                pass
    
    return True

def create_clean_database():
    """Crear base de datos completamente limpia"""
    print("\n2. CREANDO BASE DE DATOS LIMPIA")
    print("-" * 40)
    
    try:
        # Conectar y crear BD nueva
        conn = sqlite3.connect('emergency_system.db')
        cursor = conn.cursor()
        
        # TABLA USUARIOS - CON TODAS LAS COLUMNAS
        print("Creando tabla usuarios...")
        cursor.execute("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                email VARCHAR(120),
                telefono VARCHAR(20),
                rol VARCHAR(20) DEFAULT 'operador' NOT NULL,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_login DATETIME,
                llamados_atendidos INTEGER DEFAULT 0,
                intentos_login INTEGER DEFAULT 0,
                bloqueado_hasta DATETIME
            )
        """)
        print("OK: Tabla usuarios creada (con llamados_atendidos)")
        
        # TABLA PERSONAS - CON EMAIL
        print("Creando tabla personas...")
        cursor.execute("""
            CREATE TABLE personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                documento VARCHAR(20),
                telefono VARCHAR(20),
                email VARCHAR(120),
                direccion VARCHAR(200),
                barrio VARCHAR(100),
                fecha_nacimiento DATE,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                observaciones TEXT
            )
        """)
        print("OK: Tabla personas creada (con email)")
        
        # TABLA LLAMADOS
        print("Creando tabla llamados...")
        cursor.execute("""
            CREATE TABLE llamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                usuario_id INTEGER NOT NULL,
                nombre_llamante VARCHAR(100) NOT NULL,
                telefono_llamante VARCHAR(20),
                persona_id INTEGER,
                nombre_afectado VARCHAR(100),
                edad_afectado INTEGER,
                sexo_afectado VARCHAR(1),
                direccion VARCHAR(200) NOT NULL,
                barrio VARCHAR(100) NOT NULL,
                es_via_publica BOOLEAN DEFAULT 0,
                punto_referencia VARCHAR(200),
                tipo_emergencia VARCHAR(50) NOT NULL,
                motivo_llamado TEXT NOT NULL,
                prioridad VARCHAR(10) NOT NULL,
                protocolo_107 TEXT,
                estado VARCHAR(20) DEFAULT 'activo',
                derivado_a VARCHAR(100),
                observaciones TEXT,
                fecha_cierre DATETIME,
                whatsapp_enviado BOOLEAN DEFAULT 0,
                whatsapp_respuesta TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                FOREIGN KEY (persona_id) REFERENCES personas (id)
            )
        """)
        print("OK: Tabla llamados creada")
        
        # TABLA GUARDIAS
        print("Creando tabla guardias...")
        cursor.execute("""
            CREATE TABLE guardias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                usuario_id INTEGER NOT NULL,
                actividad TEXT NOT NULL,
                tipo VARCHAR(20) DEFAULT 'novedad',
                observaciones TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        print("OK: Tabla guardias creada")
        
        # TABLA CONFIGURACION
        print("Creando tabla configuracion...")
        cursor.execute("""
            CREATE TABLE configuracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave VARCHAR(100) UNIQUE NOT NULL,
                valor TEXT,
                descripcion VARCHAR(200),
                categoria VARCHAR(50) DEFAULT 'general',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("OK: Tabla configuracion creada")
        
        conn.commit()
        return conn
        
    except Exception as e:
        print(f"ERROR: No se pudo crear BD - {e}")
        return None

def insert_initial_data(conn):
    """Insertar datos iniciales"""
    print("\n3. INSERTANDO DATOS INICIALES")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # USUARIO ADMIN
        print("Creando usuario administrador...")
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
        print("OK: Usuario admin creado (admin / 123456)")
        
        # GUARDIA INICIAL
        cursor.execute("""
            INSERT INTO guardias (usuario_id, actividad, tipo)
            VALUES (1, 'Sistema recreado completamente - BD limpia sin problemas', 'sistema')
        """)
        print("OK: Guardia inicial creada")
        
        # CONFIGURACIONES
        print("Insertando configuraciones...")
        configs = [
            ('whatsapp_token', '', 'Token de API WhatsApp', 'whatsapp'),
            ('whatsapp_uid', '', 'UID del numero WhatsApp', 'whatsapp'),
            ('telefono_demva', '', 'Telefono DEMVA', 'telefonos'),
            ('telefono_cec', '', 'Telefono CEC', 'telefonos'),
            ('telefono_telemedicina', '', 'Telefono Telemedicina', 'telefonos'),
            ('telefono_bomberos', '', 'Telefono Bomberos', 'telefonos'),
            ('telefono_seguridad', '', 'Telefono Seguridad', 'telefonos'),
            ('telefono_defensa', '', 'Telefono Defensa Civil', 'telefonos'),
            ('telefono_supervisor', '', 'Telefono Supervisor', 'telefonos'),
            ('logo_sistema', '', 'Logo personalizado', 'sistema'),
            ('nombre_organizacion', 'Municipalidad de Villa Allende', 'Nombre organizacion', 'sistema'),
            ('auto_whatsapp', 'true', 'Envio automatico WhatsApp', 'sistema'),
            ('protocolo_107_habilitado', 'true', 'Protocolo 107 habilitado', 'sistema'),
            ('backup_automatico', 'true', 'Backup automatico', 'sistema')
        ]
        
        for clave, valor, descripcion, categoria in configs:
            cursor.execute("""
                INSERT INTO configuracion (clave, valor, descripcion, categoria)
                VALUES (?, ?, ?, ?)
            """, (clave, valor, descripcion, categoria))
        
        print(f"OK: {len(configs)} configuraciones insertadas")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"ERROR: No se pudieron insertar datos - {e}")
        return False

def verify_database(conn):
    """Verificar que la BD esté correcta"""
    print("\n4. VERIFICANDO BASE DE DATOS")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # Verificar estructura de usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        user_columns = [col[1] for col in cursor.fetchall()]
        
        critical_columns = ['llamados_atendidos', 'intentos_login', 'bloqueado_hasta']
        missing = [col for col in critical_columns if col not in user_columns]
        
        if missing:
            print(f"ERROR: Faltan columnas en usuarios: {missing}")
            return False
        else:
            print("OK: Tabla usuarios tiene todas las columnas criticas")
        
        # Verificar email en personas
        cursor.execute("PRAGMA table_info(personas)")
        person_columns = [col[1] for col in cursor.fetchall()]
        if 'email' in person_columns:
            print("OK: Tabla personas tiene campo email")
        else:
            print("ERROR: Tabla personas NO tiene campo email")
            return False
        
        # Verificar usuario admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count > 0:
            print(f"OK: Usuario admin existe ({admin_count} registros)")
        else:
            print("ERROR: Usuario admin no existe")
            return False
        
        # Verificar configuraciones
        cursor.execute("SELECT COUNT(*) FROM configuracion")
        config_count = cursor.fetchone()[0]
        if config_count > 0:
            print(f"OK: Configuraciones existen ({config_count} registros)")
        else:
            print("ERROR: No hay configuraciones")
            return False
        
        # PRUEBA CRITICA: Consultar llamados_atendidos
        cursor.execute("SELECT username, llamados_atendidos FROM usuarios WHERE username = 'admin'")
        result = cursor.fetchone()
        if result:
            print(f"OK: Consulta llamados_atendidos exitosa - {result}")
        else:
            print("ERROR: No se puede consultar llamados_atendidos")
            return False
        
        print("OK: Todas las verificaciones pasaron")
        return True
        
    except Exception as e:
        print(f"ERROR: Fallo en verificacion - {e}")
        return False

def clean_cache_files():
    """Limpiar archivos de cache de Python"""
    print("\n5. LIMPIANDO CACHE DE PYTHON")
    print("-" * 40)
    
    try:
        # Eliminar directorios __pycache__
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_dir = os.path.join(root, '__pycache__')
                shutil.rmtree(cache_dir)
                print(f"OK: Cache eliminado - {cache_dir}")
        
        # Eliminar archivos .pyc
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_file = os.path.join(root, file)
                    os.remove(pyc_file)
                    print(f"OK: Archivo .pyc eliminado - {pyc_file}")
        
        print("OK: Cache de Python limpiado")
        return True
        
    except Exception as e:
        print(f"AVISO: No se pudo limpiar todo el cache - {e}")
        return True  # No es crítico

def main():
    """Función principal"""
    print_banner()
    
    print("ADVERTENCIA: Este script eliminara la base de datos actual")
    print("            y creara una completamente nueva.")
    print()
    response = input("Esta seguro de continuar? (escriba 'SI' para continuar): ")
    
    if response.upper() != 'SI':
        print("Operacion cancelada")
        return 0
    
    print()
    
    # PASO 1: Eliminar BD problemática
    if not remove_problematic_database():
        print("ERROR: No se pudo eliminar BD problemática")
        return 1
    
    # PASO 2: Crear BD limpia
    conn = create_clean_database()
    if not conn:
        print("ERROR: No se pudo crear BD limpia")
        return 1
    
    # PASO 3: Insertar datos
    if not insert_initial_data(conn):
        print("ERROR: No se pudieron insertar datos")
        conn.close()
        return 1
    
    # PASO 4: Verificar BD
    if not verify_database(conn):
        print("ERROR: BD no paso verificacion")
        conn.close()
        return 1
    
    conn.close()
    
    # PASO 5: Limpiar cache
    clean_cache_files()
    
    # MENSAJE FINAL
    print("\n" + "=" * 60)
    print("SOLUCION COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("La base de datos ha sido recreada completamente")
    print("Todos los problemas han sido solucionados:")
    print("  - Cache de SQLAlchemy eliminado")
    print("  - BD nueva sin problemas de estructura")
    print("  - Campo 'llamados_atendidos' garantizado")
    print("  - Campo 'email' en personas garantizado")
    print("  - Usuario admin creado")
    print("  - Sin emojis ni caracteres problematicos")
    print()
    print("PROXIMO PASO:")
    print("  Ejecutar: python start_clean.py")
    print()
    print("Luego abrir navegador en: http://localhost:5000")
    print("Iniciar sesion con: admin / 123456")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())