@echo off
setlocal enabledelayedexpansion

:: ==========================================
:: Sistema de Emergencias Villa Allende v2.0
:: Script Final - Sin caracteres especiales
:: ==========================================

title Sistema de Emergencias Villa Allende v2.0

echo.
echo ================================================
echo SISTEMA DE EMERGENCIAS VILLA ALLENDE v2.0
echo Script Final - Version Limpia
echo ================================================
echo.

:: Verificar Python
echo Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    echo Instale Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python %PYTHON_VERSION% encontrado
echo.

:: Verificar que BD existe
if not exist "emergency_system.db" (
    echo ERROR: Base de datos no existe
    echo Ejecute primero: python fix_final.py
    pause
    exit /b 1
)

echo OK: Base de datos encontrada
echo.

:: Mostrar informacion
echo INICIANDO SISTEMA LIMPIO
echo ================================================
echo URL: http://localhost:5000
echo Usuario: admin
echo Password: 123456
echo.
echo IMPORTANTE:
echo - Cambiar password de admin despues del login
echo - Para detener presione Ctrl+C
echo ================================================
echo.

:: Iniciar aplicacion
echo Iniciando aplicacion...
python start_clean.py

:: Mensaje final
echo.
echo ================================================
echo Sistema finalizado
echo ================================================
pause