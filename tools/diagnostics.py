#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Herramientas de Diagnóstico Completas

Funcionalidades:
- Verificación completa del sistema
- Diagnóstico de base de datos
- Verificación de servicios Windows
- Test de conectividad y puertos
- Verificación de dependencias Python
- Diagnóstico de configuración WhatsApp
- Reparación automática de problemas
"""

import os
import sys
import psutil
import subprocess
import socket
import requests
import sqlite3
import json
import platform
import winreg
from datetime import datetime
import logging
import traceback

class SystemDiagnostics:
    def __init__(self):
        self.install_dir = os.path.abspath('.')
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'tests': {},
            'overall_status': 'UNKNOWN',
            'recommendations': []
        }
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_all_diagnostics(self):
        """Ejecutar todos los diagnósticos del sistema"""
        print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE EMERGENCIAS")
        print("=" * 70)
        print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"💻 Sistema: {platform.system()} {platform.release()}")
        print(f"📁 Directorio: {self.install_dir}")
        print("=" * 70)
        
        tests = [
            ('🗂️  Estructura de Archivos', self.check_file_structure),
            ('🐍 Python y Dependencias', self.check_python_dependencies),
            ('🗄️  Base de Datos', self.check_database),
            ('⚙️  Configuración', self.check_configuration),
            ('🔧 Servicios Windows', self.check_windows_services),
            ('🌐 Conectividad de Red', self.check_network_connectivity),
            ('🔐 Certificados SSL', self.check_ssl_certificates),
            ('🔥 Firewall', self.check_firewall),
            ('📱 WhatsApp', self.check_whatsapp_config),
            ('💾 Sistema de Backup', self.check_backup_system),
            ('🚀 Aplicación Web', self.check_web_application),
            ('📊 Rendimiento', self.check_performance)
        ]
        
        passed = 0
        warnings = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n{test_name}")
                print("-" * 50)
                
                result = test_func()
                self.results['tests'][test_name] = result
                
                status = result['status']
                message = result['message']
                
                if status == 'PASS':
                    print(f"✅ {message}")
                    passed += 1
                elif status == 'WARNING':
                    print(f"⚠️  {message}")
                    warnings += 1
                else:
                    print(f"❌ {message}")
                    failed += 1
                
                # Mostrar detalles si hay
                if result.get('details'):
                    for detail in result['details']:
                        print(f"   • {detail}")
                
                # Mostrar recomendaciones
                if result.get('recommendations'):
                    for rec in result['recommendations']:
                        print(f"   💡 {rec}")
                        self.results['recommendations'].append(rec)
                        
            except Exception as e:
                print(f"❌ ERROR INTERNO: {str(e)}")
                self.results['tests'][test_name] = {
                    'status': 'ERROR',
                    'message': f'Error interno: {str(e)}',
                    'details': [traceback.format_exc()]
                }
                failed += 1
        
        # Calcular estado general
        total = len(tests)
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 70)
        print("📋 RESUMEN DE DIAGNÓSTICO")
        print("=" * 70)
        print(f"✅ Pruebas exitosas: {passed}/{total} ({passed/total*100:.1f}%)")
        print(f"⚠️  Advertencias: {warnings}")
        print(f"❌ Fallas: {failed}")
        
        if success_rate >= 90 and failed == 0:
            self.results['overall_status'] = 'HEALTHY'
            status_msg = "🟢 SISTEMA SALUDABLE"
        elif success_rate >= 70 or failed <= 2:
            self.results['overall_status'] = 'WARNING'
            status_msg = "🟡 SISTEMA CON ADVERTENCIAS"
        else:
            self.results['overall_status'] = 'CRITICAL'
            status_msg = "🔴 SISTEMA CRÍTICO"
        
        print(f"\n🏥 ESTADO GENERAL: {status_msg}")
        
        # Mostrar recomendaciones principales
        if self.results['recommendations']:
            print(f"\n💡 RECOMENDACIONES PRINCIPALES:")
            for i, rec in enumerate(self.results['recommendations'][:5], 1):
                print(f"   {i}. {rec}")
        
        print("=" * 70)
        
        # Guardar resultados
        self._save_results()
        
        return self.results
    
    def check_file_structure(self):
        """Verificar estructura de archivos del sistema"""
        required_files = [
            'app.py', 'models.py', 'run.py', 'migrate_database.py'
        ]
        
        required_dirs = [
            'templates', 'static', 'utils', 'tools', 'data', 'logs', 'ssl'
        ]
        
        optional_dirs = [
            'service', 'updater', 'backups'
        ]
        
        missing_files = []
        missing_dirs = []
        present_optional = []
        
        # Verificar archivos requeridos
        for file in required_files:
            if not os.path.exists(os.path.join(self.install_dir, file)):
                missing_files.append(file)
        
        # Verificar directorios requeridos
        for dir_name in required_dirs:
            dir_path = os.path.join(self.install_dir, dir_name)
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_name)
        
        # Verificar directorios opcionales
        for dir_name in optional_dirs:
            dir_path = os.path.join(self.install_dir, dir_name)
            if os.path.exists(dir_path):
                present_optional.append(dir_name)
        
        details = []
        recommendations = []
        
        if missing_files:
            details.append(f"Archivos faltantes: {', '.join(missing_files)}")
            recommendations.append("Reinstalar la aplicación o restaurar desde backup")
        
        if missing_dirs:
            details.append(f"Directorios faltantes: {', '.join(missing_dirs)}")
            recommendations.append("Ejecutar script de reparación o reinstalar")
        
        if present_optional:
            details.append(f"Módulos opcionales instalados: {', '.join(present_optional)}")
        
        if missing_files or missing_dirs:
            status = 'FAIL'
            message = 'Estructura de archivos incompleta'
        else:
            status = 'PASS'
            message = 'Estructura de archivos correcta'
            details.append(f"Todos los archivos requeridos presentes")
            details.append(f"Directorio base: {self.install_dir}")
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_python_dependencies(self):
        """Verificar Python y dependencias"""
        details = []
        recommendations = []
        
        # Verificar versión de Python
        python_version = sys.version_info
        python_version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        details.append(f"Python {python_version_str}")
        
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            return {
                'status': 'FAIL',
                'message': f'Python {python_version_str} es muy antiguo',
                'details': details,
                'recommendations': ['Instalar Python 3.8 o superior']
            }
        
        # Verificar dependencias
        required_packages = {
            'flask': 'Flask',
            'flask_sqlalchemy': 'Flask-SQLAlchemy',
            'flask_login': 'Flask-Login',
            'werkzeug': 'Werkzeug',
            'requests': 'requests',
            'cryptography': 'cryptography'
        }
        
        optional_packages = {
            'psutil': 'psutil',
            'win32service': 'pywin32'
        }
        
        missing_required = []
        missing_optional = []
        present_packages = []
        
        for module, package in required_packages.items():
            try:
                __import__(module)
                present_packages.append(package)
            except ImportError:
                missing_required.append(package)
        
        for module, package in optional_packages.items():
            try:
                __import__(module)
                present_packages.append(package)
            except ImportError:
                missing_optional.append(package)
        
        if present_packages:
            details.append(f"Paquetes instalados: {', '.join(present_packages)}")
        
        if missing_required:
            details.append(f"Paquetes requeridos faltantes: {', '.join(missing_required)}")
            recommendations.append("Ejecutar: pip install -r requirements.txt")
            status = 'FAIL'
            message = 'Dependencias requeridas faltantes'
        elif missing_optional:
            details.append(f"Paquetes opcionales faltantes: {', '.join(missing_optional)}")
            recommendations.append("Instalar dependencias opcionales para funcionalidad completa")
            status = 'WARNING'
            message = 'Algunas dependencias opcionales faltantes'
        else:
            status = 'PASS'
            message = 'Todas las dependencias instaladas'
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_database(self):
        """Verificar base de datos"""
        db_path = os.path.join(self.install_dir, 'emergency_system.db')
        details = []
        recommendations = []
        
        if not os.path.exists(db_path):
            return {
                'status': 'FAIL',
                'message': 'Base de datos no existe',
                'details': ['Archivo emergency_system.db no encontrado'],
                'recommendations': ['Ejecutar inicialización de base de datos', 'Restaurar desde backup']
            }
        
        try:
            # Verificar conectividad
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tablas principales
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['usuarios', 'llamados', 'personas', 'guardias', 'observaciones', 'servicios_comisionados', 'configuracion']
            missing_tables = [t for t in expected_tables if t not in tables]
            extra_tables = [t for t in tables if t not in expected_tables and not t.startswith('sqlite_')]
            
            details.append(f"Tablas encontradas: {len(tables)}")
            details.append(f"Tamaño de BD: {os.path.getsize(db_path) / 1024:.1f} KB")
            
            if missing_tables:
                details.append(f"Tablas faltantes: {', '.join(missing_tables)}")
                recommendations.append("Ejecutar migración de base de datos")
            
            if extra_tables:
                details.append(f"Tablas adicionales: {', '.join(extra_tables)}")
            
            # Verificar estructura de tabla personas (campo email)
            cursor.execute("PRAGMA table_info(personas)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'email' not in columns:
                details.append("⚠️ Campo 'email' faltante en tabla personas")
                recommendations.append("Ejecutar migración para agregar campo email")
                status_email = False
            else:
                details.append("✅ Campo 'email' presente en tabla personas")
                status_email = True
            
            # Verificar usuarios admin
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin' AND activo = 1")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                details.append("⚠️ No hay usuarios administradores activos")
                recommendations.append("Crear usuario administrador")
            else:
                details.append(f"✅ {admin_count} usuario(s) administrador(es) activo(s)")
            
            # Conteo de registros
            for table in expected_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    details.append(f"Registros en {table}: {count}")
            
            conn.close()
            
            if missing_tables:
                status = 'FAIL'
                message = 'Estructura de base de datos incompleta'
            elif not status_email or admin_count == 0:
                status = 'WARNING'
                message = 'Base de datos funcional con advertencias'
            else:
                status = 'PASS'
                message = 'Base de datos en buen estado'
            
        except sqlite3.Error as e:
            return {
                'status': 'FAIL',
                'message': f'Error de base de datos: {str(e)}',
                'details': [f'Error SQLite: {str(e)}'],
                'recommendations': ['Verificar integridad de base de datos', 'Restaurar desde backup']
            }
        except Exception as e:
            return {
                'status': 'FAIL',
                'message': f'Error verificando base de datos: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Verificar permisos de archivo', 'Reinstalar aplicación']
            }
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_windows_services(self):
        """Verificar servicios Windows"""
        service_name = "EmergencySystemVA"
        details = []
        recommendations = []
        
        try:
            # Verificar si el servicio existe
            result = subprocess.run(
                ['sc', 'query', service_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode != 0:
                return {
                    'status': 'WARNING',
                    'message': 'Servicio Windows no instalado',
                    'details': ['El servicio no está registrado en el sistema'],
                    'recommendations': ['Instalar servicio con privilegios de administrador', 'Ejecutar aplicación manualmente']
                }
            
            # Analizar estado del servicio
            output = result.stdout
            
            if 'RUNNING' in output:
                status_text = 'EN EJECUCIÓN'
                service_status = 'PASS'
            elif 'STOPPED' in output:
                status_text = 'DETENIDO'
                service_status = 'WARNING'
                recommendations.append('Iniciar servicio: sc start EmergencySystemVA')
            elif 'PAUSED' in output:
                status_text = 'PAUSADO'
                service_status = 'WARNING'
                recommendations.append('Reanudar servicio')
            else:
                status_text = 'ESTADO DESCONOCIDO'
                service_status = 'WARNING'
            
            details.append(f"Estado del servicio: {status_text}")
            
            # Verificar configuración de inicio
            config_result = subprocess.run(
                ['sc', 'qc', service_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if config_result.returncode == 0:
                config_output = config_result.stdout
                if 'AUTO_START' in config_output:
                    details.append("✅ Configurado para inicio automático")
                elif 'DEMAND_START' in config_output:
                    details.append("⚠️ Configurado para inicio manual")
                    recommendations.append("Configurar inicio automático: sc config EmergencySystemVA start= auto")
            
            message = f'Servicio {status_text.lower()}'
            
        except subprocess.SubprocessError as e:
            return {
                'status': 'ERROR',
                'message': f'Error verificando servicio: {str(e)}',
                'details': [f'Error subprocess: {str(e)}'],
                'recommendations': ['Verificar permisos de administrador']
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error inesperado: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Contactar soporte técnico']
            }
        
        return {
            'status': service_status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_network_connectivity(self):
        """Verificar conectividad de red"""
        details = []
        recommendations = []
        
        # Verificar puerto 5000 (aplicación)
        port_5000_open = self._check_port_open('localhost', 5000)
        
        if port_5000_open:
            details.append("✅ Puerto 5000 accesible (aplicación)")
        else:
            details.append("❌ Puerto 5000 no accesible")
            recommendations.append("Verificar que la aplicación esté ejecutándose")
            recommendations.append("Verificar firewall local")
        
        # Verificar conectividad a internet
        internet_ok = False
        try:
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code == 200:
                details.append("✅ Conectividad a internet OK")
                internet_ok = True
        except:
            details.append("❌ Sin conectividad a internet")
            recommendations.append("Verificar conexión a internet para WhatsApp y actualizaciones")
        
        # Verificar DNS
        try:
            socket.gethostbyname('www.google.com')
            details.append("✅ Resolución DNS OK")
        except:
            details.append("❌ Problemas con resolución DNS")
            recommendations.append("Verificar configuración de DNS")
        
        # Verificar puertos adicionales si están configurados
        additional_ports = [443, 80]  # HTTPS, HTTP
        
        for port in additional_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        details.append(f"✅ Puerto {port} disponible")
                    else:
                        details.append(f"ℹ️ Puerto {port} no en uso")
            except:
                pass
        
        if port_5000_open and internet_ok:
            status = 'PASS'
            message = 'Conectividad de red correcta'
        elif port_5000_open:
            status = 'WARNING'
            message = 'Aplicación accesible, internet limitado'
        else:
            status = 'FAIL'
            message = 'Problemas de conectividad'
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_ssl_certificates(self):
        """Verificar certificados SSL"""
        ssl_dir = os.path.join(self.install_dir, 'ssl')
        cert_file = os.path.join(ssl_dir, 'server.crt')
        key_file = os.path.join(ssl_dir, 'server.key')
        
        details = []
        recommendations = []
        
        if not os.path.exists(ssl_dir):
            return {
                'status': 'WARNING',
                'message': 'Directorio SSL no existe',
                'details': ['Directorio ssl/ no encontrado'],
                'recommendations': ['Crear certificados SSL para comunicación segura']
            }
        
        missing_files = []
        if not os.path.exists(cert_file):
            missing_files.append('server.crt')
        if not os.path.exists(key_file):
            missing_files.append('server.key')
        
        if missing_files:
            details.append(f"Archivos faltantes: {', '.join(missing_files)}")
            recommendations.append("Generar certificados SSL")
            status = 'WARNING'
            message = 'Certificados SSL faltantes'
        else:
            details.append("✅ Certificados SSL presentes")
            
            # Verificar validez de certificados
            try:
                cert_stat = os.stat(cert_file)
                key_stat = os.stat(key_file)
                
                cert_size = cert_stat.st_size
                key_size = key_stat.st_size
                
                details.append(f"Tamaño certificado: {cert_size} bytes")
                details.append(f"Tamaño clave: {key_size} bytes")
                
                if cert_size > 100 and key_size > 100:
                    status = 'PASS'
                    message = 'Certificados SSL OK'
                else:
                    status = 'WARNING'
                    message = 'Certificados SSL pequeños (posibles problemas)'
                    recommendations.append("Regenerar certificados SSL")
                    
            except Exception as e:
                status = 'WARNING'
                message = f'Error verificando certificados: {str(e)}'
                recommendations.append("Verificar permisos de archivos SSL")
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_firewall(self):
        """Verificar configuración de firewall"""
        details = []
        recommendations = []
        
        try:
            # Verificar reglas de firewall para el sistema
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=EmergencySystemVA-HTTP'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if 'No rules match' in result.stdout or result.returncode != 0:
                details.append("❌ Regla de firewall HTTP no encontrada")
                recommendations.append("Agregar regla de firewall para puerto 5000")
                firewall_configured = False
            else:
                details.append("✅ Regla de firewall HTTP configurada")
                firewall_configured = True
            
            # Verificar regla HTTPS
            result_https = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=EmergencySystemVA-HTTPS'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if 'No rules match' not in result_https.stdout and result_https.returncode == 0:
                details.append("✅ Regla de firewall HTTPS configurada")
            else:
                details.append("ℹ️ Regla de firewall HTTPS no configurada")
            
            # Verificar estado general del firewall
            fw_status = subprocess.run(
                ['netsh', 'advfirewall', 'show', 'allprofiles', 'state'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if fw_status.returncode == 0:
                if 'ON' in fw_status.stdout:
                    details.append("✅ Firewall de Windows activo")
                else:
                    details.append("⚠️ Firewall de Windows desactivado")
            
        except Exception as e:
            return {
                'status': 'WARNING',
                'message': f'No se pudo verificar firewall: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Verificar permisos para consultar firewall']
            }
        
        if firewall_configured:
            status = 'PASS'
            message = 'Firewall configurado correctamente'
        else:
            status = 'WARNING'
            message = 'Firewall no configurado'
            recommendations.append("Ejecutar configuración de firewall como administrador")
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_whatsapp_config(self):
        """Verificar configuración de WhatsApp"""
        details = []
        recommendations = []
        
        try:
            # Verificar si existe configuración WhatsApp
            sys.path.insert(0, self.install_dir)
            
            # Intentar importar el módulo WhatsApp
            from utils.whatsapp import WhatsAppManager
            
            wp_manager = WhatsAppManager()
            status_info = wp_manager.get_status()
            
            if status_info['configured']:
                details.append("✅ WhatsApp configurado")
                
                # Test de conexión
                try:
                    test_result = wp_manager.test_connection()
                    if test_result['success']:
                        details.append("✅ Conexión WhatsApp exitosa")
                        status = 'PASS'
                        message = 'WhatsApp funcional'
                    else:
                        details.append(f"❌ Error de conexión: {test_result.get('error', 'Unknown')}")
                        status = 'WARNING'
                        message = 'WhatsApp configurado pero con problemas de conexión'
                        recommendations.append("Verificar credenciales de WhatsApp")
                        recommendations.append("Verificar conectividad a internet")
                except Exception as e:
                    details.append(f"⚠️ No se pudo probar conexión: {str(e)}")
                    status = 'WARNING'
                    message = 'WhatsApp configurado, conexión no verificada'
                
                # Verificar destinatarios
                if 'destinatarios' in status_info:
                    dest_config = status_info['destinatarios']
                    configured_dest = [k for k, v in dest_config.items() if v]
                    
                    if configured_dest:
                        details.append(f"Destinatarios configurados: {len(configured_dest)}")
                        for dest in configured_dest:
                            service_name = dest.replace('telefono_', '').upper()
                            details.append(f"  • {service_name}")
                    else:
                        details.append("⚠️ No hay destinatarios configurados")
                        recommendations.append("Configurar números de teléfono de servicios")
            else:
                details.append("❌ WhatsApp no configurado")
                if not status_info['token_set']:
                    details.append("  • Token no configurado")
                if not status_info['uid_set']:
                    details.append("  • UID no configurado")
                
                status = 'WARNING'
                message = 'WhatsApp no configurado'
                recommendations.append("Configurar token y UID de WhatsApp")
                recommendations.append("Configurar números de teléfono de servicios")
            
        except ImportError:
            return {
                'status': 'WARNING',
                'message': 'Módulo WhatsApp no disponible',
                'details': ['No se pudo cargar utils.whatsapp'],
                'recommendations': ['Verificar instalación completa', 'Instalar dependencias faltantes']
            }
        except Exception as e:
            return {
                'status': 'WARNING',
                'message': f'Error verificando WhatsApp: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Verificar configuración de WhatsApp']
            }
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_backup_system(self):
        """Verificar sistema de backup"""
        backup_dir = os.path.join(self.install_dir, 'backups')
        details = []
        recommendations = []
        
        if not os.path.exists(backup_dir):
            return {
                'status': 'WARNING',
                'message': 'Sistema de backup no inicializado',
                'details': ['Directorio backups/ no existe'],
                'recommendations': ['Crear directorio de backups', 'Realizar primer backup']
            }
        
        try:
            # Verificar módulo de backup
            sys.path.insert(0, self.install_dir)
            from utils.backup import BackupManager
            
            backup_manager = BackupManager()
            
            # Listar backups existentes
            backups = backup_manager.list_backups()
            
            details.append(f"Directorio de backups: {backup_dir}")
            details.append(f"Backups disponibles: {len(backups)}")
            
            if backups:
                # Mostrar información del backup más reciente
                latest_backup = backups[0]
                size_mb = latest_backup['size'] / (1024 * 1024)
                details.append(f"Backup más reciente: {latest_backup['filename']}")
                details.append(f"Tamaño: {size_mb:.1f} MB")
                details.append(f"Fecha: {latest_backup['created'].strftime('%d/%m/%Y %H:%M')}")
                
                # Verificar si el backup es reciente (menos de 7 días)
                days_old = (datetime.now() - latest_backup['created']).days
                
                if days_old <= 7:
                    details.append(f"✅ Backup reciente ({days_old} días)")
                    status = 'PASS'
                    message = 'Sistema de backup operativo'
                else:
                    details.append(f"⚠️ Backup antiguo ({days_old} días)")
                    status = 'WARNING'
                    message = 'Backup disponible pero antiguo'
                    recommendations.append("Crear backup actualizado")
            else:
                status = 'WARNING'
                message = 'No hay backups disponibles'
                recommendations.append("Crear primer backup del sistema")
            
            # Verificar integridad de BD
            integrity = backup_manager.verify_database_integrity()
            if integrity['valid']:
                details.append("✅ Integridad de base de datos OK")
            else:
                details.append("⚠️ Problemas de integridad de BD")
                for issue in integrity['issues']:
                    details.append(f"  • {issue}")
                recommendations.append("Reparar problemas de base de datos")
            
        except ImportError:
            return {
                'status': 'WARNING',
                'message': 'Módulo de backup no disponible',
                'details': ['No se pudo cargar utils.backup'],
                'recommendations': ['Verificar instalación de utilidades']
            }
        except Exception as e:
            return {
                'status': 'WARNING',
                'message': f'Error verificando backups: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Verificar permisos de directorio backups']
            }
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_web_application(self):
        """Verificar aplicación web"""
        details = []
        recommendations = []
        
        # Verificar que el puerto esté abierto
        port_open = self._check_port_open('localhost', 5000)
        
        if not port_open:
            return {
                'status': 'FAIL',
                'message': 'Aplicación web no accesible',
                'details': ['Puerto 5000 no responde'],
                'recommendations': [
                    'Iniciar la aplicación manualmente: python run.py',
                    'Verificar que no haya errores en la aplicación',
                    'Verificar firewall local'
                ]
            }
        
        details.append("✅ Puerto 5000 accesible")
        
        # Intentar conectar a la aplicación
        try:
            response = requests.get('http://localhost:5000', timeout=10, allow_redirects=True)
            
            details.append(f"Código de respuesta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                details.append("✅ Aplicación web respondiendo correctamente")
                
                # Verificar contenido de la respuesta
                if 'Emergency' in response.text or 'Emergencia' in response.text:
                    details.append("✅ Contenido de la aplicación correcto")
                    status = 'PASS'
                    message = 'Aplicación web funcional'
                else:
                    details.append("⚠️ Contenido inesperado en la respuesta")
                    status = 'WARNING'
                    message = 'Aplicación responde pero con contenido inesperado'
                    
            elif response.status_code in [301, 302]:
                details.append("ℹ️ Aplicación redirigiendo (posiblemente a login)")
                status = 'PASS'
                message = 'Aplicación web funcional (con redirección)'
            else:
                details.append(f"⚠️ Código de respuesta inesperado: {response.status_code}")
                status = 'WARNING'
                message = f'Aplicación responde con código {response.status_code}'
                recommendations.append("Verificar configuración de la aplicación")
        
        except requests.exceptions.ConnectionError:
            return {
                'status': 'FAIL',
                'message': 'No se puede conectar a la aplicación',
                'details': ['Error de conexión a http://localhost:5000'],
                'recommendations': [
                    'Verificar que la aplicación esté ejecutándose',
                    'Iniciar aplicación: python run.py'
                ]
            }
        except requests.exceptions.Timeout:
            return {
                'status': 'WARNING',
                'message': 'Timeout conectando a la aplicación',
                'details': ['La aplicación responde muy lentamente'],
                'recommendations': [
                    'Verificar rendimiento del sistema',
                    'Reiniciar la aplicación'
                ]
            }
        except Exception as e:
            return {
                'status': 'WARNING',
                'message': f'Error verificando aplicación: {str(e)}',
                'details': [f'Error: {str(e)}'],
                'recommendations': ['Verificar logs de la aplicación']
            }
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_performance(self):
        """Verificar rendimiento del sistema"""
        details = []
        recommendations = []
        
        try:
            # Información de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            details.append(f"CPU: {cpu_percent}% de uso")
            details.append(f"Núcleos de CPU: {cpu_count}")
            
            # Información de memoria
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total_gb = memory.total / (1024**3)
            memory_available_gb = memory.available / (1024**3)
            
            details.append(f"Memoria: {memory_percent}% de uso")
            details.append(f"Memoria total: {memory_total_gb:.1f} GB")
            details.append(f"Memoria disponible: {memory_available_gb:.1f} GB")
            
            # Información de disco
            disk = psutil.disk_usage(self.install_dir)
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            details.append(f"Disco: {disk_percent:.1f}% de uso")
            details.append(f"Espacio libre: {disk_free_gb:.1f} GB")
            
            # Evaluar rendimiento
            performance_issues = []
            
            if cpu_percent > 80:
                performance_issues.append("Alto uso de CPU")
                recommendations.append("Verificar procesos que consumen CPU")
            
            if memory_percent > 90:
                performance_issues.append("Memoria casi agotada")
                recommendations.append("Cerrar aplicaciones innecesarias")
            
            if disk_percent > 90:
                performance_issues.append("Disco casi lleno")
                recommendations.append("Liberar espacio en disco")
            
            if disk_free_gb < 1:
                performance_issues.append("Espacio en disco muy bajo")
                recommendations.append("Liberar espacio urgentemente")
            
            if memory_total_gb < 2:
                performance_issues.append("Poca memoria RAM del sistema")
                recommendations.append("Considerar actualizar hardware")
            
            # Procesos relacionados con Python
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append(proc.info)
                except:
                    pass
            
            if python_processes:
                details.append(f"Procesos Python activos: {len(python_processes)}")
                for proc in python_processes[:3]:  # Mostrar solo los primeros 3
                    details.append(f"  • PID {proc['pid']}: CPU {proc['cpu_percent']}%, RAM {proc['memory_percent']:.1f}%")
            
            if performance_issues:
                status = 'WARNING'
                message = f'Problemas de rendimiento detectados: {", ".join(performance_issues)}'
            else:
                status = 'PASS'
                message = 'Rendimiento del sistema adecuado'
                
        except Exception as e:
            return {
                'status': 'WARNING',
                'message': f'Error verificando rendimiento: {str(e)}',
                'details': [f'Error psutil: {str(e)}'],
                'recommendations': ['Instalar psutil para monitoreo completo']
            }
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def check_configuration(self):
        """Verificar configuración del sistema"""
        details = []
        recommendations = []
        
        # Verificar archivo de configuración principal
        config_files = ['config.ini', 'emergency_system.db']
        
        for config_file in config_files:
            file_path = os.path.join(self.install_dir, config_file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                details.append(f"✅ {config_file} presente ({size} bytes)")
            else:
                details.append(f"❌ {config_file} faltante")
                recommendations.append(f"Crear/restaurar {config_file}")
        
        # Verificar configuración en base de datos
        try:
            sys.path.insert(0, self.install_dir)
            
            db_path = os.path.join(self.install_dir, 'emergency_system.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Verificar tabla de configuración
                cursor.execute("SELECT COUNT(*) FROM configuracion")
                config_count = cursor.fetchone()[0]
                
                details.append(f"Parámetros de configuración: {config_count}")
                
                # Verificar configuraciones críticas
                critical_configs = [
                    'whatsapp_token',
                    'whatsapp_uid',
                    'telefono_demva',
                    'telefono_cec'
                ]
                
                missing_configs = []
                for config_key in critical_configs:
                    cursor.execute("SELECT valor FROM configuracion WHERE clave = ? AND valor != ''", (config_key,))
                    if not cursor.fetchone():
                        missing_configs.append(config_key)
                
                if missing_configs:
                    details.append(f"⚠️ Configuraciones faltantes: {', '.join(missing_configs)}")
                    recommendations.append("Completar configuración desde el panel de administración")
                else:
                    details.append("✅ Configuraciones críticas completas")
                
                conn.close()
                
        except Exception as e:
            details.append(f"⚠️ Error verificando configuración: {str(e)}")
            recommendations.append("Verificar integridad de la base de datos")
        
        # Determinar estado
        if any("❌" in detail for detail in details):
            status = 'FAIL'
            message = 'Configuración incompleta'
        elif any("⚠️" in detail for detail in details):
            status = 'WARNING'
            message = 'Configuración funcional con advertencias'
        else:
            status = 'PASS'
            message = 'Configuración completa'
        
        return {
            'status': status,
            'message': message,
            'details': details,
            'recommendations': recommendations
        }
    
    def _check_port_open(self, host, port):
        """Verificar si un puerto está abierto"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)
                result = s.connect_ex((host, port))
                return result == 0
        except:
            return False
    
    def _get_system_info(self):
        """Obtener información del sistema"""
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'hostname': platform.node()
            }
        except:
            return {'error': 'No se pudo obtener información del sistema'}
    
    def _save_results(self):
        """Guardar resultados del diagnóstico"""
        try:
            results_file = os.path.join(self.install_dir, 'logs', 'diagnostics_results.json')
            
            # Crear directorio logs si no existe
            os.makedirs(os.path.dirname(results_file), exist_ok=True)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n📄 Resultados guardados en: {results_file}")
            
        except Exception as e:
            print(f"\n⚠️ No se pudieron guardar los resultados: {e}")

