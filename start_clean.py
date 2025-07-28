#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Script de Inicio Limpio - Sin emojis ni caracteres especiales

Compatible con Windows, sin problemas de encoding
"""

import os
import sys
import logging

# Configurar logging SIN emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def print_banner():
    print("=" * 60)
    print("SISTEMA DE EMERGENCIAS VILLA ALLENDE v2.0")
    print("Script de Inicio Limpio - Sin caracteres especiales")
    print("=" * 60)
    print()

def check_python():
    """Verificar Python"""
    print("Verificando Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"ERROR: Python {version.major}.{version.minor} no compatible")
        return False
    print(f"OK: Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_files():
    """Verificar archivos"""
    print("Verificando archivos...")
    required = ['app.py', 'requirements.txt']
    
    for file in required:
        if os.path.exists(file):
            print(f"OK: {file}")
        else:
            print(f"ERROR: {file} no encontrado")
            return False
    return True

def create_directories():
    """Crear directorios"""
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
    """Verificar dependencias"""
    print("Verificando dependencias...")
    
    modules = ['flask', 'flask_sqlalchemy', 'flask_login', 'werkzeug']
    missing = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"OK: {module}")
        except ImportError:
            print(f"ERROR: {module} faltante")
            missing.append(module)
    
    if missing:
        print("Desea instalar dependencias faltantes? (s/n): ", end='')
        response = input().lower()
        
        if response in ['s', 'si', 'y', 'yes']:
            print("Instalando dependencias...")
            import subprocess
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                             check=True)
                print("OK: Dependencias instaladas")
                return True
            except subprocess.CalledProcessError:
                print("ERROR: No se pudieron instalar")
                return False
        else:
            return len(missing) == 0
    
    return True

def start_application():
    """Iniciar aplicación"""
    print("\nINICIANDO APLICACION")
    print("=" * 30)
    print("URL: http://localhost:5000")
    print("Usuario: admin")
    print("Password: 123456")
    print("Presione Ctrl+C para detener")
    print("=" * 30)
    
    try:
        # Importar app LIMPIA (sin emojis en logs)
        sys.path.insert(0, os.getcwd())
        
        # Importar solo lo necesario
        from flask import Flask
        from werkzeug.security import generate_password_hash
        import sqlite3
        
        # Crear aplicación Flask simple
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'emergency-system-villa-allende-2024-secure'
        
        # Verificar que BD existe
        if not os.path.exists('emergency_system.db'):
            print("ERROR: Base de datos no existe")
            print("       Ejecute primero: python fix_final.py")
            return False
        
        # Importar app completa SOLO si BD existe
        from app import app as full_app
        
        print("OK: Aplicacion cargada")
        
        # Ejecutar servidor
        full_app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
        
        return True
        
    except KeyboardInterrupt:
        print("\nSistema detenido por el usuario")
        return True
    except ImportError as e:
        print(f"ERROR: No se pudo importar app - {e}")
        print("Verifique que app.py existe y es correcto")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Función principal"""
    print_banner()
    
    # Verificaciones
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
    
    # Verificar que BD existe
    if not os.path.exists('emergency_system.db'):
        print("\nERROR: Base de datos no existe")
        print("       Ejecute primero: python fix_final.py")
        input("Presione Enter para salir...")
        return 1
    
    print("OK: Base de datos encontrada")
    
    # Iniciar aplicación
    print("\nIniciando aplicacion...")
    if start_application():
        print("Sistema finalizado correctamente")
        return 0
    else:
        print("Error iniciando sistema")
        input("Presione Enter para salir...")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"\nError critico: {e}")
        input("Presione Enter para salir...")
        sys.exit(1)