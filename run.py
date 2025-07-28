#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Script de Inicio y Verificación - Versión Corregida

Este script:
1. Verifica dependencias
2. Verifica estructura de archivos 
3. Ejecuta migración de base de datos
4. Inicializa la aplicación Flask
5. Inicia el servidor

Uso:
    python run.py            # Inicia el servidor normalmente
    python run.py --check    # Solo verifica el sistema sin iniciar
    python run.py --migrate  # Solo ejecuta migración
    python run.py --help     # Muestra ayuda
"""

import os
import sys
import traceback
import argparse
from datetime import datetime

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 70)
    print("🚨 SISTEMA DE EMERGENCIAS VILLA ALLENDE v2.0")
    print("   Script de Inicio y Verificación")
    print("=" * 70)
    print()

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} no es compatible")
        print("💡 Solución: Instalar Python 3.8 o superior")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Verificar dependencias críticas"""
    print("\n🔍 Verificando dependencias...")
    
    critical_deps = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('werkzeug', 'Werkzeug'),
        ('sqlite3', 'SQLite3 (built-in)')
    ]
    
    optional_deps = [
        ('requests', 'requests (para WhatsApp)'),
        ('cryptography', 'cryptography (para SSL)')
    ]
    
    missing_critical = []
    missing_optional = []
    
    # Verificar dependencias críticas
    for module, name in critical_deps:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - CRÍTICO")
            missing_critical.append(name)
    
    # Verificar dependencias opcionales
    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️ {name} - OPCIONAL")
            missing_optional.append(name)
    
    if missing_critical:
        print(f"\n❌ ERROR: Dependencias críticas faltantes: {', '.join(missing_critical)}")
        print("💡 Solución: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️ AVISO: Dependencias opcionales faltantes: {', '.join(missing_optional)}")
        print("   Algunas funcionalidades pueden no estar disponibles")
    
    print("✅ Todas las dependencias críticas están instaladas")
    return True

