#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende v2.0
Script de Inicio Principal

Mejoras en v2.0:
- Verificación completa de dependencias
- Migración automática de base de datos
- Campo email agregado en personas
- Verificación de integridad del sistema
- Logging mejorado
- Manejo de errores robusto
"""

import os
import sys
import logging
from datetime import datetime
import traceback

def setup_logging():
    """Configurar sistema de logging"""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 70)
    print("🚨 SISTEMA DE EMERGENCIAS VILLA ALLENDE v2.0")
    print("   Gestión Integral de Llamados de Emergencia")
    print("   Villa Allende, Córdoba - Argentina")
    print("=" * 70)
    print(f"📅 Iniciado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Directorio: {os.getcwd()}")
    print("=" * 70)

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        print("   Descargue Python desde: https://python.org")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_dependencies():
    """Verificar dependencias críticas"""
    print("\n🔍 Verificando dependencias...")
    
    critical_deps = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('werkzeug', 'Werkzeug'),
        ('requests', 'requests'),
        ('sqlite3', 'SQLite3 (built-in)')
    ]
    
    missing_deps = []
    
    for module, name in critical_deps:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - FALTANTE")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\n❌ ERROR: Dependencias faltantes: {', '.join(missing_deps)}")
        print("💡 Solución: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_file_structure():
    """Verificar estructura de archivos"""
    print("\n🗂️  Verificando estructura de archivos...")
    
    required_files = [
        'app.py',
        'models.py', 
        'migrate_database.py',
        'requirements.txt'
    ]
    
    required_dirs = [
        'templates',
        'static',
        'utils'
    ]
    
    missing_items = []
    
    # Verificar archivos
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - FALTANTE")
            missing_items.append(file)
    
    # Verificar directorios
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ - FALTANTE")
            missing_items.append(f"{directory}/")
    
    if missing_items:
        print(f"\n❌ ERROR: Archivos/directorios faltantes: {', '.join(missing_items)}")
        print("💡 Solución: Restaurar desde backup o reinstalar")
        return False
    
    print("✅ Estructura de archivos completa")
    return True

def run_database_migration():
    """Ejecutar migración de base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        # Ejecutar migración automática
        from migrate_database import DatabaseMigrator
        
        migrator = DatabaseMigrator()
        if migrator.run_migration():
            print("✅ Base de datos migrada/verificada correctamente")
            return True
        else:
            print("❌ Error en migración de base de datos")
            return False
            
    except ImportError:
        print("⚠️  Script de migración no disponible, intentando inicialización básica...")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        return False

def initialize_application():
    """Inicializar aplicación Flask"""
    print("\n🚀 Inicializando aplicación...")
    
    try:
        # Importar aplicación
        from app import app, init_database
        
        # Inicializar base de datos en contexto de aplicación
        with app.app_context():
            init_database()
        
        print("✅ Aplicación inicializada correctamente")
        return app
        
    except Exception as e:
        print(f"❌ Error inicializando aplicación: {e}")
        print(f"📋 Detalles del error:")
        print(traceback.format_exc())
        return None

def start_application(app):
    """Iniciar servidor Flask"""
    print("\n🌐 Iniciando servidor web...")
    print("=" * 70)
    print("🔗 URL de acceso: http://localhost:5000")
    print("👤 Usuario por defecto: admin")
    print("🔑 Contraseña por defecto: 123456")
    print("=" * 70)
    print("⚠️  IMPORTANTE:")
    print("   • Cambie la contraseña por defecto después del primer acceso")
    print("   • Configure WhatsApp desde el panel de configuración")
    print("   • Realice un backup inicial del sistema")
    print("=" * 70)
    print("🛑 Presione Ctrl+C para detener el servidor")
    print("=" * 70)
    
    try:
        # Configurar desde config.ini si existe
        host = '0.0.0.0'
        port = 5000
        debug = False
        
        if os.path.exists('config.ini'):
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read('config.ini')
                
                host = config.get('SERVER', 'host', fallback='0.0.0.0')
                port = config.getint('SERVER', 'port', fallback=5000)
                debug = config.getboolean('SERVER', 'debug', fallback=False)
                
                print(f"📋 Configuración cargada desde config.ini")
            except Exception as e:
                print(f"⚠️  Error leyendo config.ini, usando valores por defecto: {e}")
        
        print(f"🌐 Servidor iniciando en {host}:{port}")
        print(f"🔧 Modo debug: {'Activado' if debug else 'Desactivado'}")
        
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Sistema detenido por el usuario")
        print("👋 ¡Hasta la vista!")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando servidor: {e}")
        print("📋 Detalles del error:")
        print(traceback.format_exc())
        return False
    
    return True

