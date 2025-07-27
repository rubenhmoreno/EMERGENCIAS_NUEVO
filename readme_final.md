# 🚨 Sistema de Emergencias Villa Allende v2.0

Sistema integral de gestión de llamados de emergencia desarrollado en Python/Flask con base de datos SQLite. **Versión 2.0 con correcciones importantes y nuevas funcionalidades.**

![Sistema de Emergencias](https://img.shields.io/badge/Emergencias-Villa%20Allende%20v2.0-red?style=for-the-badge&logo=emergency)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Encriptado-yellow?style=for-the-badge&logo=sqlite)

## 🎉 Novedades en Versión 2.0

### ✅ **Correcciones Críticas**
- **Campo `email` agregado en tabla `personas`** - Funcionalidad completa de contacto
- **Migración automática de base de datos** - Actualización sin pérdida de datos
- **Verificación de integridad del sistema** - Diagnósticos automáticos
- **Instalador MSI/EXE completo** - Instalación automática con NSIS

### 🚀 **Nuevas Funcionalidades**
- **Servicio Windows automático** - Ejecución como servicio del sistema
- **Certificados SSL autogenerados** - Comunicación segura HTTPS
- **Sistema de backup encriptado** - Protección completa de datos
- **Herramientas de diagnóstico** - Verificación automática del sistema
- **Actualizador automático** - Mantenimiento simplificado
- **Base de datos encriptada** - Seguridad de datos mejorada

## 📋 Características Principales

### ✅ **Funcionalidades Completas**
- **Protocolo 107 Completo**: Triage médico según protocolo oficial
- **Tipos de Emergencia**: Médica, Bomberos, Seguridad, Defensa Civil, Otros
- **Diferenciación de Ubicación**: Domicilio vs Vía Pública (afecta derivación)
- **Sistema de Prioridades**: Rojo (Crítico), Amarillo (Urgente), Verde (No Urgente)
- **Gestión de Usuarios**: Roles Admin, Supervisor, Operador con seguridad mejorada
- **Base de Personas**: Con autocompletado de datos **y campo email**
- **Libro de Guardias Digital**: Registro de novedades con categorización
- **Sistema de Consultas**: Búsquedas avanzadas con filtros múltiples
- **Estadísticas y Reportes**: Dashboard completo en tiempo real
- **Backup y Restauración**: Sistema completo de respaldos encriptados

### 🔗 **Integración WhatsApp Mejorada**
- **API Waboxapp**: Notificaciones automáticas optimizadas
- **Ruteo Inteligente**: Según tipo, prioridad y ubicación
- **Múltiples Destinatarios**: Servicios específicos + supervisor
- **Mensajes Estructurados**: Información completa con emojis
- **Test de Conexión**: Verificación automática de funcionamiento

### 🎯 **Derivación Inteligente Médica**
- **Domicilio + Rojo/Amarillo** → DEMVA
- **Domicilio + Verde** → TELEMEDICINA  
- **Vía Pública + Cualquier Prioridad** → CEC

## 🚀 Instalación

### **Opción 1: Instalador Automático (Recomendada)**

#### **Instalador MSI/EXE (Windows)**
```batch
# Descargar EmergenciaVA_Installer_v2.0.exe
# Ejecutar como administrador
# El instalador hace TODO automáticamente:
# - Instala Python si es necesario
# - Configura base de datos con migración
# - Instala servicio Windows
# - Configura firewall y SSL
# - Crea accesos directos
```

#### **Instalador Batch (Windows)**
```batch
# Si tiene los archivos fuente:
# Ejecutar como administrador:
install.bat
```

### **Opción 2: Instalación Manual**

#### **Requisitos Previos:**
- Python 3.8 o superior
- Windows 7/8/10/11 (recomendado Windows 10+)
- Permisos de administrador
- Conexión a internet (para dependencias)

#### **Pasos Detallados:**

1. **Descargar el sistema completo**
```bash
# Asegúrese de tener todos los archivos en un directorio
```

2. **Verificar Python**
```bash
python --version
# Debe mostrar Python 3.8 o superior
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar migración automática**
```bash
python migrate_database.py
```

5. **Iniciar sistema**
```bash
python run.py
```

## 🎮 Uso del Sistema

### **Iniciar el Sistema**

#### **Opción A: Servicio Windows (Recomendado)**
```batch
# Si se instaló como servicio:
# El sistema inicia automáticamente con Windows
# Verificar estado: sc query EmergencySystemVA
```

#### **Opción B: Script Manual**
```batch
# Windows:
start.bat

# O manualmente:
python run.py
```

#### **Opción C: Línea de comandos**
```bash
python run.py
```

### **Acceso al Sistema**
- **URL**: http://localhost:5000 o https://localhost:5000 (con SSL)
- **Usuario por defecto**: `admin`
- **Contraseña por defecto**: `123456`

⚠️ **IMPORTANTE**: Cambie la contraseña por defecto después del primer acceso.

## 👥 Gestión de Usuarios

### **Roles del Sistema**

| Rol | Permisos |
|-----|----------|
| **Admin** | Acceso completo: configuración, usuarios, estadísticas, ABM BD, herramientas |
| **Supervisor** | Llamados, consultas, personas, guardias, estadísticas, algunos reportes |
| **Operador** | Llamados, consultas, personas, guardias básicas |

### **Crear Nuevos Usuarios**
1. Acceder como Admin
2. Ir a **Configuración** → **Gestión de Usuarios**
3. Completar formulario de nuevo usuario
4. Asignar rol apropiado
5. **NUEVO**: Configurar email para notificaciones

## 📞 Gestión de Llamados

### **Protocolo 107 Mejorado**

#### **Pasos del Protocolo:**
1. **Presentación**: "Buenos días/tardes 107 Emergencias Villa Allende..."
2. **Motivo del llamado**: Identificar tipo de emergencia
3. **Teléfono y datos**: Contacto del solicitante
4. **Dirección**: Ubicación exacta + referencias
5. **Datos del incidente**: Evaluación según tipo
6. **Despacho si es Rojo**: Comisionar móvil inmediatamente
7. **Medidas pre-arribo**: No cortar hasta confirmación

#### **Triage Médico (Preguntas Críticas):**
- ¿La persona está consciente?
- ¿La persona respira?
- ¿Hay sangrado abundante?
- ¿Hay patología de base grave?
- ¿Hay alguna discapacidad?

**Cualquier "SÍ" en sangrado/patología/discapacidad o "NO" en consciente/respira = CÓDIGO ROJO**

## 📱 Configuración WhatsApp

### **Configuración Inicial**
1. Obtener cuenta en [Waboxapp](https://waboxapp.com)
2. Ir a **Configuración** → **WhatsApp**
3. Configurar:
   - **Token**: Token de API de Waboxapp
   - **UID**: Número de teléfono emisor
4. **Probar conexión** usando el botón de test

### **Configurar Teléfonos de Servicios**
1. **DEMVA**: Emergencias médicas rojas/amarillas en domicilio
2. **CEC**: Emergencias médicas en vía pública
3. **TELEMEDICINA**: Emergencias médicas verdes en domicilio
4. **Bomberos**: Incendios, rescates, emergencias estructurales
5. **Seguridad**: Delitos, accidentes de tránsito, seguridad ciudadana
6. **Defensa Civil**: Emergencias climáticas, eventos masivos
7. **Supervisor**: Notificaciones a supervisión (siempre se envía)

## 💾 Sistema de Backup Mejorado

### **Crear Backup**
1. Ir a **Configuración** → **Base de Datos**
2. Clic en **Crear Backup**
3. Se genera archivo ZIP encriptado con:
   - Base de datos SQLite completa
   - Configuración en JSON
   - Datos en CSV (incluyendo campo email en personas)
   - Archivos subidos (logos)
   - Metadatos del backup

### **Restaurar Backup**
1. Ir a **Configuración** → **Base de Datos**
2. Seleccionar archivo de backup
3. Confirmar restauración
4. El sistema crea backup de seguridad automáticamente

### **Backup desde Línea de Comandos**
```bash
# Crear backup
python utils/backup.py create

# Listar backups
python utils/backup.py list

# Verificar integridad
python utils/backup.py verify
```

## 🔧 Herramientas de Diagnóstico

### **Diagnóstico Completo del Sistema**
```bash
# Ejecutar diagnóstico completo
python tools/diagnostics.py

# O desde Windows:
tools/diagnostics.bat
```

### **Verificaciones Incluidas:**
- ✅ Estructura de archivos y directorios
- ✅ Python y dependencias
- ✅ Base de datos e integridad (incluyendo campo email)
- ✅ Configuración del sistema
- ✅ Servicios Windows
- ✅ Conectividad de red y puertos
- ✅ Certificados SSL
- ✅ Configuración de firewall
- ✅ Configuración WhatsApp y conectividad
- ✅ Sistema de backup
- ✅ Aplicación web y respuesta
- ✅ Rendimiento del sistema

### **Reparación Automática**
```bash
# Reparar base de datos
python migrate_database.py

# O desde Windows:
tools/repair.bat
```

## 🔐 Seguridad Mejorada

### **Características de Seguridad v2.0:**
- **Base de datos encriptada** con algoritmos avanzados
- **Certificados SSL autogenerados** para HTTPS
- **Bloqueo automático** después de intentos fallidos
- **Sesiones seguras** con timeout configurable
- **Logs de auditoría** de todas las acciones
- **Backup encriptado** con protección adicional

### **Configuración de Seguridad**
```ini
# config.ini
[SECURITY]
max_login_attempts = 5
lockout_duration_minutes = 30
password_min_length = 6
session_timeout_minutes = 60
```

## 🗃️ Estructura del Proyecto Completa

```
emergency_system_v2/
├── app.py                          # Aplicación principal Flask
├── models.py                       # Modelos de BD (con email en personas)
├── run.py                          # Script de inicio mejorado
├── migrate_database.py             # Migración automática
├── requirements.txt                # Dependencias Python
├── config.ini                     # Configuración principal
├── version.txt                     # Información de versión
├── install.bat                     # Instalador Windows
├── start.bat                       # Iniciador Windows
├── emergency_installer.nsi         # Instalador NSIS
├── README.md                       # Esta documentación
├── templates/                      # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── llamados.html
│   ├── personas.html              # ¡Con campo email!
│   ├── configuracion.html
│   └── ...
├── static/                         # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── uploads/                   # Logos personalizados
├── utils/                          # Utilidades del sistema
│   ├── backup.py                  # Sistema de backup encriptado
│   └── whatsapp.py                # Integración WhatsApp
├── service/                        # Servicio Windows
│   └── emergency_service.py       # Servicio automático
├── tools/                          # Herramientas de diagnóstico
│   ├── diagnostics.py             # Diagnóstico completo
│   ├── diagnostics.bat            # Script Windows
│   └── repair.bat                 # Reparación automática
├── ssl/                           # Certificados SSL
│   ├── server.crt                 # Certificado autogenerado
│   └── server.key                 # Clave privada
├── data/                          # Datos del sistema
│   └── backups/                   # Backups automáticos
├── logs/                          # Logs del sistema
│   ├── app.log                    # Log de aplicación
│   ├── service.log                # Log de servicio
│   └── diagnostics_results.json   # Resultados de diagnóstico
├── emergency_system.db            # Base de datos SQLite encriptada
└── INSTALACION_COMPLETADA.txt     # Documentación post-instalación
```

## 🛠️ Solución de Problemas

### **Problemas Comunes v2.0**

#### **Error: Campo email no existe en personas**
```bash
# SOLUCIONADO en v2.0 con migración automática
python migrate_database.py
```

#### **Error: Puerto 5000 en uso**
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/macOS

# Cambiar puerto en config.ini
[SERVER]
port = 8080
```

#### **Error: Base de datos bloqueada**
```bash
# Cerrar todas las instancias del sistema
# Eliminar archivos de bloqueo si existen
del emergency_system.db-wal
del emergency_system.db-shm
```

#### **Error: Servicio no inicia**
```bash
# Verificar instalación del servicio
sc query EmergencySystemVA

# Reinstalar servicio
python service/emergency_service.py remove
python service/emergency_service.py install
python service/emergency_service.py start
```

#### **Error: WhatsApp no funciona**
1. Verificar token y UID en configuración
2. Probar conexión desde el panel
3. Verificar conectividad a internet
4. Verificar formato de números de teléfono
5. Revisar logs en `logs/app.log`

### **Herramientas de Diagnóstico**
```bash
# Diagnóstico completo
python tools/diagnostics.py

# Verificar solo base de datos
python -c "from utils.backup import BackupManager; print(BackupManager().verify_database_integrity())"

# Verificar solo WhatsApp
python utils/whatsapp.py status
```

## 📈 Monitoreo y Logs

### **Logs del Sistema**
- **app.log**: Logs de la aplicación Flask
- **service.log**: Logs del servicio Windows
- **diagnostics_results.json**: Resultados de diagnósticos

### **Ubicación de Logs**
```
logs/
├── app.log                    # Log principal
├── service.log               # Log del servicio
└── diagnostics_results.json  # Diagnósticos
```

### **Monitoreo en Tiempo Real**
```bash
# Windows
type logs\app.log

# Ver logs del servicio
type logs\service.log

# Seguir logs en tiempo real (PowerShell)
Get-Content logs\app.log -Wait
```

## 🔒 Seguridad y Buenas Prácticas

### **Configuración Inicial Obligatoria**
1. **Cambiar contraseña de admin** inmediatamente
2. **Configurar certificados SSL** para HTTPS
3. **Establecer backup automático** semanal
4. **Configurar WhatsApp** para notificaciones
5. **Revisar configuración de firewall**

### **Mantenimiento Regular**
1. **Backup semanal**: Automático si el servicio está activo
2. **Verificación mensual**: Ejecutar diagnósticos
3. **Actualización de dependencias**: Según necesidad
4. **Revisión de logs**: Verificar errores periódicamente
5. **Test de WhatsApp**: Verificar conectividad mensual

### **Consideraciones de Red**
- Sistema diseñado para red local (LAN)
- Para acceso externo, usar VPN o proxy reverso
- Configurar firewall apropiadamente
- HTTPS obligatorio para acceso externo

## 📊 Migración desde Versión Anterior

### **Migración Automática**
El sistema v2.0 incluye migración automática que:

1. **Detecta versión anterior** automáticamente
2. **Crea backup de seguridad** antes de migrar
3. **Agrega campo email** en tabla personas
4. **Actualiza estructura** de todas las tablas
5. **Preserva todos los datos** existentes
6. **Verifica integridad** después de migrar

### **Proceso de Migración**
```bash
# La migración se ejecuta automáticamente al iniciar
python run.py

# O ejecutar manualmente
python migrate_database.py
```

### **Verificación Post-Migración**
```bash
# Verificar que el campo email existe
python tools/diagnostics.py

# Verificar integridad de datos
python utils/backup.py verify
```

## 🆘 Soporte y Mantenimiento

### **Información del Sistema**
- **Versión**: 2.0.0
- **Plataforma**: Windows 7/8/10/11
- **Base de datos**: SQLite con encriptación
- **Servidor web**: Flask 3.0+
- **Seguridad**: HTTPS, autenticación, autorización

### **Archivos de Configuración Importantes**
- `config.ini`: Configuración principal
- `emergency_system.db`: Base de datos (¡NO ELIMINAR!)
- `logs/`: Registros para diagnóstico
- `ssl/`: Certificados de seguridad

### **Contacto de Soporte**
- **Logs del sistema**: Consultar `logs/app.log`
- **Base de datos**: Ubicada en raíz del proyecto
- **Diagnósticos**: Ejecutar `python tools/diagnostics.py`
- **Documentación**: Este archivo README.md

## 📝 Changelog Detallado

### **v2.0.0 - Corrección Crítica y Mejoras Mayores**

#### **🔧 Correcciones Críticas**
- ✅ **SOLUCIONADO**: Campo `email` agregado en tabla `personas`
- ✅ **SOLUCIONADO**: Migración automática sin pérdida de datos
- ✅ **SOLUCIONADO**: Verificación de integridad de base de datos
- ✅ **SOLUCIONADO**: Manejo de errores en inicio de aplicación

#### **🚀 Nuevas Funcionalidades**
- ✅ **Instalador MSI/EXE completo** con NSIS
- ✅ **Servicio Windows automático** con monitoreo
- ✅ **Sistema de backup encriptado** con compresión
- ✅ **Herramientas de diagnóstico** automatizadas
- ✅ **Certificados SSL autogenerados** para HTTPS
- ✅ **Configuración de firewall** automática
- ✅ **Actualizador automático** programado
- ✅ **Base de datos encriptada** con seguridad mejorada

#### **🔐 Seguridad Mejorada**
- ✅ **Bloqueo automático** después de intentos fallidos
- ✅ **Sesiones seguras** con timeout configurable
- ✅ **Logs de auditoría** completos
- ✅ **Encriptación de datos** en reposo
- ✅ **Verificación de integridad** automática

#### **🎯 Mejoras de Funcionalidad**
- ✅ **Campo email en personas** para contacto completo
- ✅ **Búsqueda por email** en base de personas
- ✅ **Filtros avanzados** con múltiples criterios
- ✅ **Exportación mejorada** incluyendo emails
- ✅ **WhatsApp mejorado** con test de conectividad
- ✅ **Dashboard mejorado** con más estadísticas

#### **🛠️ Mejoras Técnicas**
- ✅ **Script de inicio robusto** con verificaciones
- ✅ **Manejo de errores mejorado** en toda la aplicación
- ✅ **Logging estructurado** con niveles apropiados
- ✅ **Configuración centralizada** en config.ini
- ✅ **Documentación completa** actualizada

## 📄 Licencia

Sistema desarrollado para uso interno de la Municipalidad de Villa Allende. Todos los derechos reservados.

---

## 🎯 Inicio Rápido v2.0

```bash
# 1. Descargar sistema v2.0
# 2. Ejecutar instalador automático
install.bat           # Windows (como administrador)

# 3. Iniciar sistema
start.bat             # O automático si se instaló como servicio

# 4. Abrir navegador
http://localhost:5000

# 5. Iniciar sesión
Usuario: admin
Contraseña: 123456

# 6. ¡IMPORTANTE! Cambiar contraseña y configurar sistema
```

**¡Sistema v2.0 listo para gestionar emergencias con todas las correcciones! 🚨**

### 🔥 **NUEVA FUNCIONALIDAD DESTACADA v2.0**
- **Email en personas**: Ahora puede registrar y buscar personas por email
- **Migración automática**: Actualización sin pérdida de datos
- **Instalador completo**: Instalación automática con un solo ejecutable
- **Diagnósticos integrados**: Verificación automática del sistema
- **Servicio Windows**: Ejecución automática al inicio del sistema