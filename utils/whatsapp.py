#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Integración WhatsApp con Waboxapp

Funcionalidades:
- Envío automático de mensajes por tipo de emergencia
- Ruteo inteligente según prioridad y ubicación
- Múltiples destinatarios configurables
- Mensajes estructurados con toda la información
"""

import requests
import json
import logging
from datetime import datetime

class WhatsAppManager:
    def __init__(self):
        self.base_url = "https://www.waboxapp.com/api/send/chat"
        self.token = None
        self.uid = None
        self.logger = logging.getLogger(__name__)
        
        # Cargar configuración
        self._load_config()
    
    def _load_config(self):
        """Cargar configuración desde base de datos"""
        try:
            # Intentar cargar desde configuración si está disponible
            from models import Configuracion
            
            token_config = Configuracion.query.filter_by(clave='whatsapp_token').first()
            uid_config = Configuracion.query.filter_by(clave='whatsapp_uid').first()
            
            if token_config:
                self.token = token_config.valor
            if uid_config:
                self.uid = uid_config.valor
                
        except Exception as e:
            self.logger.warning(f"No se pudo cargar configuración WhatsApp: {e}")
    
    def configure(self, token, uid):
        """Configurar credenciales de WhatsApp"""
        self.token = token
        self.uid = uid
        
        # Guardar en base de datos si es posible
        try:
            from models import Configuracion, db
            
            # Actualizar o crear token
            token_config = Configuracion.query.filter_by(clave='whatsapp_token').first()
            if token_config:
                token_config.valor = token
            else:
                token_config = Configuracion(clave='whatsapp_token', valor=token)
                db.session.add(token_config)
            
            # Actualizar o crear UID
            uid_config = Configuracion.query.filter_by(clave='whatsapp_uid').first()
            if uid_config:
                uid_config.valor = uid
            else:
                uid_config = Configuracion(clave='whatsapp_uid', valor=uid)
                db.session.add(uid_config)
            
            db.session.commit()
            self.logger.info("Configuración WhatsApp guardada")
            
        except Exception as e:
            self.logger.warning(f"No se pudo guardar configuración: {e}")
    
    def is_configured(self):
        """Verificar si WhatsApp está configurado"""
        return bool(self.token and self.uid)
    
    def test_connection(self):
        """Probar conexión con WhatsApp"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WhatsApp no configurado'
            }
        
        try:
            # Enviar mensaje de prueba al mismo número
            test_message = f"🧪 Prueba de conexión - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            result = self.send_message(self.uid, test_message)
            
            return {
                'success': result,
                'message': 'Mensaje de prueba enviado' if result else 'Error enviando mensaje de prueba'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_message(self, phone, message):
        """Enviar mensaje de WhatsApp"""
        if not self.is_configured():
            self.logger.error("WhatsApp no configurado")
            return False
        
        try:
            # Limpiar número de teléfono
            phone = self._clean_phone_number(phone)
            
            # Preparar datos para la API
            data = {
                'token': self.token,
                'uid': self.uid,
                'to': phone,
                'custom_uid': f'emergency_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'text': message
            }
            
            # Enviar request
            response = requests.post(self.base_url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('sent', False):
                self.logger.info(f"WhatsApp enviado a {phone}")
                return True
            else:
                self.logger.error(f"Error enviando WhatsApp: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión WhatsApp: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error enviando WhatsApp: {e}")
            return False
    
    def crear_mensaje_llamado(self, llamado):
        """Crear mensaje estructurado para un llamado"""
        # Mapear tipos de emergencia
        tipos_emoji = {
            'medica': '🏥',
            'bomberos': '🚒',
            'seguridad': '🚔',
            'defensa': '🌪️',
            'otros': '📞'
        }
        
        # Mapear prioridades
        prioridades_emoji = {
            'rojo': '🔴',
            'amarillo': '🟡',
            'verde': '🟢'
        }
        
        emoji_tipo = tipos_emoji.get(llamado.tipo, '📞')
        emoji_prioridad = prioridades_emoji.get(llamado.prioridad, '🟢')
        
        # Crear mensaje
        mensaje = f"""🚨 EMERGENCIA VILLA ALLENDE

{emoji_tipo} TIPO: {llamado.tipo.upper()}
{emoji_prioridad} PRIORIDAD: {llamado.prioridad.upper()}

👤 SOLICITANTE:
{llamado.nombre} {llamado.apellido}
📞 {llamado.telefono}

📍 UBICACIÓN:
{llamado.direccion_completa}
{"🏠" if llamado.via_publica == "domicilio" else "🛣️"} {llamado.via_publica.replace("_", " ").title()}

📝 OBSERVACIONES:
{llamado.observaciones_iniciales or "Sin observaciones"}

⏰ HORA: {llamado.fecha.strftime("%d/%m/%Y %H:%M")}
🆔 LLAMADO: #{llamado.id}
👨‍💼 OPERADOR: {llamado.usuario.nombre}"""

        # Agregar información de triage si es médica
        if llamado.tipo == 'medica' and llamado.triage_data:
            try:
                triage = json.loads(llamado.triage_data)
                if any(triage.values()):
                    mensaje += "\n\n🩺 TRIAGE:"
                    if triage.get('consciente') == False:
                        mensaje += "\n⚠️ NO CONSCIENTE"
                    if triage.get('respira') == False:
                        mensaje += "\n⚠️ NO RESPIRA"
                    if triage.get('sangrado'):
                        mensaje += "\n🩸 SANGRADO ABUNDANTE"
                    if triage.get('patologia'):
                        mensaje += "\n⚕️ PATOLOGÍA GRAVE"
                    if triage.get('discapacidad'):
                        mensaje += "\n♿ DISCAPACIDAD"
            except:
                pass
        
        return mensaje
    
    def obtener_destinatarios(self, llamado):
        """Obtener lista de destinatarios según tipo y prioridad"""
        destinatarios = []
        
        try:
            from models import Configuracion
            
            # Siempre incluir supervisor si está configurado
            supervisor = Configuracion.query.filter_by(clave='telefono_supervisor').first()
            if supervisor and supervisor.valor:
                destinatarios.append(supervisor.valor)
            
            # Destinatarios específicos según tipo y contexto
            if llamado.tipo == 'medica':
                if llamado.via_publica == 'domicilio':
                    if llamado.prioridad in ['rojo', 'amarillo']:
                        # DEMVA para emergencias rojas/amarillas en domicilio
                        demva = Configuracion.query.filter_by(clave='telefono_demva').first()
                        if demva and demva.valor:
                            destinatarios.append(demva.valor)
                    else:
                        # TELEMEDICINA para verdes en domicilio
                        telemedicina = Configuracion.query.filter_by(clave='telefono_telemedicina').first()
                        if telemedicina and telemedicina.valor:
                            destinatarios.append(telemedicina.valor)
                else:
                    # CEC para todas las emergencias en vía pública
                    cec = Configuracion.query.filter_by(clave='telefono_cec').first()
                    if cec and cec.valor:
                        destinatarios.append(cec.valor)
            
            elif llamado.tipo == 'bomberos':
                bomberos = Configuracion.query.filter_by(clave='telefono_bomberos').first()
                if bomberos and bomberos.valor:
                    destinatarios.append(bomberos.valor)
            
            elif llamado.tipo == 'seguridad':
                seguridad = Configuracion.query.filter_by(clave='telefono_seguridad').first()
                if seguridad and seguridad.valor:
                    destinatarios.append(seguridad.valor)
            
            elif llamado.tipo == 'defensa':
                defensa = Configuracion.query.filter_by(clave='telefono_defensa').first()
                if defensa and defensa.valor:
                    destinatarios.append(defensa.valor)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo destinatarios: {e}")
        
        # Eliminar duplicados manteniendo orden
        destinatarios_unicos = []
        for dest in destinatarios:
            if dest not in destinatarios_unicos:
                destinatarios_unicos.append(dest)
        
        return destinatarios_unicos
    
    def enviar_notificacion_llamado(self, llamado):
        """Enviar notificación completa de un llamado"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WhatsApp no configurado'
            }
        
        try:
            # Crear mensaje
            mensaje = self.crear_mensaje_llamado(llamado)
            
            # Obtener destinatarios
            destinatarios = self.obtener_destinatarios(llamado)
            
            if not destinatarios:
                return {
                    'success': False,
                    'error': 'No hay destinatarios configurados'
                }
            
            # Enviar a todos los destinatarios
            enviados = 0
            errores = []
            
            for destinatario in destinatarios:
                if self.send_message(destinatario, mensaje):
                    enviados += 1
                else:
                    errores.append(destinatario)
            
            return {
                'success': enviados > 0,
                'enviados': enviados,
                'total_destinatarios': len(destinatarios),
                'errores': errores,
                'destinatarios': destinatarios
            }
            
        except Exception as e:
            self.logger.error(f"Error enviando notificación: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def enviar_mensaje_manual(self, telefono, mensaje, tipo='manual'):
        """Enviar mensaje manual"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WhatsApp no configurado'
            }
        
        try:
            # Preparar mensaje con formato
            mensaje_formateado = f"""📱 MENSAJE MANUAL - VILLA ALLENDE

{mensaje}

⏰ {datetime.now().strftime("%d/%m/%Y %H:%M")}
📨 Tipo: {tipo.upper()}"""
            
            success = self.send_message(telefono, mensaje_formateado)
            
            return {
                'success': success,
                'message': 'Mensaje enviado correctamente' if success else 'Error enviando mensaje'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_phone_number(self, phone):
        """Limpiar y formatear número de teléfono"""
        if not phone:
            return ""
        
        # Eliminar caracteres no numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Agregar código de país argentino si no está presente
        if len(clean_phone) == 10:  # Número nacional
            clean_phone = "54" + clean_phone
        elif len(clean_phone) == 11 and clean_phone.startswith("0"):
            clean_phone = "54" + clean_phone[1:]
        elif len(clean_phone) == 13 and clean_phone.startswith("549"):
            # Ya tiene código de país con 9
            pass
        elif len(clean_phone) == 12 and clean_phone.startswith("54"):
            # Agregar 9 después del código de país
            clean_phone = clean_phone[:2] + "9" + clean_phone[2:]
        
        return clean_phone
    
    def get_status(self):
        """Obtener estado de la configuración WhatsApp"""
        status = {
            'configured': self.is_configured(),
            'token_set': bool(self.token),
            'uid_set': bool(self.uid)
        }
        
        if self.is_configured():
            # Obtener configuración de destinatarios
            try:
                from models import Configuracion
                
                destinatarios_config = [
                    'telefono_supervisor',
                    'telefono_demva',
                    'telefono_cec',
                    'telefono_telemedicina',
                    'telefono_bomberos',
                    'telefono_seguridad',
                    'telefono_defensa'
                ]
                
                destinatarios = {}
                for config_key in destinatarios_config:
                    config = Configuracion.query.filter_by(clave=config_key).first()
                    destinatarios[config_key] = bool(config and config.valor)
                
                status['destinatarios'] = destinatarios
                
            except Exception as e:
                self.logger.warning(f"Error obteniendo estado de destinatarios: {e}")
        
        return status

# Script principal para pruebas
if __name__ == '__main__':
    import sys
    
    wp_manager = WhatsAppManager()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == 'test' and len(sys.argv) > 3:
            token = sys.argv[2]
            uid = sys.argv[3]
            
            wp_manager.configure(token, uid)
            result = wp_manager.test_connection()
            
            if result['success']:
                print("✅ Conexión WhatsApp exitosa")
            else:
                print(f"❌ Error: {result['error']}")
        
        elif action == 'status':
            status = wp_manager.get_status()
            print(f"📱 WhatsApp configurado: {status['configured']}")
            print(f"🔑 Token configurado: {status['token_set']}")
            print(f"📞 UID configurado: {status['uid_set']}")
        
        else:
            print("Uso: python whatsapp.py [test <token> <uid>|status]")
    else:
        print("Uso: python whatsapp.py [test <token> <uid>|status]")
