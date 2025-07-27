#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Utilidad de Backup y Restauración

Funcionalidades:
- Backup completo de base de datos SQLite
- Exportación a CSV de todas las tablas
- Backup de configuración y archivos subidos
- Restauración completa desde backup
- Verificación de integridad
"""

import os
import shutil
import sqlite3
import json
import csv
import zipfile
from datetime import datetime
import logging
from io import StringIO

class BackupManager:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.backup_dir = 'backups'
        self.db_path = 'emergency_system.db'
        
        # Crear directorio de backup si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self, include_uploads=True):
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"emergency_backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            self.logger.info(f"Iniciando backup: {backup_filename}")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # 1. Backup de base de datos SQLite
                if os.path.exists(self.db_path):
                    backup_zip.write(self.db_path, 'emergency_system.db')
                    self.logger.info("✅ Base de datos agregada al backup")
                
                # 2. Exportar datos a CSV
                csv_data = self._export_csv_data()
                for table_name, csv_content in csv_data.items():
                    if csv_content:
                        backup_zip.writestr(f'csv_export/{table_name}.csv', csv_content)
                self.logger.info("✅ Datos CSV exportados")
                
                # 3. Backup de configuración
                config_data = self._export_configuration()
                backup_zip.writestr('configuration.json', json.dumps(config_data, indent=2, ensure_ascii=False))
                self.logger.info("✅ Configuración exportada")
                
                # 4. Backup de archivos subidos (logos, etc.)
                if include_uploads and os.path.exists('static/uploads'):
                    for root, dirs, files in os.walk('static/uploads'):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = os.path.join('uploads', os.path.relpath(file_path, 'static/uploads'))
                            backup_zip.write(file_path, arc_path)
                    self.logger.info("✅ Archivos subidos agregados")
                
                # 5. Metadatos del backup
                metadata = {
                    'timestamp': timestamp,
                    'version': '2.0.0',
                    'backup_type': 'complete',
                    'includes_uploads': include_uploads,
                    'record_counts': self._get_record_counts()
                }
                backup_zip.writestr('metadata.json', json.dumps(metadata, indent=2))
                self.logger.info("✅ Metadatos agregados")
            
            self.logger.info(f"✅ Backup completado: {backup_path}")
            return {
                'success': True,
                'backup_file': backup_filename,
                'backup_path': backup_path,
                'size': os.path.getsize(backup_path)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creando backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_backup(self, backup_file):
        """Restaurar backup completo"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Archivo de backup no encontrado: {backup_file}")
            
            self.logger.info(f"Iniciando restauración: {backup_file}")
            
            # Crear backup de seguridad antes de restaurar
            safety_backup = self.create_backup(include_uploads=True)
            if not safety_backup['success']:
                raise Exception("No se pudo crear backup de seguridad")
            
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # Verificar que es un backup válido
                if 'metadata.json' not in backup_zip.namelist():
                    raise Exception("Archivo de backup inválido: falta metadata.json")
                
                # Leer metadatos
                metadata = json.loads(backup_zip.read('metadata.json'))
                self.logger.info(f"Restaurando backup del {metadata['timestamp']}")
                
                # 1. Restaurar base de datos
                if 'emergency_system.db' in backup_zip.namelist():
                    # Cerrar conexiones existentes
                    if self.db:
                        self.db.session.close()
                    
                    # Backup de BD actual
                    if os.path.exists(self.db_path):
                        shutil.copy2(self.db_path, f"{self.db_path}.restore_backup")
                    
                    # Restaurar BD
                    with open(self.db_path, 'wb') as db_file:
                        db_file.write(backup_zip.read('emergency_system.db'))
                    
                    self.logger.info("✅ Base de datos restaurada")
                
                # 2. Restaurar archivos subidos
                if metadata.get('includes_uploads', False):
                    uploads_dir = 'static/uploads'
                    
                    # Limpiar directorio actual
                    if os.path.exists(uploads_dir):
                        shutil.rmtree(uploads_dir)
                    os.makedirs(uploads_dir, exist_ok=True)
                    
                    # Restaurar archivos
                    for file_info in backup_zip.infolist():
                        if file_info.filename.startswith('uploads/'):
                            relative_path = file_info.filename[8:]  # Quitar 'uploads/'
                            target_path = os.path.join(uploads_dir, relative_path)
                            
                            # Crear directorios si es necesario
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            
                            # Extraer archivo
                            with backup_zip.open(file_info) as source:
                                with open(target_path, 'wb') as target:
                                    target.write(source.read())
                    
                    self.logger.info("✅ Archivos subidos restaurados")
            
            # Verificar integridad después de la restauración
            integrity_check = self.verify_database_integrity()
            
            self.logger.info("✅ Restauración completada exitosamente")
            return {
                'success': True,
                'safety_backup': safety_backup['backup_file'],
                'integrity_check': integrity_check
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando backup: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self):
        """Listar todos los backups disponibles"""
        try:
            backups = []
            
            if not os.path.exists(self.backup_dir):
                return backups
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.zip') and filename.startswith('emergency_backup_'):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_stats = os.stat(file_path)
                    
                    # Intentar leer metadatos
                    metadata = {}
                    try:
                        with zipfile.ZipFile(file_path, 'r') as backup_zip:
                            if 'metadata.json' in backup_zip.namelist():
                                metadata = json.loads(backup_zip.read('metadata.json'))
                    except:
                        pass
                    
                    backups.append({
                        'filename': filename,
                        'size': file_stats.st_size,
                        'created': datetime.fromtimestamp(file_stats.st_ctime),
                        'metadata': metadata
                    })
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
            return []
    
    def delete_backup(self, backup_file):
        """Eliminar un backup específico"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            if os.path.exists(backup_path):
                os.remove(backup_path)
                self.logger.info(f"Backup eliminado: {backup_file}")
                return {'success': True}
            else:
                return {'success': False, 'error': 'Archivo no encontrado'}
                
        except Exception as e:
            self.logger.error(f"Error eliminando backup: {e}")
            return {'success': False, 'error': str(e)}
    
    def _export_configuration(self):
        """Exportar configuración del sistema"""
        config_data = {
            'export_timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'configurations': {}
        }
        
        if self.app:
            with self.app.app_context():
                try:
                    from models import Configuracion
                    configs = Configuracion.query.all()
                    
                    config_data['configurations'] = {
                        config.clave: {
                            'valor': config.valor,
                            'descripcion': config.descripcion,
                            'categoria': config.categoria
                        } for config in configs
                    }
                except Exception as e:
                    self.logger.warning(f"No se pudo exportar configuración: {e}")
        
        return config_data
    
    def _export_csv_data(self):
        """Exportar datos en formato CSV"""
        csv_data = {}
        
        if not self.app:
            return csv_data
        
        with self.app.app_context():
            try:
                from models import Usuario, Llamado, Persona, Guardia, Observacion, ServicioComisionado, Configuracion
                
                # Exportar usuarios (sin contraseñas)
                usuarios = Usuario.query.all()
                csv_data['usuarios'] = self._to_csv([{
                    'id': u.id,
                    'username': u.username,
                    'nombre': u.nombre,
                    'apellido': u.apellido,
                    'email': u.email,
                    'telefono': u.telefono,
                    'rol': u.rol,
                    'activo': u.activo,
                    'fecha_creacion': u.fecha_creacion.isoformat() if u.fecha_creacion else '',
                    'ultimo_login': u.ultimo_login.isoformat() if u.ultimo_login else '',
                    'llamados_atendidos': u.llamados_atendidos
                } for u in usuarios])
                
                # Exportar llamados
                llamados = Llamado.query.all()
                csv_data['llamados'] = self._to_csv([{
                    'id': l.id,
                    'fecha': l.fecha.isoformat(),
                    'usuario_id': l.usuario_id,
                    'telefono': l.telefono,
                    'nombre': l.nombre,
                    'apellido': l.apellido,
                    'dni': l.dni,
                    'calle': l.calle,
                    'numero': l.numero,
                    'entre_calles': l.entre_calles,
                    'barrio': l.barrio,
                    'observaciones_iniciales': l.observaciones_iniciales,
                    'tipo': l.tipo,
                    'prioridad': l.prioridad,
                    'via_publica': l.via_publica,
                    'estado': l.estado,
                    'whatsapp_enviado': l.whatsapp_enviado,
                    'movil_en_domicilio': l.movil_en_domicilio,
                    'fecha_movil_domicilio': l.fecha_movil_domicilio.isoformat() if l.fecha_movil_domicilio else '',
                    'fecha_cierre': l.fecha_cierre.isoformat() if l.fecha_cierre else '',
                    'triage_data': l.triage_data
                } for l in llamados])
                
                # Exportar personas (CON EMAIL)
                personas = Persona.query.all()
                csv_data['personas'] = self._to_csv([{
                    'id': p.id,
                    'apellido': p.apellido,
                    'nombre': p.nombre,
                    'dni': p.dni,
                    'telefono': p.telefono,
                    'celular': p.celular,
                    'email': p.email,  # *** CAMPO EMAIL INCLUIDO ***
                    'direccion': p.direccion,
                    'barrio': p.barrio,
                    'observaciones': p.observaciones,
                    'fecha_creacion': p.fecha_creacion.isoformat() if p.fecha_creacion else '',
                    'fecha_modificacion': p.fecha_modificacion.isoformat() if p.fecha_modificacion else '',
                    'activo': p.activo
                } for p in personas])
                
                # Exportar guardias
                guardias = Guardia.query.all()
                csv_data['guardias'] = self._to_csv([{
                    'id': g.id,
                    'fecha': g.fecha.isoformat(),
                    'usuario_id': g.usuario_id,
                    'actividad': g.actividad,
                    'tipo': g.tipo
                } for g in guardias])
                
                # Exportar observaciones
                observaciones = Observacion.query.all()
                csv_data['observaciones'] = self._to_csv([{
                    'id': o.id,
                    'llamado_id': o.llamado_id,
                    'usuario_id': o.usuario_id,
                    'fecha': o.fecha.isoformat(),
                    'texto': o.texto
                } for o in observaciones])
                
                # Exportar servicios comisionados
                servicios = ServicioComisionado.query.all()
                csv_data['servicios_comisionados'] = self._to_csv([{
                    'id': s.id,
                    'llamado_id': s.llamado_id,
                    'usuario_id': s.usuario_id,
                    'fecha': s.fecha.isoformat(),
                    'tipo_servicio': s.tipo_servicio,
                    'motivo': s.motivo,
                    'estado': s.estado
                } for s in servicios])
                
                # Exportar configuración
                configs = Configuracion.query.all()
                csv_data['configuracion'] = self._to_csv([{
                    'id': c.id,
                    'clave': c.clave,
                    'valor': c.valor,
                    'descripcion': c.descripcion,
                    'categoria': c.categoria,
                    'fecha_modificacion': c.fecha_modificacion.isoformat() if c.fecha_modificacion else ''
                } for c in configs])
                
            except Exception as e:
                self.logger.error(f"Error exportando datos CSV: {e}")
        
        return csv_data
    
    def _to_csv(self, data):
        """Convertir lista de diccionarios a CSV"""
        if not data:
            return ""
        
        output = StringIO()
        fieldnames = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def _get_record_counts(self):
        """Obtener conteo de registros por tabla"""
        counts = {}
        
        if self.app:
            with self.app.app_context():
                try:
                    from models import Usuario, Llamado, Persona, Guardia, Observacion, ServicioComisionado, Configuracion
                    
                    counts = {
                        'usuarios': Usuario.query.count(),
                        'llamados': Llamado.query.count(),
                        'personas': Persona.query.count(),
                        'guardias': Guardia.query.count(),
                        'observaciones': Observacion.query.count(),
                        'servicios_comisionados': ServicioComisionado.query.count(),
                        'configuracion': Configuracion.query.count()
                    }
                except Exception as e:
                    self.logger.warning(f"No se pudo obtener conteo de registros: {e}")
        
        return counts
    
    def verify_database_integrity(self):
        """Verificar integridad de la base de datos"""
        issues = []
        
        try:
            # Verificar que el archivo de BD existe
            if not os.path.exists(self.db_path):
                issues.append("Archivo de base de datos no encontrado")
                return {'valid': False, 'issues': issues}
            
            # Verificar que se puede conectar
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar estructura de tablas
            required_tables = ['usuarios', 'llamados', 'personas', 'guardias', 
                             'observaciones', 'servicios_comisionados', 'configuracion']
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table not in existing_tables:
                    issues.append(f"Tabla faltante: {table}")
            
            # Verificar que existe al menos un admin
            try:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin' AND activo = 1")
                admin_count = cursor.fetchone()[0]
                if admin_count == 0:
                    issues.append("No hay usuarios administradores activos")
            except:
                issues.append("Error verificando usuarios administradores")
            
            # Verificar campo email en personas
            try:
                cursor.execute("PRAGMA table_info(personas)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'email' not in columns:
                    issues.append("Campo 'email' faltante en tabla personas")
            except:
                issues.append("Error verificando estructura de tabla personas")
            
            conn.close()
            
        except Exception as e:
            issues.append(f"Error verificando integridad: {str(e)}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

# Script principal para uso independiente
if __name__ == '__main__':
    import sys
    
    backup_manager = BackupManager()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'create':
            result = backup_manager.create_backup()
            if result['success']:
                print(f"✅ Backup creado: {result['backup_file']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif action == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print("📋 Backups disponibles:")
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    print(f"  • {backup['filename']} ({size_mb:.1f} MB) - {backup['created']}")
            else:
                print("No hay backups disponibles")
        
        elif action == 'verify':
            integrity = backup_manager.verify_database_integrity()
            if integrity['valid']:
                print("✅ Base de datos íntegra")
            else:
                print("❌ Problemas de integridad:")
                for issue in integrity['issues']:
                    print(f"  • {issue}")
        
        else:
            print("Acciones disponibles: create, list, verify")
    else:
        print("Uso: python backup.py [create|list|verify]")