def check_file_structure():
    """Verificar estructura de archivos"""
    print("\n🗂️ Verificando estructura de archivos...")
    
    required_files = [
        'app.py',
        'migrate_database.py',
        'requirements.txt'
    ]
    
    required_dirs = [
        'templates',
        'static'
    ]
    
    optional_dirs = [
        'utils',
        'tools',
        'logs',
        'data',
        'ssl',
        'backups'
    ]
    
    missing_files = []
    missing_dirs = []
    created_dirs = []
    
    # Verificar archivos requeridos
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - REQUERIDO")
            missing_files.append(file)
    
    # Verificar directorios requeridos
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ - REQUERIDO")
            missing_dirs.append(directory)
    
    # Crear directorios opcionales si no existen
    for directory in optional_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"  ✅ {directory}/ - CREADO")
                created_dirs.append(directory)
            except Exception as e:
                print(f"  ⚠️ {directory}/ - Error creando: {e}")
    
    if missing_files or missing_dirs:
        print(f"\n❌ ERROR: Archivos/directorios críticos faltantes")
        if missing_files:
            print(f"   Archivos: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"   Directorios: {', '.join(missing_dirs)}")
        print("💡 Solución: Restaurar desde backup o reinstalar")
        return False
    
    if created_dirs:
        print(f"\n✅ Directorios creados: {', '.join(created_dirs)}")
    
    print("✅ Estructura de archivos verificada")
    return True

def run_database_migration():
    """Ejecutar migración de base de datos"""
    print("\n🗄️ Ejecutando migración de base de datos...")
    
    try:
        # Verificar si existe el script de migración
        if not os.path.exists('migrate_database.py'):
            print("⚠️ Script de migración no encontrado, saltando...")
            return True
        
        # Importar y ejecutar migración
        from migrate_database import DatabaseMigrator
        
        migrator = DatabaseMigrator()
        if migrator.run_migration():
            print("✅ Migración de base de datos completada")
            return True
        else:
            print("❌ Error en migración de base de datos")
            return False
            
    except ImportError as e:
        print(f"⚠️ No se pudo importar migrador: {e}")
        print("   Continuando con inicialización básica...")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        print(f"📋 Detalles del error:")
        print(traceback.format_exc())
        return False

def initialize_application():
    """Inicializar aplicación Flask"""
    print("\n🚀 Inicializando aplicación Flask...")
    
    try:
        # Verificar que app.py existe
        if not os.path.exists('app.py'):
            print("❌ Archivo app.py no encontrado")
            return None
        
        # Importar aplicación
        from app import app, init_database
        
        # Inicializar base de datos en contexto de aplicación
        with app.app_context():
            init_database()
        
        print("✅ Aplicación Flask inicializada correctamente")
        return app
        
    except Exception as e:
        print(f"❌ Error inicializando aplicación: {e}")
        print(f"📋 Detalles del error:")
        print(traceback.format_exc())
        return None

def start_application(app, port=5000, debug=False):
    """Iniciar servidor Flask"""
    print(f"\n🌐 Iniciando servidor en puerto {port}...")
    print(f"🔗 Acceso web: http://localhost:{port}")
    print("👤 Usuario inicial: admin / 123456")
    print("\n⚠️ IMPORTANTE: Cambiar contraseña de admin después del primer login")
    print("🛑 Presione Ctrl+C para detener el servidor")
    print("=" * 70)
    
    try:
        app.run(
            debug=debug,
            host='0.0.0.0',
            port=port,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        return True
    except Exception as e:
        print(f"\n❌ Error ejecutando servidor: {e}")
        return False

def run_diagnostics():
    """Ejecutar diagnósticos completos"""
    print("\n🔧 Ejecutando diagnósticos del sistema...")
    
    try:
        if os.path.exists('tools/diagnostics.py'):
            from tools.diagnostics import SystemDiagnostics
            diagnostics = SystemDiagnostics()
            results = diagnostics.run_full_diagnostics()
            
            print("\n📋 Resultados de diagnósticos:")
            for check_name, result in results.items():
                status = "✅" if result['status'] == 'PASS' else "❌"
                print(f"  {status} {check_name}: {result['message']}")
            
            return True
        else:
            print("⚠️ Herramientas de diagnóstico no disponibles")
            return True
            
    except Exception as e:
        print(f"❌ Error ejecutando diagnósticos: {e}")
        return False

def main():
    """Función principal"""
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Sistema de Emergencias Villa Allende')
    parser.add_argument('--check', action='store_true', help='Solo verificar sistema sin iniciar')
    parser.add_argument('--migrate', action='store_true', help='Solo ejecutar migración de BD')
    parser.add_argument('--diagnostics', action='store_true', help='Ejecutar diagnósticos completos')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Modo debug (NO usar en producción)')
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    
    # Verificaciones básicas
    print("🔍 VERIFICACIONES BÁSICAS")
    print("-" * 30)
    
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_file_structure():
        sys.exit(1)
    
    # Modo solo verificación
    if args.check:
        print("\n✅ Verificaciones completadas - Sistema OK")
        if args.diagnostics:
            run_diagnostics()
        sys.exit(0)
    
    # Modo solo migración
    if args.migrate:
        print("\n🔄 EJECUTANDO SOLO MIGRACIÓN")
        print("-" * 35)
        if run_database_migration():
            print("\n✅ Migración completada exitosamente")
            sys.exit(0)
        else:
            print("\n❌ Error en migración")
            sys.exit(1)
    
    # Modo diagnósticos
    if args.diagnostics:
        print("\n🔧 EJECUTANDO DIAGNÓSTICOS")
        print("-" * 32)
        run_diagnostics()
        sys.exit(0)
    
    # Proceso completo de inicio
    print("\n🔄 INICIALIZACIÓN COMPLETA")
    print("-" * 30)
    
    # Migración de base de datos
    if not run_database_migration():
        print("\n❌ Error en migración - Abortando inicio")
        sys.exit(1)
    
    # Inicialización de aplicación
    app = initialize_application()
    if not app:
        print("\n❌ Error en inicialización - Abortando inicio")
        sys.exit(1)
    
    # Inicio del servidor
    print("\n🌐 INICIANDO SERVIDOR")
    print("-" * 22)
    
    if not start_application(app, port=args.port, debug=args.debug):
        print("\n❌ Error iniciando servidor")
        sys.exit(1)
    
    print("\n✅ Sistema finalizado correctamente")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        print(f"📋 Detalles del error:")
        print(traceback.format_exc())
        sys.exit(1)