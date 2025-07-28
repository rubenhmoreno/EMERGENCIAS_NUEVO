#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Aplicación Principal - Versión Sin Emojis

Esta versión elimina todos los emojis y caracteres especiales
para garantizar compatibilidad con Windows.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
import shutil
import csv
import io
import base64
import logging
from datetime import datetime, timedelta

# Configurar logging SIN emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Crear directorios necesarios
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('backups', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('ssl', exist_ok=True)

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergency-system-villa-allende-2024-secure'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emergency_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debe iniciar sesión para acceder.'

# =============== CONSTANTES ===============
BARRIOS = [
    'Altos del Valle', 'Altos del Chateau', 'Barrio Norte', 'Barrio Sur',
    'Centro', 'Country Club', 'El Libertador', 'La Alameda',
    'La Estanzuela', 'Las Caletas', 'Los Aromos', 'Los Jazmines',
    'Los Naranjos', 'Los Paraísos', 'Manantiales', 'Parque Norte',
    'Quebrada de las Rosas', 'Residencial Norte', 'San Alfonso',
    'San Ignacio', 'Valle del Golf', 'Villa del Dique', 'Otro'
]

TIPOS_EMERGENCIA = [
    'Médica', 'Bomberos', 'Seguridad', 'Defensa Civil', 'Otros'
]

PRIORIDADES = ['rojo', 'amarillo', 'verde']
ROLES = ['admin', 'supervisor', 'operador']
TIPOS_GUARDIA = ['novedad', 'incidente', 'llamado', 'administrativo', 'sistema']

# =============== MODELOS DE BASE DE DATOS ===============

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    rol = db.Column(db.String(20), nullable=False, default='operador')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    llamados_atendidos = db.Column(db.Integer, default=0)
    intentos_login = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Persona(db.Model):
    __tablename__ = 'personas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)  # CAMPO EMAIL
    direccion = db.Column(db.String(200), nullable=True)
    barrio = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text, nullable=True)
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def edad(self):
        if self.fecha_nacimiento:
            today = datetime.today().date()
            return today.year - self.fecha_nacimiento.year - \
                   ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None

class Llamado(db.Model):
    __tablename__ = 'llamados'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Datos del llamante
    nombre_llamante = db.Column(db.String(100), nullable=False)
    telefono_llamante = db.Column(db.String(20), nullable=True)
    
    # Datos del afectado
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=True)
    nombre_afectado = db.Column(db.String(100), nullable=True)
    edad_afectado = db.Column(db.Integer, nullable=True)
    sexo_afectado = db.Column(db.String(1), nullable=True)
    
    # Ubicación
    direccion = db.Column(db.String(200), nullable=False)
    barrio = db.Column(db.String(100), nullable=False)
    es_via_publica = db.Column(db.Boolean, default=False)
    punto_referencia = db.Column(db.String(200), nullable=True)
    
    # Emergencia
    tipo_emergencia = db.Column(db.String(50), nullable=False)
    motivo_llamado = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(10), nullable=False)
    protocolo_107 = db.Column(db.Text, nullable=True)
    
    # Estado
    estado = db.Column(db.String(20), default='activo')
    derivado_a = db.Column(db.String(100), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    
    # WhatsApp
    whatsapp_enviado = db.Column(db.Boolean, default=False)
    whatsapp_respuesta = db.Column(db.Text, nullable=True)

class Guardia(db.Model):
    __tablename__ = 'guardias'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    actividad = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), default='novedad')
    observaciones = db.Column(db.Text, nullable=True)

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.String(200), nullable=True)
    categoria = db.Column(db.String(50), default='general')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow)

# =============== FUNCIONES DE LOGIN ===============

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# =============== FUNCIONES DE INICIALIZACIÓN ===============

