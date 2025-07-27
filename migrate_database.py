#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Script de Migración Automática de Base de Datos

Este script verifica y migra automáticamente la base de datos
a la nueva estructura, agregando campos faltantes y manteniendo datos existentes.
"""

import sqlite3
import os
import shutil
from datetime import datetime
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)

class DatabaseMigrator:
    def __init__(self, db_path='emergency_system.db'):
        self.db_path = db_path
        self.backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Crear backup de la base de datos antes de migrar"""
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, self.backup_path)
                logging.info(f"✅ Backup creado: {self.backup_path}")
                return True
            else:
                logging.info("ℹ️  Base de datos nueva, no se necesita backup")
                return True
        except Exception as e:
            logging.error(f"❌ Error creando backup: {e}")
            return False
    
    def check_table_exists(self, conn, table_name):
        """Verificar si una tabla existe"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None
    
    def check_column_exists(self, conn, table_name, column_name):
        """Verificar si una columna existe en una tabla"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
    
    def add_column_if_not_exists(self, conn, table_name, column_name, column_definition):
        """Agregar columna si no existe"""
        if not self.check_column_exists(conn, table_name, column_name):
            try:
                cursor = conn.cursor()
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
                conn.commit()
                logging.info(f"✅ Columna '{column_name}' agregada a tabla '{table_name}'")
                return True
            except Exception as e:
                logging.error(f"❌ Error agregando columna '{column_name}': {e}")
                return False
        else:
            logging.info(f"ℹ️  Columna '{column_name}' ya existe en '{table_name}'")
            return True
    
    def migrate_personas_table(self, conn):
        """Migrar tabla personas agregando campo email"""
        logging.info("🔄 Migrando tabla 'personas'...")
        
        # Verificar si la tabla existe
        if not self.check_table_exists(conn, 'personas'):
            logging.info("ℹ️  Tabla 'personas' no existe, se creará con la nueva estructura")
            return True
        
        # Agregar campo email si no existe
        success = self.add_column_if_not_exists(
            conn, 
            'personas', 
            'email', 
            'VARCHAR(120)'
        )
        
        return success
    
    def migrate_usuarios_table(self, conn):
        """Migrar tabla usuarios agregando campos de seguridad"""
        logging.info("🔄 Migrando tabla 'usuarios'...")
        
        if not self.check_table_exists(conn, 'usuarios'):
            logging.info("ℹ️  Tabla 'usuarios' no existe, se creará con la nueva estructura")
            return True
        
        # Agregar campos de seguridad
        success = True
        
        success &= self.add_column_if_not_exists(
            conn, 'usuarios', 'intentos_login', 'INTEGER DEFAULT 0'
        )
        
        success &= self.add_column_if_not_exists(
            conn, 'usuarios', 'bloqueado_hasta', 'DATETIME'
        )
        
        return success
    
    def update_configuracion_table(self, conn):
        """Actualizar tabla configuración con nuevos campos"""
        logging.info("🔄 Actualizando tabla 'configuracion'...")
        
        if not self.check_table_exists(conn, 'configuracion'):
            logging.info("ℹ️  Tabla 'configuracion' no existe, se creará con la nueva estructura")
            return True
        
        # Agregar campo categoria si no existe
        success = self.add_column_if_not_exists(
            conn, 'configuracion', 'categoria', 'VARCHAR(50)'
        )
        
        return success
    
    def insert_default_configurations(self, conn):
        """Insertar configuraciones por defecto si no existen"""
        logging.info("🔄 Verificando configuraciones por defecto...")
        
        cursor = conn.cursor()
        
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
            ('logo_sistema', '', 'Logo del sistema', 'general'),
            ('version_sistema', '2.0.0', 'Versión actual del sistema', 'general'),
            ('fecha_instalacion', datetime.now().isoformat(), 'Fecha de instalación', 'general')
        ]
        
        for clave, valor, descripcion, categoria in default_configs:
            try:
                # Verificar si la configuración ya existe
                cursor.execute("SELECT id FROM configuracion WHERE clave = ?", (clave,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO configuracion (clave, valor, descripcion, categoria)
                        VALUES (?, ?, ?, ?)
                    """, (clave, valor, descripcion, categoria))
                    logging.info(f"✅ Configuración '{clave}' agregada")
            except Exception as e:
                logging.error(f"❌ Error agregando configuración '{clave}': {e}")
        
        conn.commit()
        return True
    
    def verify_database_integrity(self, conn):
        """Verificar integridad de la base de datos después de la migración"""
        logging.info("🔍 Verificando integridad de la base de datos...")
        
        checks = []
        cursor = conn.cursor()
        
        # Verificar que todas las tablas principales existan
        required_tables = ['usuarios', 'llamados', 'personas', 'guardias', 
                          'observaciones', 'servicios_comisionados', 'configuracion']
        
        for table in required_tables:
            if self.check_table_exists(conn, table):
                checks.append(f"✅ Tabla '{table}' existe")
            else:
                checks.append(f"❌ Tabla '{table}' faltante")
        
        # Verificar campo email en personas
        if self.check_column_exists(conn, 'personas', 'email'):
            checks.append("✅ Campo 'email' existe en tabla 'personas'")
        else:
            checks.append("❌ Campo 'email' faltante en tabla 'personas'")
        
        # Verificar usuario admin
        try:
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin' AND activo = 1")
            admin_count = cursor.fetchone()[0]
            if admin_count > 0:
                checks.append(f"✅ {admin_count} usuario(s) admin activo(s)")
            else:
                checks.append("⚠️  No hay usuarios admin activos")
        except Exception as e:
            checks.append(f"❌ Error verificando usuarios admin: {e}")
        
        # Mostrar resultados
        for check in checks:
            logging.info(check)
        
        return all("✅" in check for check in checks if not check.startswith("⚠️"))
    
    def run_migration(self):
        """Ejecutar migración completa"""
        logging.info("🚀 Iniciando migración de base de datos...")
        logging.info("=" * 60)
        
        try:
            # Crear backup
            if not self.create_backup():
                return False
            
            # Conectar a la base de datos
            conn = sqlite3.connect(self.db_path)
            
            # Ejecutar migraciones
            migrations = [
                ("personas", self.migrate_personas_table),
                ("usuarios", self.migrate_usuarios_table),
                ("configuracion", self.update_configuracion_table),
                ("configuraciones por defecto", self.insert_default_configurations)
            ]
            
            for name, migration_func in migrations:
                logging.info(f"🔄 Ejecutando migración: {name}")
                if not migration_func(conn):
                    logging.error(f"❌ Error en migración: {name}")
                    conn.close()
                    return False
            
            # Verificar integridad
            if not self.verify_database_integrity(conn):
                logging.warning("⚠️  Algunas verificaciones de integridad fallaron")
            
            conn.close()
            
            logging.info("=" * 60)
            logging.info("✅ Migración completada exitosamente")
            logging.info(f"📁 Backup disponible en: {self.backup_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error durante la migración: {e}")
            
            # Intentar restaurar backup si algo salió mal
            if os.path.exists(self.backup_path):
                try:
                    shutil.copy2(self.backup_path, self.db_path)
                    logging.info("🔄 Base de datos restaurada desde backup")
                except Exception as restore_error:
                    logging.error(f"❌ Error restaurando backup: {restore_error}")
            
            return False

def main():
    """Función principal"""
    print("🚨 SISTEMA DE EMERGENCIAS VILLA ALLENDE")
    print("   Script de Migración de Base de Datos")
    print("=" * 60)
    
    # Verificar si existe la base de datos o crear una nueva
    db_path = 'emergency_system.db'
    
    migrator = DatabaseMigrator(db_path)
    
    if migrator.run_migration():
        print("\n✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("   La base de datos está lista para usar.")
    else:
        print("\n❌ ERROR EN LA MIGRACIÓN")
        print("   Revise los logs para más detalles.")
        sys.exit(1)

if __name__ == '__main__':
    main()