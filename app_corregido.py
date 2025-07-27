#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Aplicación Principal Flask - Versión Corregida

Características:
- Base de datos SQLite con encriptación
- Sistema de usuarios con roles
- Gestión completa de llamados de emergencia
- Protocolo 107 implementado
- Integración WhatsApp
- Sistema de backup y restauración
- Campo email agregado en tabla personas
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
import sqlite3
import shutil
import csv
import io
import base64
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergency-system-villa-allende-2024-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emergency_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Crear directorios necesarios
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Importar modelos
from models import *

# Inicializar extensiones
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debe iniciar sesión para acceder.'

# Importar utilidades (con manejo de errores)
try:
    from utils.backup import BackupManager
    from utils.whatsapp import WhatsAppManager
    backup_manager = BackupManager(app, db)
    whatsapp_manager = WhatsAppManager()
except ImportError as e:
    logging.warning(f"No se pudieron cargar algunas utilidades: {e}")
    backup_manager = None
    whatsapp_manager = None

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# =============== FUNCIONES DE INICIALIZACIÓN ===============

def init_database():
    """Inicializar base de datos con datos por defecto"""
    try:
        # Ejecutar migración primero
        from migrate_database import DatabaseMigrator
        migrator = DatabaseMigrator()
        migrator.run_migration()
        
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario admin si no existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                password_hash=generate_password_hash('123456'),
                nombre='Administrador',
                apellido='Sistema',
                email='admin@villaallende.gov.ar',
                rol='admin'
            )
            db.session.add(admin)
            
            # Crear guardia de inicialización
            guardia = Guardia(
                usuario_id=1,  # Admin user
                actividad="🚀 Sistema inicializado - Base de datos creada",
                tipo='sistema'
            )
            db.session.add(guardia)
            
            db.session.commit()
            logging.info("Usuario administrador creado: admin / 123456")
        
        # Verificar configuraciones por defecto
        init_default_configurations()
        
        logging.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logging.error(f"Error inicializando base de datos: {e}")
        raise

def init_default_configurations():
    """Inicializar configuraciones por defecto"""
    default_configs = [
        ('whatsapp_token', '', 'Token de API WhatsApp'),
        ('whatsapp_uid', '', 'UID del número WhatsApp'),
        ('telefono_demva', '', 'Teléfono DEMVA'),
        ('telefono_cec', '', 'Teléfono CEC'),
        ('telefono_telemedicina', '', 'Teléfono Telemedicina'),
        ('telefono_bomberos', '', 'Teléfono Bomberos'),
        ('telefono_seguridad', '', 'Teléfono Seguridad'),
        ('telefono_defensa', '', 'Teléfono Defensa Civil'),
        ('telefono_supervisor', '', 'Teléfono Supervisor'),
        ('logo_sistema', '', 'Logo del sistema'),
        ('version_sistema', '2.0.0', 'Versión del sistema'),
    ]
    
    for clave, valor, descripcion in default_configs:
        config = Configuracion.query.filter_by(clave=clave).first()
        if not config:
            config = Configuracion(
                clave=clave,
                valor=valor,
                descripcion=descripcion
            )
            db.session.add(config)
    
    db.session.commit()

# =============== RUTAS DE AUTENTICACIÓN ===============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = Usuario.query.filter_by(username=username, activo=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Verificar si el usuario está bloqueado
            if user.bloqueado_hasta and user.bloqueado_hasta > datetime.utcnow():
                return jsonify({
                    'success': False, 
                    'message': f'Usuario bloqueado hasta {user.bloqueado_hasta.strftime("%d/%m/%Y %H:%M")}'
                })
            
            # Resetear intentos fallidos
            user.intentos_login = 0
            user.bloqueado_hasta = None
            
            login_user(user)
            user.ultimo_login = datetime.utcnow()
            user.llamados_atendidos = user.llamados_atendidos or 0
            db.session.commit()
            
            # Registrar en guardias
            guardia = Guardia(
                usuario_id=user.id,
                actividad=f"🚪 Inicio de sesión - Usuario: {user.nombre} ({user.rol})",
                tipo='sistema'
            )
            db.session.add(guardia)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'nombre': user.nombre,
                    'apellido': user.apellido,
                    'rol': user.rol
                }
            })
        
        # Login fallido
        if user:
            user.intentos_login = (user.intentos_login or 0) + 1
            if user.intentos_login >= 5:
                user.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=30)
                db.session.commit()
                return jsonify({
                    'success': False, 
                    'message': 'Usuario bloqueado por 30 minutos debido a múltiples intentos fallidos'
                })
            db.session.commit()
        
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Registrar en guardias
    guardia = Guardia(
        usuario_id=current_user.id,
        actividad=f"🚪 Cierre de sesión - Usuario: {current_user.nombre}",
        tipo='sistema'
    )
    db.session.add(guardia)
    db.session.commit()
    
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('login'))

