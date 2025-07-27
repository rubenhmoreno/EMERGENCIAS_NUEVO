from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
import sqlite3
import shutil

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergency-system-villa-allende-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emergency_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Crear directorio de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('backups', exist_ok=True)

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debe iniciar sesión para acceder.'

# =============== MODELOS ===============
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
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Llamado(db.Model):
    __tablename__ = 'llamados'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Datos del llamante
    telefono = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=True)
    
    # Ubicación
    calle = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(10), nullable=True)
    entre_calles = db.Column(db.String(200), nullable=True)
    barrio = db.Column(db.String(100), nullable=False)
    
    # Descripción
    observaciones_iniciales = db.Column(db.Text, nullable=True)
    
    # Tipo y clasificación
    tipo = db.Column(db.String(20), nullable=False)
    prioridad = db.Column(db.String(10), nullable=False, default='verde')
    via_publica = db.Column(db.String(15), nullable=False, default='domicilio')
    
    # Estado y seguimiento
    estado = db.Column(db.String(20), nullable=False, default='en_curso')
    whatsapp_enviado = db.Column(db.Boolean, default=False)
    movil_en_domicilio = db.Column(db.Boolean, default=False)
    fecha_movil_domicilio = db.Column(db.DateTime, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    
    # Triage médico (JSON)
    triage_data = db.Column(db.Text, nullable=True)
    
    # Relación con usuario
    usuario = db.relationship('Usuario', backref='llamados_usuario')
    
    @property
    def direccion_completa(self):
        direccion = self.calle
        if self.numero:
            direccion += f" {self.numero}"
        direccion += f", {self.barrio}"
        return direccion

class Persona(db.Model):
    __tablename__ = 'personas'
    
    id = db.Column(db.Integer, primary_key=True)
    apellido = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    celular = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    barrio = db.Column(db.String(100), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

class Guardia(db.Model):
    __tablename__ = 'guardias'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    actividad = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='operacion')
    
    usuario = db.relationship('Usuario', backref='guardias_usuario')

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# =============== RUTAS DE AUTENTICACIÓN ===============

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.form.get('username')
                password = request.form.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Usuario y contraseña requeridos'})
            
            user = Usuario.query.filter_by(username=username, activo=True).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                user.ultimo_login = datetime.utcnow()
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
                        'rol': user.rol
                    }
                })
            
            return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})
            
        except Exception as e:
            print(f"Error en login: {e}")
            return jsonify({'success': False, 'message': 'Error interno del servidor'})
    
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

# =============== API ENDPOINTS ===============