def show_system_status():
    """Mostrar estado del sistema después de las verificaciones"""
    print("\n📊 ESTADO DEL SISTEMA:")
    print("=" * 40)
    
    # Verificar base de datos
    if os.path.exists('emergency_system.db'):
        size = os.path.getsize('emergency_system.db')
        print(f"🗄️  Base de datos: OK ({size} bytes)")
    else:
        print("🗄️  Base de datos: Se creará automáticamente")
    
    # Verificar logs
    if os.path.exists('logs'):
        log_files = len([f for f in os.listdir('logs') if f.endswith('.log')])
        print(f"📄 Logs: {log_files} archivo(s)")
    else:
        print("📄 Logs: Directorio se creará")
    
    # Verificar backups
    if os.path.exists('backups'):
        backup_files = len([f for f in os.listdir('backups') if f.endswith('.zip')])
        print(f"💾 Backups: {backup_files} archivo(s)")
    else:
        print("💾 Backups: Directorio se creará")
    
    # Verificar SSL
    if os.path.exists('ssl'):
        ssl_files = len([f for f in os.listdir('ssl') if f.endswith(('.crt', '.key'))])
        print(f"🔐 SSL: {ssl_files} archivo(s)")
    else:
        print("🔐 SSL: No configurado")
    
    print("=" * 40)

def main():
    """Función principal"""
    # Configurar logging
    logger = setup_logging()
    
    try:
        # Mostrar banner
        print_banner()
        
        # Verificaciones pre-inicio
        checks = [
            ("Versión de Python", check_python_version),
            ("Dependencias", check_dependencies), 
            ("Estructura de archivos", check_file_structure),
            ("Migración de base de datos", run_database_migration)
        ]
        
        for check_name, check_func in checks:
            if not check_func():
                print(f"\n💔 FALLO EN VERIFICACIÓN: {check_name}")
                print("🔧 Corrija los errores antes de continuar")
                input("\n⏸️  Presione Enter para salir...")
                sys.exit(1)
        
        # Mostrar estado del sistema
        show_system_status()
        
        # Inicializar aplicación
        app = initialize_application()
        if not app:
            print("\n💔 No se pudo inicializar la aplicación")
            input("\n⏸️  Presione Enter para salir...")
            sys.exit(1)
        
        # Mostrar información de novedades v2.0
        print("\n🎉 NOVEDADES EN VERSIÓN 2.0:")
        print("  ✅ Campo email agregado en tabla personas")
        print("  ✅ Migración automática de base de datos")
        print("  ✅ Sistema de backup mejorado")
        print("  ✅ Herramientas de diagnóstico integradas")
        print("  ✅ Instalador automático completo")
        print("  ✅ Servicio Windows incluido")
        
        # Pausa antes de iniciar servidor
        print(f"\n🚀 Sistema verificado y listo para iniciar")
        print("⏳ Iniciando en 3 segundos...")
        
        import time
        time.sleep(3)
        
        # Iniciar servidor
        start_application(app)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Inicio cancelado por el usuario")
        
    except Exception as e:
        logger.error(f"Error crítico en startup: {e}")
        print(f"\n💥 ERROR CRÍTICO: {e}")
        print("📋 Detalles completos en logs/app.log")
        print(traceback.format_exc())
        input("\n⏸️  Presione Enter para salir...")
        sys.exit(1)

if __name__ == '__main__':
    main()