# =============== RUTAS PRINCIPALES ===============

@app.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas para el dashboard
    stats = {
        'total_llamados': Llamado.query.count(),
        'llamados_hoy': Llamado.query.filter(
            Llamado.fecha >= datetime.utcnow().date()
        ).count(),
        'total_personas': Persona.query.filter_by(activo=True).count(),
        'usuarios_activos': Usuario.query.filter_by(activo=True).count(),
        'total_guardias': Guardia.query.count()
    }
    
    # Últimos llamados
    ultimos_llamados = Llamado.query.order_by(Llamado.fecha.desc()).limit(10).all()
    
    return render_template('dashboard.html', stats=stats, ultimos_llamados=ultimos_llamados)

@app.route('/llamados')
@login_required
def llamados():
    return render_template('llamados.html')

@app.route('/consultas')
@login_required
def consultas():
    return render_template('consultas.html')

@app.route('/personas')
@login_required
def personas():
    return render_template('personas.html')

@app.route('/guardias')
@login_required
def guardias():
    return render_template('guardias.html')

@app.route('/configuracion')
@login_required
def configuracion():
    if current_user.rol != 'admin':
        flash('Solo los administradores pueden acceder a esta sección', 'error')
        return redirect(url_for('dashboard'))
    return render_template('configuracion.html')

# =============== API ENDPOINTS - LLAMADOS ===============