@app.route('/api/llamados', methods=['GET', 'POST'])
@login_required
def api_llamados():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
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
            db.session.flush()
            
            # Registrar en guardias
            guardia = Guardia(
                usuario_id=current_user.id,
                actividad=f"📞 Llamado #{llamado.id} registrado - {data['tipo'].upper()} - {data['nombre']} {data['apellido']} - Prioridad: {data.get('prioridad', 'verde').upper()}",
                tipo='llamado'
            )
            db.session.add(guardia)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'llamado_id': llamado.id,
                'message': f'Llamado #{llamado.id} registrado exitosamente'
            })
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creando llamado: {e}")
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            # Obtener llamados con filtros
            query = Llamado.query
            
            llamados = query.order_by(Llamado.fecha.desc()).limit(50).all()
            
            return jsonify({
                'success': True,
                'llamados': [{
                    'id': l.id,
                    'fecha': l.fecha.isoformat(),
                    'tipo': l.tipo,
                    'prioridad': l.prioridad,
                    'estado': l.estado,
                    'nombre': l.nombre,
                    'apellido': l.apellido,
                    'telefono': l.telefono,
                    'direccion_completa': l.direccion_completa,
                    'via_publica': l.via_publica,
                    'usuario_nombre': l.usuario.nombre if l.usuario else 'Desconocido'
                } for l in llamados]
            })
        except Exception as e:
            print(f"Error obteniendo llamados: {e}")
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/llamados/<int:llamado_id>')
@login_required
def api_llamado_detalle(llamado_id):
    try:
        llamado = Llamado.query.get_or_404(llamado_id)
        
        return jsonify({
            'success': True,
            'llamado': {
                'id': llamado.id,
                'fecha': llamado.fecha.isoformat(),
                'tipo': llamado.tipo,
                'prioridad': llamado.prioridad,
                'estado': llamado.estado,
                'nombre': llamado.nombre,
                'apellido': llamado.apellido,
                'telefono': llamado.telefono,
                'dni': llamado.dni,
                'direccion_completa': llamado.direccion_completa,
                'entre_calles': llamado.entre_calles,
                'barrio': llamado.barrio,
                'via_publica': llamado.via_publica,
                'observaciones_iniciales': llamado.observaciones_iniciales,
                'triage_data': json.loads(llamado.triage_data) if llamado.triage_data else {},
                'whatsapp_enviado': llamado.whatsapp_enviado,
                'movil_en_domicilio': llamado.movil_en_domicilio,
                'usuario_nombre': llamado.usuario.nombre if llamado.usuario else 'Desconocido'
            }
        })
    except Exception as e:
        print(f"Error obteniendo llamado: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/personas', methods=['GET', 'POST'])
@login_required
def api_personas():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            persona = Persona(
                apellido=data['apellido'].upper(),
                nombre=data['nombre'].upper(),
                dni=data.get('dni', ''),
                telefono=data.get('telefono', ''),
                celular=data.get('celular', ''),
                direccion=data.get('direccion', '').upper(),
                barrio=data.get('barrio', ''),
                observaciones=data.get('observaciones', '')
            )
            
            db.session.add(persona)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'persona_id': persona.id,
                'message': f'Persona #{persona.id} registrada exitosamente'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error creando persona: {e}")
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            personas = Persona.query.filter_by(activo=True).order_by(Persona.apellido).limit(100).all()
            
            return jsonify({
                'success': True,
                'personas': [{
                    'id': p.id,
                    'apellido': p.apellido,
                    'nombre': p.nombre,
                    'dni': p.dni,
                    'telefono': p.telefono,
                    'celular': p.celular,
                    'direccion': p.direccion,
                    'barrio': p.barrio,
                    'observaciones': p.observaciones
                } for p in personas]
            })
        except Exception as e:
            print(f"Error obteniendo personas: {e}")
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/personas/buscar')
@login_required
def api_buscar_persona():
    try:
        telefono = request.args.get('telefono')
        dni = request.args.get('dni')
        
        persona = None
        
        if telefono:
            persona = Persona.query.filter(
                ((Persona.telefono == telefono) | (Persona.celular == telefono)) &
                (Persona.activo == True)
            ).first()
        elif dni:
            persona = Persona.query.filter_by(dni=dni, activo=True).first()
        
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
                    'direccion': persona.direccion,
                    'barrio': persona.barrio,
                    'observaciones': persona.observaciones
                }
            })
        
        return jsonify({'success': False, 'message': 'Persona no encontrada'})
    except Exception as e:
        print(f"Error buscando persona: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/guardias', methods=['GET', 'POST'])
@login_required
def api_guardias():
    if request.method == 'POST':
        try:
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
                'message': f'Novedad #{guardia.id} registrada exitosamente'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error creando guardia: {e}")
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            guardias = Guardia.query.order_by(Guardia.fecha.desc()).limit(50).all()
            
            return jsonify({
                'success': True,
                'guardias': [{
                    'id': g.id,
                    'fecha': g.fecha.isoformat(),
                    'actividad': g.actividad,
                    'tipo': g.tipo,
                    'usuario_nombre': g.usuario.nombre if g.usuario else 'Desconocido'
                } for g in guardias]
            })
        except Exception as e:
            print(f"Error obteniendo guardias: {e}")
            return jsonify({'success': False, 'message': str(e)})

# =============== CONFIGURACIÓN ===============

@app.route('/api/configuracion', methods=['GET', 'POST'])
@login_required
def api_configuracion():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            for clave, valor in data.items():
                config = Configuracion.query.filter_by(clave=clave).first()
                if config:
                    config.valor = valor
                else:
                    config = Configuracion(clave=clave, valor=valor)
                    db.session.add(config)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Configuración guardada'})
        except Exception as e:
            db.session.rollback()
            print(f"Error guardando configuración: {e}")
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            configs = Configuracion.query.all()
            return jsonify({
                'success': True,
                'configuracion': {c.clave: c.valor for c in configs}
            })
        except Exception as e:
            print(f"Error obteniendo configuración: {e}")
            return jsonify({'success': False, 'message': str(e)})

@app.route('/api/usuarios', methods=['GET', 'POST'])
@login_required
def api_usuarios():
    if current_user.rol != 'admin':
        return jsonify({'success': False, 'message': 'Acceso denegado'})
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Verificar si el username ya existe
            if Usuario.query.filter_by(username=data['username']).first():
                return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'})
            
            usuario = Usuario(
                username=data['username'],
                password_hash=generate_password_hash(data['password']),
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=data.get('email', ''),
                telefono=data.get('telefono', ''),
                rol=data['rol']
            )
            
            db.session.add(usuario)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'usuario_id': usuario.id,
                'message': f'Usuario {data["username"]} creado exitosamente'
            })
        except Exception as e:
            db.session.rollback()
            print(f"Error creando usuario: {e}")
            return jsonify({'success': False, 'message': str(e)})
    
    else:  # GET
        try:
            usuarios = Usuario.query.all()
            return jsonify({
                'success': True,
                'usuarios': [{
                    'id': u.id,
                    'username': u.username,
                    'nombre': u.nombre,
                    'apellido': u.apellido,
                    'email': u.email,
                    'telefono': u.telefono,
                    'rol': u.rol,
                    'activo': u.activo,
                    'ultimo_login': u.ultimo_login.isoformat() if u.ultimo_login else None,
                    'fecha_creacion': u.fecha_creacion.isoformat()
                } for u in usuarios]
            })
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            return jsonify({'success': False, 'message': str(e)})

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

# =============== FUNCIONES AUXILIARES ===============

def init_database():
    """Inicializar base de datos con datos por defecto"""
    with app.app_context():
        try:
            db.create_all()
            
            # Crear admin si no existe
            if not Usuario.query.filter_by(username='admin').first():
                admin = Usuario(
                    username='admin',
                    password_hash=generate_password_hash('123456'),
                    nombre='Administrador',
                    apellido='Sistema',
                    email='admin@villaallende.gov.ar',
                    rol='admin'
                )
                db.session.add(admin)
                
                # Configuración inicial
                configs_iniciales = [
                    ('whatsapp_token', ''),
                    ('whatsapp_uid', ''),
                    ('telefono_demva', ''),
                    ('telefono_cec', ''),
                    ('telefono_telemedicina', ''),
                    ('telefono_bomberos', ''),
                    ('telefono_seguridad', ''),
                    ('telefono_defensa', ''),
                    ('telefono_supervisor', ''),
                    ('logo_sistema', '')
                ]
                
                for clave, valor in configs_iniciales:
                    config = Configuracion(clave=clave, valor=valor)
                    db.session.add(config)
                
                db.session.commit()
                print("✅ Usuario administrador creado (admin/123456)")
                print("✅ Configuración inicial creada")
        except Exception as e:
            print(f"Error inicializando base de datos: {e}")
            raise

if __name__ == '__main__':
    init_database()
    app.run(debug=False, host='0.0.0.0', port=5000)