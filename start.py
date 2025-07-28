#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Script de Inicio Simplificado - Sin caracteres especiales

Este script es más simple y robusto para iniciar el sistema.
"""

import os
import sys
import subprocess

def print_banner():
    print("=" * 60)
    print("SISTEMA DE EMERGENCIAS VILLA ALLENDE v2.0")
    print("Script de Inicio Simplificado")
    print("=" * 60)
    print()

def check_python():
    """Verificar versión de Python"""
    print("Verificando Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python {version.major}.{version.minor} no compatible")
        print("       Instale Python 3.8 o superior")
        return False
    print(f"OK: Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_files():
    """Verificar archivos necesarios"""
    print("Verificando archivos...")
    required_files = ['app.py', 'run.py', 'requirements.txt']
    
    for file in required_files:
        if os.path.exists(file):
            print(f"OK: {file}")
        else:
            print(f"ERROR: {file} no encontrado")
            return False
    return True

def create_directories():
    """Crear directorios necesarios"""
    print("Creando directorios...")
    dirs = ['logs', 'data', 'static/uploads', 'backups']
    
    for dir_path in dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"OK: {dir_path}")
        except Exception as e:
            print(f"ERROR: No se pudo crear {dir_path} - {e}")
            return False
    return True

def check_dependencies():
    """Verificar dependencias básicas"""
    print("Verificando dependencias...")
    
    required_modules = ['flask', 'flask_sqlalchemy', 'flask_login', 'werkzeug']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"OK: {module}")
        except ImportError:
            print(f"ERROR: {module} faltante")
            missing.append(module)
    
    if missing:
        print(f"Dependencias faltantes: {', '.join(missing)}")
        print("Desea instalarlas ahora? (s/n): ", end='')
        response = input().lower()
        
        if response in ['s', 'si', 'y', 'yes']:
            print("Instalando dependencias...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                             check=True)
                print("OK: Dependencias instaladas")
                return True
            except subprocess.CalledProcessError:
                print("ERROR: No se pudieron instalar las dependencias")
                return False
        else:
            print("Continuando sin instalar dependencias...")
            return len(missing) == 0
    
    return True

def check_database():
    """Verificar estado de la base de datos"""
    print("Verificando base de datos...")
    
    if not os.path.exists('emergency_system.db'):
        print("INFO: Base de datos no existe, se creara automaticamente")
        return True
    
    # Verificar si la BD tiene problemas
    try:
        import sqlite3
        conn = sqlite3.connect('emergency_system.db')
        cursor = conn.cursor()
        
        # Probar consulta básica
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        # Probar consulta problemática
        cursor.execute("SELECT username, llamados_atendidos FROM usuarios LIMIT 1")
        
        conn.close()
        print(f"OK: Base de datos funcional ({count} usuarios)")
        return True
        
    except Exception as e:
        print(f"AVISO: Posible problema en base de datos - {e}")
        print("      Se recomienda recrear la base de datos")
        return True  # Continuamos de todas formas

def start_application():
    """Iniciar la aplicación"""
    print("\nINICIANDO APLICACION")
    print("=" * 30)
    print("URL: http://localhost:5000")
    print("Usuario: admin")
    print("Password: 123456")
    print("Presione Ctrl+C para detener")
    print("=" * 30)
    
    try:
        # Importar y ejecutar app
        sys.path.insert(0, os.getcwd())
        from app import app, init_database
        
        # Inicializar BD
        with app.app_context():
            init_database()
            print("OK: Aplicacion inicializada")
        
        # Ejecutar servidor
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
        
    except KeyboardInterrupt:
        print("\nSistema detenido por el usuario")
        return True
    except ImportError as e:
        print(f"ERROR: No se pudo importar la aplicacion - {e}")
        print("Verifique que app.py existe y es correcto")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def show_menu():
    """Mostrar menú de opciones"""
    print("OPCIONES DISPONIBLES:")
    print("1. Iniciar sistema normalmente")
    print("2. Diagnosticar base de datos")
    print("3. Recrear base de datos desde cero")
    print("4. Solo verificar sistema")
    print("5. Salir")
    print()
    
    while True:
        try:
            choice = int(input("Seleccione una opcion (1-5): "))
            if 1 <= choice <= 5:
                return choice
            else:
                print("Opcion invalida. Ingrese un numero entre 1 y 5.")
        except ValueError:
            print("Ingrese un numero valido.")

def main():
    """Función principal"""
    print_banner()
    
    # Verificaciones básicas
    if not check_python():
        input("Presione Enter para salir...")
        return 1
    
    if not check_files():
        input("Presione Enter para salir...")
        return 1
    
    if not create_directories():
        input("Presione Enter para salir...")
        return 1
    
    if not check_dependencies():
        input("Presione Enter para salir...")
        return 1
    
    check_database()
    
    # Mostrar menú
    print("\n")
    choice = show_menu()
    
    if choice == 1:
        # Iniciar sistema
        print("\nIniciando sistema...")
        if start_application():
            print("Sistema finalizado correctamente")
            return 0
        else:
            print("Error iniciando sistema")
            input("Presione Enter para salir...")
            return 1
    
    elif choice == 2:
        # Diagnóstico
        print("\nEjecutando diagnostico...")
        if os.path.exists('database_diagnostic.py'):
            os.system('python database_diagnostic.py')
        else:
            print("ERROR: database_diagnostic.py no encontrado")
            print("Cree el archivo con el script de diagnostico")
        input("Presione Enter para continuar...")
        return 0
    
    elif choice == 3:
        # Recrear BD
        print("\nRecreando base de datos...")
        if os.path.exists('recreate_database.py'):
            os.system('python recreate_database.py')
        else:
            print("ERROR: recreate_database.py no encontrado")
            print("Cree el archivo con el script de recreacion")
        input("Presione Enter para continuar...")
        return 0
    
    elif choice == 4:
        # Solo verificar
        print("\nVerificacion completada")
        input("Presione Enter para salir...")
        return 0
    
    elif choice == 5:
        # Salir
        print("Saliendo...")
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\nError critico: {e}")
        input("Presione Enter para salir...")
        sys.exit(1)