@app.route('/api/llamados', methods=['GET', 'POST'])
@login_required
def api_llamados():
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            # Crear nuevo llamado
            llamado = Llamado(
                telefono=data['telefono'],
                nombre=data['nombre'],
                apellido=data['apellido'],
                dni=data.get('dni', ''),
                calle=data['calle'],
                numero=data.get('numero', ''),
                entre_calles=data.get('entre_calles', ''),
                barrio=data['barrio'],
                observaciones_iniciales=data.get('observaciones_iniciales', ''),
                tipo=data['tipo'],
                prioridad=data.get('prioridad', 'verde'),
                via_publica=data.get('via_publica', 'domicilio'),
                usuario_id=current_user.id,
                triage_data=json.dumps(data.get('triage_data', {}))
            )
            
            db.session.add(llamado)
            db.session.flush()  # Para obtener el ID
            
            # Incrementar contador de llamados del usuario
            current_user.llamados_atendidos = (current_user.llamados_atendidos or 0) + 1
            
            # Registrar en guardias
            guardia = Guardia(
                usuario_id=current_user.id,
                actividad=f"📞 Llamado #{llamado.id} registrado - {data['tipo'].upper()} - {data['nombre']} {data['apellido']} - Prioridad: {data.get('prioridad', 'verde').upper()}",
                tipo='llamado'
            )
            db.session.add(guardia)
            
            db.session.commit()
            
            # Enviar WhatsApp si está configurado
            if whatsapp_manager and data.get('enviar_whatsapp', False):
                try:
                    mensaje = whatsapp_manager.crear_mensaje_llamado(llamado)
                    destinatarios = whatsapp_manager.obtener_destinatarios(llamado)
                    
                    for destinatario in destinatarios:
                        if whatsapp_manager.enviar_mensaje(destinatario, mensaje):
                            llamado.whatsapp_enviado = True
                            
                            # Registrar envío en guardias
                            guardia_wp = Guardia(
                                usuario_id=current_user.id,
                                actividad=f"📱 WhatsApp enviado para Llamado #{llamado.id} a {destinatario}",
                                tipo='whatsapp'
                            )
                            db.session.add(guardia_wp)
                    
                    db.session.commit()
                except Exception as e:
                    logging.error(f"Error enviando WhatsApp: {e}")
            
            return jsonify({
                'success': True,
                'llamado_id': llamado.id,
                'message': f'Llamado #{llamado.id} registrado exitosamente'
            })
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creando llamado: {e}")
            return jsonify({'success': False, 'message': f'Error creando llamado: {str(e)}'})
    
    else:  # GET
        # Aplicar filtros
        query = Llamado.query
        
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        tipo = request.args.get('tipo')
        estado = request.args.get('estado')
        prioridad = request.args.get('prioridad')
        
        if fecha_desde:
            query = query.filter(Llamado.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d'))
        if fecha_hasta:
            query = query.filter(Llamado.fecha <= datetime.strptime(fecha_hasta + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        if tipo:
            query = query.filter(Llamado.tipo == tipo)
        if estado:
            query = query.filter(Llamado.estado == estado)
        if prioridad:
            query = query.filter(Llamado.prioridad == prioridad)
        
        llamados = query.order_by(Llamado.fecha.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'llamados': [{
                'id': l.id,
                'fecha': l.fecha.isoformat(),
                'telefono': l.telefono,
                'nombre': l.nombre,
                'apellido': l.apellido,
                'direccion_completa': l.direccion_completa,
                'tipo': l.tipo,
                'prioridad': l.prioridad,
                'estado': l.estado,
                'usuario': l.usuario.nombre_completo,
                'whatsapp_enviado': l.whatsapp_enviado
            } for l in llamados]
        })

# =============== API ENDPOINTS - PERSONAS (CORREGIDO CON EMAIL) ===============

@app.route('/api/personas', methods=['GET', 'POST'])
@login_required
def api_personas():
    if request.method == 'POST':
        data = request.get_json()
        
        # Verificar si ya existe una persona con el mismo DNI o teléfono
        persona_existente = None
        if data.get('dni'):
            persona_existente = Persona.query.filter_by(dni=data['dni'], activo=True).first()
        if not persona_existente and data.get('telefono'):
            persona_existente = Persona.query.filter(
                (Persona.telefono == data['telefono']) | (Persona.celular == data['telefono']),
                Persona.activo == True
            ).first()
        
        if persona_existente:
            return jsonify({
                'success': False, 
                'message': f'Ya existe una persona registrada con esos datos (ID: {persona_existente.id})'
            })
        
        persona = Persona(
            apellido=data['apellido'],
            nombre=data['nombre'],
            dni=data.get('dni', ''),
            telefono=data.get('telefono', ''),
            celular=data.get('celular', ''),
            email=data.get('email', ''),  # *** CAMPO EMAIL AGREGADO ***
            direccion=data.get('direccion', ''),
            barrio=data.get('barrio', ''),
            observaciones=data.get('observaciones', '')
        )
        
        db.session.add(persona)
        db.session.commit()
        
        # Registrar en guardias
        guardia = Guardia(
            usuario_id=current_user.id,
            actividad=f"👤 Persona #{persona.id} registrada - {persona.nombre_completo}",
            tipo='operacion'
        )
        db.session.add(guardia)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'persona_id': persona.id,
            'message': f'Persona #{persona.id} registrada exitosamente'
        })
    
    else:  # GET
        query = Persona.query.filter_by(activo=True)
        
        # Aplicar filtros
        nombre = request.args.get('nombre')
        telefono = request.args.get('telefono')
        barrio = request.args.get('barrio')
        email = request.args.get('email')  # *** FILTRO EMAIL AGREGADO ***
        
        if nombre:
            query = query.filter(
                (Persona.nombre.ilike(f'%{nombre}%')) |
                (Persona.apellido.ilike(f'%{nombre}%'))
            )
        if telefono:
            query = query.filter(
                (Persona.telefono.contains(telefono)) |
                (Persona.celular.contains(telefono))
            )
        if barrio:
            query = query.filter(Persona.barrio == barrio)
        if email:  # *** FILTRO EMAIL IMPLEMENTADO ***
            query = query.filter(Persona.email.ilike(f'%{email}%'))
        
        personas = query.order_by(Persona.apellido).all()
        
        return jsonify({
            'success': True,
            'personas': [{
                'id': p.id,
                'apellido': p.apellido,
                'nombre': p.nombre,
                'dni': p.dni,
                'telefono': p.telefono,
                'celular': p.celular,
                'email': p.email,  # *** CAMPO EMAIL EN RESPUESTA ***
                'direccion': p.direccion,
                'barrio': p.barrio,
                'observaciones': p.observaciones,
                'fecha_creacion': p.fecha_creacion.isoformat()
            } for p in personas]
        })