def init_database():
    """Inicializar base de datos SIMPLE - sin migraciones complejas"""
    try:
        # NO ejecutar migración compleja, solo crear tablas si no existen
        db.create_all()
        
        # Crear usuario admin si no existe - CONSULTA SIMPLE
        try:
            # Usar consulta SQL directa para evitar problemas de ORM
            conn = sqlite3.connect('emergency_system.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                # Crear admin con SQL directo
                password_hash = generate_password_hash('123456')
                cursor.execute("""
                    INSERT INTO usuarios (
                        username, password_hash, nombre, apellido, email, rol, 
                        activo, llamados_atendidos, intentos_login
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'admin', password_hash, 'Administrador', 'Sistema',
                    'admin@villaallende.gov.ar', 'admin', 1, 0, 0
                ))
                
                # Crear guardia inicial
                cursor.execute("""
                    INSERT INTO guardias (usuario_id, actividad, tipo)
                    VALUES (1, 'Sistema inicializado con BD limpia', 'sistema')
                """)
                
                conn.commit()
                logging.info("Usuario administrador creado: admin / 123456")
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error en inicialización simple: {e}")
        
        logging.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        logging.error(f"Error inicializando base de datos: {e}")
        raise

# =============== RUTAS PRINCIPALES ===============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = Usuario.query.filter_by(username=username, activo=True).first()
        
        if usuario and check_password_hash(usuario.password_hash, password):
            # Verificar bloqueo
            if usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.utcnow():
                flash('Usuario bloqueado temporalmente. Intente más tarde.', 'error')
                return render_template('login.html')
            
            # Login exitoso
            login_user(usuario)
            usuario.ultimo_login = datetime.utcnow()
            usuario.intentos_login = 0
            usuario.bloqueado_hasta = None
            
            try:
                db.session.commit()
            except:
                pass  # No fallar por problemas de guardado
            
            return redirect(url_for('dashboard'))
        else:
            if usuario:
                usuario.intentos_login += 1
                if usuario.intentos_login >= 5:
                    usuario.bloqueado_hasta = datetime.utcnow() + timedelta(minutes=30)
                try:
                    db.session.commit()
                except:
                    pass
            
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas básicas
    stats = {
        'llamados_hoy': Llamado.query.filter(
            Llamado.fecha >= datetime.now().replace(hour=0, minute=0, second=0)
        ).count(),
        'llamados_activos': Llamado.query.filter_by(estado='activo').count(),
        'total_personas': Persona.query.count(),
        'usuarios_activos': Usuario.query.filter_by(activo=True).count()
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/llamados')
@login_required
def llamados():
    return render_template('llamados.html')

@app.route('/personas')
@login_required
def personas():
    return render_template('personas.html')

@app.route('/guardias')
@login_required
def guardias():
    return render_template('guardias.html')

@app.route('/consultas')
@login_required
def consultas():
    return render_template('consultas.html')

@app.route('/configuracion')
@login_required
def configuracion():
    if current_user.rol not in ['admin', 'supervisor']:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    return render_template('configuracion.html')

# =============== API ENDPOINTS BÁSICOS ===============

@app.route('/api/llamados', methods=['GET', 'POST'])
@login_required
def api_llamados():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Crear llamado básico
            llamado = Llamado(
                usuario_id=current_user.id,
                nombre_llamante=data.get('nombre_llamante', ''),
                telefono_llamante=data.get('telefono_llamante', ''),
                nombre_afectado=data.get('nombre_afectado', ''),
                direccion=data.get('direccion', ''),
                barrio=data.get('barrio', ''),
                tipo_emergencia=data.get('tipo_emergencia', ''),
                motivo_llamado=data.get('motivo_llamado', ''),
                prioridad=data.get('prioridad', 'verde')
            )
            
            db.session.add(llamado)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Llamado registrado correctamente',
                'llamado_id': llamado.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            llamados = Llamado.query.order_by(Llamado.fecha.desc()).limit(50).all()
            
            return jsonify({
                'success': True,
                'llamados': [{
                    'id': l.id,
                    'fecha': l.fecha.strftime('%d/%m/%Y %H:%M'),
                    'tipo_emergencia': l.tipo_emergencia,
                    'prioridad': l.prioridad,
                    'direccion': l.direccion,
                    'barrio': l.barrio,
                    'estado': l.estado
                } for l in llamados]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/personas', methods=['GET', 'POST'])
@login_required
def api_personas():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            persona = Persona(
                nombre=data.get('nombre', ''),
                apellido=data.get('apellido', ''),
                documento=data.get('documento', ''),
                telefono=data.get('telefono', ''),
                email=data.get('email', ''),  # CAMPO EMAIL
                direccion=data.get('direccion', ''),
                barrio=data.get('barrio', '')
            )
            
            db.session.add(persona)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Persona registrada correctamente',
                'persona_id': persona.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            buscar = request.args.get('q', '')
            
            query = Persona.query
            if buscar:
                query = query.filter(
                    (Persona.nombre.contains(buscar)) |
                    (Persona.apellido.contains(buscar)) |
                    (Persona.documento.contains(buscar)) |
                    (Persona.telefono.contains(buscar)) |
                    (Persona.email.contains(buscar))  # INCLUIR EMAIL
                )
            
            personas = query.order_by(Persona.apellido, Persona.nombre).limit(100).all()
            
            return jsonify({
                'success': True,
                'personas': [{
                    'id': p.id,
                    'nombre_completo': p.nombre_completo,
                    'documento': p.documento or '',
                    'telefono': p.telefono or '',
                    'email': p.email or '',  # INCLUIR EMAIL
                    'direccion': p.direccion or '',
                    'barrio': p.barrio or ''
                } for p in personas]
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

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
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Endpoint no encontrado'}), 404
    return "<h1>404 - Página no encontrada</h1>", 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500
    return "<h1>500 - Error interno del servidor</h1>", 500

# =============== INICIALIZACIÓN ===============

if __name__ == '__main__':
    # Inicializar base de datos con contexto de aplicación
    with app.app_context():
        init_database()
    
    # Ejecutar aplicación
    app.run(
        debug=False,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )