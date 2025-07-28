#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Recrear Base de Datos Desde Cero

Este script elimina la base de datos problemática y crea una nueva
con la estructura correcta garantizada.
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

def print_banner():
    print("=" * 60)
    print("RECREAR BASE DE DATOS DESDE CERO")
    print("Sistema de Emergencias Villa Allende v2.0")
    print("=" * 60)
    print()

def backup_current_database():
    """Hacer backup de la base de datos actual"""
    print("1. HACIENDO BACKUP DE BASE DE DATOS ACTUAL")
    print("-" * 40)
    
    if os.path.exists('emergency_system.db'):
        backup_name = f"emergency_system.db.broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2('emergency_system.db', backup_name)
            print(f"OK: Backup creado - {backup_name}")
            
            # Eliminar base de datos actual
            os.remove('emergency_system.db')
            print("OK: Base de datos problemática eliminada")
            return True
        except Exception as e:
            print(f"ERROR: No se pudo hacer backup - {e}")
            return False
    else:
        print("INFO: No hay base de datos actual para respaldar")
        return True

def create_fresh_database():
    """Crear base de datos completamente nueva"""
    print("\n2. CREANDO BASE DE DATOS NUEVA")
    print("-" * 40)
    
    try:
        conn = sqlite3.connect('emergency_system.db')
        cursor = conn.cursor()
        
        # Crear tabla usuarios CON TODAS LAS COLUMNAS
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
        print("OK: Tabla usuarios creada")
        
        # Crear tabla personas CON CAMPO EMAIL
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
        print("OK: Tabla personas creada")
        
        # Crear tabla llamados
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
        
        # Crear tabla guardias
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
        
        # Crear tabla configuracion
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
        print(f"ERROR: No se pudo crear la base de datos - {e}")
        return None

def insert_initial_data(conn):
    """Insertar datos iniciales garantizados"""
    print("\n3. INSERTANDO DATOS INICIALES")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # Crear usuario admin
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
        print("OK: Usuario admin creado")
        
        # Crear guardia de inicialización
        cursor.execute("""
            INSERT INTO guardias (usuario_id, actividad, tipo)
            VALUES (1, 'Sistema recreado desde cero - Base de datos nueva', 'sistema')
        """)
        print("OK: Guardia inicial creada")
        
        # Insertar configuraciones
        print("Insertando configuraciones por defecto...")
        default_configs = [
            ('whatsapp_token', '', 'Token de API WhatsApp', 'whatsapp'),
            ('whatsapp_uid', '', 'UID del número WhatsApp', 'whatsapp'),
            ('telefono_demva', '', 'Teléfono DEMVA', 'telefonos'),
            ('telefono_cec', '', 'Teléfono CEC', 'telefonos'),
            ('telefono_telemedicina', '', 'Teléfono Telemedicina', 'telefonos'),
            ('telefono_bomberos', '', 'Teléfono Bomberos', 'telefonos'),
            ('telefono_seguridad', '', 'Teléfono Seguridad', 'telefonos'),
            ('telefono_defensa', '', 'Teléfono Defensa Civil', 'telefonos'),
            ('telefono_supervisor', '', 'Teléfono Supervisor', 'telefonos'),
            ('logo_sistema', '', 'Logo personalizado', 'sistema'),
            ('nombre_organizacion', 'Municipalidad de Villa Allende', 'Nombre organización', 'sistema'),
            ('auto_whatsapp', 'true', 'Envío automático WhatsApp', 'sistema'),
            ('protocolo_107_habilitado', 'true', 'Protocolo 107 habilitado', 'sistema'),
            ('backup_automatico', 'true', 'Backup automático', 'sistema')
        ]
        
        for clave, valor, descripcion, categoria in default_configs:
            cursor.execute("""
                INSERT INTO configuracion (clave, valor, descripcion, categoria)
                VALUES (?, ?, ?, ?)
            """, (clave, valor, descripcion, categoria))
        
        print(f"OK: {len(default_configs)} configuraciones insertadas")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"ERROR: No se pudieron insertar datos iniciales - {e}")
        return False

def verify_new_database(conn):
    """Verificar que la nueva base de datos sea correcta"""
    print("\n4. VERIFICANDO NUEVA BASE DE DATOS")
    print("-" * 40)
    
    cursor = conn.cursor()
    
    try:
        # Verificar tabla usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        user_columns = [col[1] for col in cursor.fetchall()]
        required_user_columns = [
            'id', 'username', 'password_hash', 'nombre', 'apellido',
            'email', 'telefono', 'rol', 'activo', 'fecha_creacion',
            'ultimo_login', 'llamados_atendidos', 'intentos_login', 'bloqueado_hasta'
        ]
        
        missing_user_cols = [col for col in required_user_columns if col not in user_columns]
        if missing_user_cols:
            print(f"ERROR: Faltan columnas en usuarios: {missing_user_cols}")
            return False
        else:
            print("OK: Tabla usuarios tiene todas las columnas requeridas")
        
        # Verificar tabla personas
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
        
        # Probar consulta problemática específicamente
        cursor.execute("SELECT username, llamados_atendidos FROM usuarios WHERE username = 'admin'")
        result = cursor.fetchone()
        if result:
            print(f"OK: Consulta de 'llamados_atendidos' exitosa - {result}")
        else:
            print("ERROR: No se puede consultar llamados_atendidos")
            return False
        
        print("OK: Todas las verificaciones pasaron")
        return True
        
    except Exception as e:
        print(f"ERROR: Fallo en verificación - {e}")
        return False

def main():
    """Función principal"""
    print_banner()
    
    print("ADVERTENCIA: Este script eliminará la base de datos actual")
    print("            y creará una completamente nueva.")
    print()
    response = input("¿Está seguro de continuar? (escriba 'SI' para continuar): ")
    
    if response.upper() != 'SI':
        print("Operación cancelada por el usuario")
        return 0
    
    print()
    
    # Hacer backup y eliminar BD actual
    if not backup_current_database():
        print("ERROR: No se pudo hacer backup")
        return 1
    
    # Crear nueva base de datos
    conn = create_fresh_database()
    if not conn:
        print("ERROR: No se pudo crear nueva base de datos")
        return 1
    
    # Insertar datos iniciales
    if not insert_initial_data(conn):
        print("ERROR: No se pudieron insertar datos iniciales")
        conn.close()
        return 1
    
    # Verificar que todo esté correcto
    if not verify_new_database(conn):
        print("ERROR: La nueva base de datos no pasó las verificaciones")
        conn.close()
        return 1
    
    conn.close()
    
    # Mensaje de éxito
    print("\n" + "=" * 60)
    print("BASE DE DATOS RECREADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print("La base de datos ha sido recreada completamente")
    print("Estado actual:")
    print("  OK: Todas las tablas creadas correctamente")
    print("  OK: Campo 'email' en tabla personas")
    print("  OK: Campo 'llamados_atendidos' en tabla usuarios")
    print("  OK: Usuario admin creado (admin / 123456)")
    print("  OK: Configuraciones por defecto insertadas")
    print()
    print("Próximo paso:")
    print("  Ejecutar: python run.py")
    print()
    print("Luego abrir navegador en: http://localhost:5000")
    print("Iniciar sesión con: admin / 123456")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())