@app.route('/api/personas/buscar')
@login_required
def api_buscar_persona():
    telefono = request.args.get('telefono')
    dni = request.args.get('dni')
    email = request.args.get('email')  # *** BÚSQUEDA POR EMAIL AGREGADA ***
    
    persona = None
    
    if telefono:
        persona = Persona.query.filter(
            (Persona.telefono == telefono) | (Persona.celular == telefono),
            Persona.activo == True
        ).first()
    elif dni:
        persona = Persona.query.filter_by(dni=dni, activo=True).first()
    elif email:  # *** BÚSQUEDA POR EMAIL IMPLEMENTADA ***
        persona = Persona.query.filter_by(email=email, activo=True).first()
    
    if persona:
        return jsonify({
            'success': True,
            'persona': {
                'id': persona.id,
                'apellido': persona.apellido,
                'nombre': persona.nombre,
                'dni': persona.dni,
                'telefono': persona.telefono,
                'celular': persona.celular,
                'email': persona.email,  # *** CAMPO EMAIL EN RESPUESTA ***
                'direccion': persona.direccion,
                'barrio': persona.barrio,
                'observaciones': persona.observaciones
            }
        })
    
    return jsonify({'success': False, 'message': 'Persona no encontrada'})

# =============== API ENDPOINTS - GUARDIAS ===============

@app.route('/api/guardias', methods=['GET', 'POST'])
@login_required
def api_guardias():
    if request.method == 'POST':
        data = request.get_json()
        
        guardia = Guardia(
            usuario_id=current_user.id,
            actividad=data['actividad'],
            tipo=data.get('tipo', 'operacion')
        )
        
        db.session.add(guardia)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'guardia_id': guardia.id,
            'message': 'Registro de guardia agregado exitosamente'
        })
    
    else:  # GET
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        tipo = request.args.get('tipo')
        
        query = Guardia.query
        
        if fecha_desde:
            query = query.filter(Guardia.fecha >= datetime.strptime(fecha_desde, '%Y-%m-%d'))
        if fecha_hasta:
            query = query.filter(Guardia.fecha <= datetime.strptime(fecha_hasta + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        if tipo:
            query = query.filter(Guardia.tipo == tipo)
        
        guardias = query.order_by(Guardia.fecha.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'guardias': [{
                'id': g.id,
                'fecha': g.fecha.isoformat(),
                'usuario': g.usuario.nombre_completo,
                'actividad': g.actividad,
                'tipo': g.tipo
            } for g in guardias]
        })

# =============== API ENDPOINTS - CONFIGURACIÓN ===============

@app.route('/api/configuracion', methods=['GET', 'POST'])
@login_required
def api_configuracion():
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    if request.method == 'POST':
        data = request.get_json()
        
        for clave, valor in data.items():
            config = Configuracion.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
                config.fecha_modificacion = datetime.utcnow()
            else:
                config = Configuracion(clave=clave, valor=valor)
                db.session.add(config)
        
        db.session.commit()
        
        # Registrar en guardias
        guardia = Guardia(
            usuario_id=current_user.id,
            actividad=f"⚙️ Configuración actualizada - {len(data)} parámetros modificados",
            tipo='sistema'
        )
        db.session.add(guardia)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Configuración actualizada correctamente'})
    
    else:  # GET
        configs = Configuracion.query.all()
        return jsonify({
            'success': True,
            'configuracion': {config.clave: config.valor for config in configs}
        })

# =============== FUNCIONES DE UTILIDAD ===============

@app.context_processor
def inject_globals():
    """Inyectar variables globales en templates"""
    return {
        'BARRIOS': BARRIOS,
        'TIPOS_EMERGENCIA': TIPOS_EMERGENCIA,
        'PRIORIDADES': PRIORIDADES,
        'ROLES': ROLES,
        'TIPOS_GUARDIA': TIPOS_GUARDIA,
        'datetime': datetime
    }

# =============== MANEJO DE ERRORES ===============

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Página no encontrada"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Error interno del servidor"), 500

# =============== INICIALIZACIÓN ===============

if __name__ == '__main__':
    # Inicializar base de datos
    with app.app_context():
        init_database()
    
    # Ejecutar aplicación
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )