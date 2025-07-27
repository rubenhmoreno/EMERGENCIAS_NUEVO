#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Servicio Windows

Funcionalidades:
- Ejecución automática como servicio Windows
- Monitoreo y reinicio automático de la aplicación
- Logging detallado de eventos
- Manejo de errores y recuperación automática
"""

import win32serviceutil
import win32service
import win32event
import win32api
import logging
import os
import sys
import threading
import subprocess
import time
import signal
from datetime import datetime

class EmergencySystemService(win32serviceutil.ServiceFramework):
    """Servicio Windows para el Sistema de Emergencias Villa Allende"""
    
    _svc_name_ = "EmergencySystemVA"
    _svc_display_name_ = "Sistema de Emergencias Villa Allende"
    _svc_description_ = "Servicio del Sistema de Gestión de Emergencias de Villa Allende v2.0"
    _svc_deps_ = None
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        self.app_process = None
        self.monitor_thread = None
        
        # Configurar rutas
        self.install_dir = r'C:\EmergenciaVA'
        self.app_script = os.path.join(self.install_dir, 'run.py')
        self.log_file = os.path.join(self.install_dir, 'logs', 'service.log')
        
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Servicio EmergencySystemVA inicializado")
    
    def SvcStop(self):
        """Detener el servicio"""
        self.logger.info("Recibida señal de parada del servicio")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Marcar como no vivo para detener el monitor
        self.is_alive = False
        
        # Terminar proceso de la aplicación
        self._stop_application()
        
        # Señalar evento de parada
        win32event.SetEvent(self.hWaitStop)
        
        self.logger.info("Servicio detenido correctamente")
    
    def SvcDoRun(self):
        """Ejecutar el servicio"""
        self.logger.info("=== INICIANDO SERVICIO EMERGENCIA VILLA ALLENDE ===")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        try:
            # Verificar instalación
            if not self._verify_installation():
                self.logger.error("Verificación de instalación falló")
                return
            
            # Iniciar thread de monitoreo
            self.monitor_thread = threading.Thread(target=self._monitor_application)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("Servicio en ejecución, esperando señal de parada...")
            
            # Esperar señal de parada
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f"Error crítico en servicio: {e}")
        finally:
            self.logger.info("=== FINALIZANDO SERVICIO ===")
    
    def _verify_installation(self):
        """Verificar que la instalación esté completa"""
        self.logger.info("Verificando instalación...")
        
        # Verificar directorio de instalación
        if not os.path.exists(self.install_dir):
            self.logger.error(f"Directorio de instalación no encontrado: {self.install_dir}")
            return False
        
        # Verificar script principal
        if not os.path.exists(self.app_script):
            self.logger.error(f"Script principal no encontrado: {self.app_script}")
            return False
        
        # Verificar Python
        python_path = self._find_python()
        if not python_path:
            self.logger.error("Python no encontrado en el sistema")
            return False
        
        self.python_path = python_path
        self.logger.info(f"Python encontrado: {python_path}")
        
        # Verificar base de datos
        db_path = os.path.join(self.install_dir, 'emergency_system.db')
        if not os.path.exists(db_path):
            self.logger.warning(f"Base de datos no encontrada: {db_path}")
        else:
            self.logger.info("Base de datos encontrada")
        
        self.logger.info("Verificación de instalación completada")
        return True
    
    def _monitor_application(self):
        """Monitorear y mantener la aplicación ejecutándose"""
        self.logger.info("Iniciando monitor de aplicación")
        
        restart_count = 0
        max_restarts = 5
        restart_delay = 30  # segundos
        
        while self.is_alive:
            try:
                # Verificar si la aplicación está ejecutándose
                if not self._is_application_running():
                    if restart_count < max_restarts:
                        self.logger.info(f"Iniciando aplicación (intento {restart_count + 1}/{max_restarts})")
                        
                        if self._start_application():
                            self.logger.info("Aplicación iniciada exitosamente")
                            restart_count = 0  # Resetear contador en inicio exitoso
                        else:
                            restart_count += 1
                            self.logger.error(f"Error iniciando aplicación (intento {restart_count})")
                            
                            if restart_count >= max_restarts:
                                self.logger.critical("Máximo número de reintentos alcanzado, deteniendo monitor")
                                break
                    else:
                        self.logger.critical("Aplicación no se puede iniciar, monitor detenido")
                        break
                
                # Esperar antes de la siguiente verificación
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error en monitor de aplicación: {e}")
                time.sleep(60)  # Esperar más tiempo en caso de error
        
        self.logger.info("Monitor de aplicación finalizado")
    
    def _is_application_running(self):
        """Verificar si la aplicación está ejecutándose"""
        if self.app_process is None:
            return False
        
        # Verificar si el proceso sigue vivo
        if self.app_process.poll() is not None:
            self.logger.warning("Proceso de aplicación terminó inesperadamente")
            self.app_process = None
            return False
        
        # Verificar si el puerto está abierto (indicador de que la app funciona)
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex(('localhost', 5000))
                if result == 0:
                    return True
                else:
                    self.logger.warning("Puerto 5000 no accesible, aplicación posiblemente no responde")
                    return False
        except Exception as e:
            self.logger.warning(f"Error verificando puerto: {e}")
            return False
    
    def _start_application(self):
        """Iniciar la aplicación Flask"""
        try:
            # Cambiar al directorio de instalación
            os.chdir(self.install_dir)
            
            # Configurar variables de entorno
            env = os.environ.copy()
            env['PYTHONPATH'] = self.install_dir
            env['FLASK_ENV'] = 'production'
            
            # Comando para ejecutar la aplicación
            cmd = [self.python_path, self.app_script]
            
            self.logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            # Iniciar proceso
            self.app_process = subprocess.Popen(
                cmd,
                cwd=self.install_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.logger.info(f"Aplicación iniciada con PID: {self.app_process.pid}")
            
            # Esperar un momento y verificar que no haya terminado inmediatamente
            time.sleep(5)
            
            if self.app_process.poll() is None:
                self.logger.info("Aplicación ejecutándose correctamente")
                return True
            else:
                # La aplicación terminó inmediatamente, hay un error
                stdout, stderr = self.app_process.communicate()
                self.logger.error(f"Aplicación terminó inmediatamente")
                if stdout:
                    self.logger.error(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                if stderr:
                    self.logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                
                self.app_process = None
                return False
                
        except Exception as e:
            self.logger.error(f"Error iniciando aplicación: {e}")
            self.app_process = None
            return False
    
    def _stop_application(self):
        """Detener la aplicación"""
        if self.app_process is not None:
            try:
                self.logger.info(f"Deteniendo aplicación (PID: {self.app_process.pid})")
                
                # Intentar terminación gentil primero
                self.app_process.terminate()
                
                # Esperar hasta 10 segundos para que termine
                try:
                    self.app_process.wait(timeout=10)
                    self.logger.info("Aplicación terminada correctamente")
                except subprocess.TimeoutExpired:
                    # Si no termina, forzar terminación
                    self.logger.warning("Aplicación no respondió, forzando terminación")
                    self.app_process.kill()
                    self.app_process.wait()
                    
            except Exception as e:
                self.logger.error(f"Error deteniendo aplicación: {e}")
            finally:
                self.app_process = None
    
    def _find_python(self):
        """Buscar ejecutable de Python en el sistema"""
        possible_paths = [
            r'C:\Python\python.exe',
            r'C:\Python39\python.exe',
            r'C:\Python38\python.exe',
            r'C:\Python37\python.exe',
            r'C:\Program Files\Python39\python.exe',
            r'C:\Program Files\Python38\python.exe',
            r'C:\Program Files\Python37\python.exe',
            r'C:\Program Files (x86)\Python39\python.exe',
            r'C:\Program Files (x86)\Python38\python.exe',
        ]
        
        # Buscar en PATH primero
        try:
            result = subprocess.run(
                ['where', 'python'], 
                capture_output=True, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                python_path = result.stdout.strip().split('\n')[0]
                if os.path.exists(python_path):
                    return python_path
        except:
            pass
        
        # Buscar en rutas conocidas
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Último intento: python sin ruta
        try:
            result = subprocess.run(
                ['python', '--version'], 
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return 'python'
        except:
            pass
        
        return None

def install_service():
    """Instalar el servicio"""
    try:
        win32serviceutil.InstallService(
            EmergencySystemService._svc_reg_class_,
            EmergencySystemService._svc_name_,
            EmergencySystemService._svc_display_name_,
            description=EmergencySystemService._svc_description_
        )
        print("✅ Servicio instalado correctamente")
        
        # Configurar para inicio automático
        try:
            subprocess.run(['sc', 'config', EmergencySystemService._svc_name_, 'start=', 'auto'], 
                         check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print("✅ Servicio configurado para inicio automático")
        except:
            print("⚠️ No se pudo configurar inicio automático")
        
        return True
        
    except Exception as e:
        print(f"❌ Error instalando servicio: {e}")
        return False

def remove_service():
    """Desinstalar el servicio"""
    try:
        # Detener servicio primero
        try:
            win32serviceutil.StopService(EmergencySystemService._svc_name_)
            print("🛑 Servicio detenido")
            time.sleep(2)
        except:
            pass
        
        # Remover servicio
        win32serviceutil.RemoveService(EmergencySystemService._svc_name_)
        print("✅ Servicio desinstalado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error desinstalando servicio: {e}")
        return False

def start_service():
    """Iniciar el servicio"""
    try:
        win32serviceutil.StartService(EmergencySystemService._svc_name_)
        print("▶️ Servicio iniciado")
        return True
    except Exception as e:
        print(f"❌ Error iniciando servicio: {e}")
        return False

def stop_service():
    """Detener el servicio"""
    try:
        win32serviceutil.StopService(EmergencySystemService._svc_name_)
        print("⏹️ Servicio detenido")
        return True
    except Exception as e:
        print(f"❌ Error deteniendo servicio: {e}")
        return False

def status_service():
    """Verificar estado del servicio"""
    try:
        status = win32serviceutil.QueryServiceStatus(EmergencySystemService._svc_name_)[1]
        
        status_names = {
            win32service.SERVICE_STOPPED: "DETENIDO",
            win32service.SERVICE_START_PENDING: "INICIANDO",
            win32service.SERVICE_STOP_PENDING: "DETENIENDO",
            win32service.SERVICE_RUNNING: "EJECUTÁNDOSE",
            win32service.SERVICE_CONTINUE_PENDING: "REANUDANDO",
            win32service.SERVICE_PAUSE_PENDING: "PAUSANDO",
            win32service.SERVICE_PAUSED: "PAUSADO"
        }
        
        status_name = status_names.get(status, f"DESCONOCIDO ({status})")
        print(f"📊 Estado del servicio: {status_name}")
        
        return status
        
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        return None

def main():
    """Función principal"""
    print("🚨 SISTEMA DE EMERGENCIAS VILLA ALLENDE")
    print("   Gestión de Servicio Windows v2.0")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        # Sin argumentos, ejecutar como servicio
        win32serviceutil.HandleCommandLine(EmergencySystemService)
    else:
        action = sys.argv[1].lower()
        
        if action == 'install':
            print("📦 Instalando servicio...")
            if install_service():
                print("\n✅ Instalación completada")
                print("💡 Use 'python emergency_service.py start' para iniciar")
            
        elif action == 'remove' or action == 'uninstall':
            print("🗑️ Desinstalando servicio...")
            if remove_service():
                print("\n✅ Desinstalación completada")
            
        elif action == 'start':
            print("▶️ Iniciando servicio...")
            if start_service():
                print("\n✅ Servicio iniciado correctamente")
                print("🌐 La aplicación debería estar disponible en http://localhost:5000")
            
        elif action == 'stop':
            print("⏹️ Deteniendo servicio...")
            if stop_service():
                print("\n✅ Servicio detenido correctamente")
            
        elif action == 'restart':
            print("🔄 Reiniciando servicio...")
            stop_service()
            time.sleep(3)
            if start_service():
                print("\n✅ Servicio reiniciado correctamente")
            
        elif action == 'status':
            print("📊 Verificando estado del servicio...")
            status_service()
            
        elif action == 'debug':
            print("🐛 Ejecutando en modo debug...")
            # Ejecutar directamente sin servicio para debug
            service = EmergencySystemService([])
            try:
                service.SvcDoRun()
            except KeyboardInterrupt:
                print("\n🛑 Detenido por usuario")
                service.SvcStop()
            
        else:
            print("❓ Comandos disponibles:")
            print("  install   - Instalar servicio")
            print("  remove    - Desinstalar servicio")
            print("  start     - Iniciar servicio")
            print("  stop      - Detener servicio")
            print("  restart   - Reiniciar servicio")
            print("  status    - Ver estado del servicio")
            print("  debug     - Ejecutar en modo debug")

if __name__ == '__main__':
    main()