def main():
    """Función principal"""
    print("🚨 SISTEMA DE EMERGENCIAS VILLA ALLENDE")
    print("   Herramientas de Diagnóstico Completas v2.0")
    print()
    
    # Cambiar al directorio de instalación si se especifica
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        os.chdir(sys.argv[1])
        print(f"📁 Directorio cambiado a: {sys.argv[1]}")
    
    diagnostics = SystemDiagnostics()
    results = diagnostics.run_all_diagnostics()
    
    # Mostrar resumen final
    print(f"\n🏁 DIAGNÓSTICO FINALIZADO")
    print(f"⏰ Duración: Completado a las {datetime.now().strftime('%H:%M:%S')}")
    
    # Sugerir acciones según el estado
    if results['overall_status'] == 'HEALTHY':
        print("💚 El sistema está funcionando correctamente.")
        print("   Continúe con el uso normal del sistema.")
    elif results['overall_status'] == 'WARNING':
        print("💛 El sistema funciona pero tiene advertencias.")
        print("   Revise las recomendaciones para optimizar el funcionamiento.")
    else:
        print("💔 El sistema tiene problemas críticos.")
        print("   Es necesario realizar reparaciones antes de usar el sistema.")
    
    print(f"\n📋 Para ver el reporte completo, consulte: logs/diagnostics_results.json")

if __name__ == '__main__':
    main()
