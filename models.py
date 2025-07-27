from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# =============== MODELO USUARIO ===============
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    rol = db.Column(db.String(20), nullable=False, default='operador')  # admin, supervisor, operador
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    llamados_atendidos = db.Column(db.Integer, default=0)
    intentos_login = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    llamados = db.relationship('Llamado', backref='usuario', lazy=True)
    guardias = db.relationship('Guardia', backref='usuario', lazy=True)
    observaciones = db.relationship('Observacion', backref='usuario', lazy=True)
    servicios_comisionados = db.relationship('ServicioComisionado', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

# =============== MODELO LLAMADO ===============
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
    tipo = db.Column(db.String(20), nullable=False)  # medica, bomberos, seguridad, defensa, otros
    prioridad = db.Column(db.String(10), nullable=False, default='verde')  # rojo, amarillo, verde
    via_publica = db.Column(db.String(15), nullable=False, default='domicilio')  # domicilio, via_publica
    
    # Estado y seguimiento
    estado = db.Column(db.String(20), nullable=False, default='en_curso')  # en_curso, cerrado
    whatsapp_enviado = db.Column(db.Boolean, default=False)
    movil_en_domicilio = db.Column(db.Boolean, default=False)
    fecha_movil_domicilio = db.Column(db.DateTime, nullable=True)
    fecha_cierre = db.Column(db.DateTime, nullable=True)
    
    # Triage médico (JSON)
    triage_data = db.Column(db.Text, nullable=True)
    
    # Relaciones
    observaciones = db.relationship('Observacion', backref='llamado', lazy=True, cascade='all, delete-orphan')
    servicios_comisionados = db.relationship('ServicioComisionado', backref='llamado', lazy=True, cascade='all, delete-orphan')
    
    @property
    def direccion_completa(self):
        direccion = self.calle
        if self.numero:
            direccion += f" {self.numero}"
        direccion += f", {self.barrio}"
        return direccion
    
    @property
    def solicitante_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def __repr__(self):
        return f'<Llamado #{self.id} - {self.tipo}>'

# =============== MODELO PERSONA (CORREGIDO CON EMAIL) ===============
class Persona(db.Model):
    __tablename__ = 'personas'
    
    id = db.Column(db.Integer, primary_key=True)
    apellido = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    celular = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)  # *** CAMPO AGREGADO ***
    direccion = db.Column(db.String(200), nullable=True)
    barrio = db.Column(db.String(100), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"
    
    def __repr__(self):
        return f'<Persona {self.apellido}, {self.nombre}>'

# =============== MODELO GUARDIA ===============
class Guardia(db.Model):
    __tablename__ = 'guardias'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    actividad = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='operacion')  # sistema, llamado, operacion, whatsapp, procedimiento, mantenimiento, capacitacion, incidente
    
    def __repr__(self):
        return f'<Guardia #{self.id} - {self.tipo}>'

# =============== MODELO OBSERVACION ===============
class Observacion(db.Model):
    __tablename__ = 'observaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    llamado_id = db.Column(db.Integer, db.ForeignKey('llamados.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Observacion #{self.id} - Llamado #{self.llamado_id}>'

# =============== MODELO SERVICIO COMISIONADO ===============
class ServicioComisionado(db.Model):
    __tablename__ = 'servicios_comisionados'
    
    id = db.Column(db.Integer, primary_key=True)
    llamado_id = db.Column(db.Integer, db.ForeignKey('llamados.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo_servicio = db.Column(db.String(20), nullable=False)  # demva, cec, telemedicina, bomberos, seguridad, defensa
    motivo = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente, confirmado
    
    def __repr__(self):
        return f'<ServicioComisionado #{self.id} - {self.tipo_servicio}>'

# =============== MODELO CONFIGURACION ===============
class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=True)
    descripcion = db.Column(db.String(255), nullable=True)
    categoria = db.Column(db.String(50), nullable=True)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracion {self.clave}>'

# =============== BARRIOS PREDEFINIDOS ===============
BARRIOS = [
    'ANTIGUA ESTANCIA', 'BOSQUE ALEGRE', 'CENTRO', 'CHACRAS DE LA VILLA',
    'CONDOR ALTO', 'CONDOR BAJO', 'CUMBRES DE V. A.', 'EL CEIBO',
    'ESPAÑOL', 'INDUSTRIAL', 'JARDIN DE EPICURO', 'LA AMALIA',
    'LA CRUZ', 'LA HERRADURA', 'LA PALOMA', 'LAS LOMITAS',
    'LAS POLINESIAS', 'LAS ROSAS', 'LOMAS ESTE', 'LOMAS OESTE',
    'LOMAS SUR', 'MORADA', 'PAN DE AZUCAR', 'SAN ALFONSO',
    'SAN CLEMENTE', 'SAN ISIDRO', 'SOLARES DE SAN ALFONSO',
    'TERRAZAS DE LA VILLA', 'V. A. GOLF', 'V. A. PARQUE',
    'VILLA BRIZUELA', 'OTROS'
]

# =============== TIPOS DE EMERGENCIA ===============
TIPOS_EMERGENCIA = [
    ('medica', 'Emergencia Médica'),
    ('bomberos', 'Bomberos'),
    ('seguridad', 'Seguridad Ciudadana'),
    ('defensa', 'Defensa Civil'),
    ('otros', 'Otros Servicios')
]

# =============== PRIORIDADES ===============
PRIORIDADES = [
    ('rojo', 'Rojo - Crítico'),
    ('amarillo', 'Amarillo - Urgente'),
    ('verde', 'Verde - No Urgente')
]

# =============== ROLES DE USUARIO ===============
ROLES = [
    ('admin', 'Administrador'),
    ('supervisor', 'Supervisor'),
    ('operador', 'Operador')
]

# =============== TIPOS DE GUARDIA ===============
TIPOS_GUARDIA = [
    ('sistema', 'Sistema'),
    ('llamado', 'Llamado'),
    ('operacion', 'Operación'),
    ('whatsapp', 'WhatsApp'),
    ('procedimiento', 'Procedimiento'),
    ('mantenimiento', 'Mantenimiento'),
    ('capacitacion', 'Capacitación'),
    ('incidente', 'Incidente')
]

# =============== SERVICIOS PARA COMISIONAR ===============
SERVICIOS_COMISIONABLES = [
    ('demva', 'DEMVA'),
    ('cec', 'CEC'),
    ('telemedicina', 'TELEMEDICINA'),
    ('bomberos', 'Bomberos'),
    ('seguridad', 'Seguridad'),
    ('defensa', 'Defensa Civil')
]