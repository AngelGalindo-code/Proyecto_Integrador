from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for, abort, session 
from routes.decorators import adminRequired, loginRequired
from validaciones.reservas import *
import requests 
from constantes import URL_BACKEND
from flask_mail import Message

# Para el QR
import qrcode
import io
import base64

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)


apiBackend = requests.Session()


reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route('/reservar', methods=['GET', 'POST'])
def crearReserva():
    
    id_usuario = session.get('id_usuario')
    if not id_usuario and session.get('usuario'):
        id_usuario = session.get('usuario').get('id') or session.get('usuario').get('id_usuario')

    # Si no hay ningún usuario logueado en ningún lado, no mandamos la petición
    if not id_usuario:
        return render_template('home.html', menu={'comidas': []}, resenas={}, error="Debes iniciar sesión para realizar una reserva.")

    if request.method == 'GET':
        return render_template('home.html', menu={'comidas': []}, resenas={})

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        fecha_hora = request.form.get('fecha_hora', '').strip()  
        mesa = request.form.get('mesa', '').strip()            
        personas = request.form.get('cantidad_personas', '').strip()

        if not all([nombre, fecha_hora, mesa, personas]):
            return render_template('home.html', menu={'comidas': []}, resenas={}, error="Todos los campos son obligatorios")

        try:
            fecha, hora = fecha_hora.split('T')
        except ValueError:
            return render_template('home.html', menu={'comidas': []}, resenas={}, error="Formato de fecha inválido")

        if not validarFecha(fecha):
            datosViejos = {'nombre': nombre, 'fecha_hora': fecha_hora, 'mesa': mesa, 'cantidad_personas': personas}
            return render_template('home.html', valores=datosViejos, menu={'comidas': []}, resenas={}, error="Fecha inválida")

        try:
            payload = {
                'id_usuario': id_usuario, 
                'nombre': nombre,
                'fecha': fecha,
                'hora': hora,
                'mesa': mesa,
                'cantidad_personas': int(personas),
                'estado': 'pendiente'
            }

            respuesta = apiBackend.post(f"{URL_BACKEND}/reservas", json=payload, timeout=5)

            if respuesta.status_code in [200, 201]:
                id_nueva_reserva = respuesta.json().get('id')

                if id_nueva_reserva is not None:
                    flash("¡Reserva creada con éxito!", "success")
                    return redirect(url_for('reservas.reservaExitosa', id_reserva=int(id_nueva_reserva)))
                
                return render_template('home.html', menu={'comidas': []}, resenas={}, error="Error al procesar el identificador de la reserva.")
            
            return render_template('home.html', menu={'comidas': []}, resenas={}, error="El sistema de reservas rechazó la petición.")
                
        except requests.exceptions.RequestException:
            return render_template('home.html', menu={'comidas': []}, resenas={}, error="Error de comunicación con el servicio de reservas")
@reservas_bp.errorhandler(405)
def method_not_allowed(e):

    return render_template('400.html'), 405

@reservas_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500_serverError.html'), 500

@reservas_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404_notFound.html'), 404

@reservas_bp.errorhandler(403)
def acces_forbidden(e):
    return render_template('errors/403_forbidden.html'), 403

@reservas_bp.errorhandler(400)
def bad_request(e):
    return render_template('errors/400_badRequest.html'), 400


        

def obtener_reservas_backend():
    try:
        # Hacemos el pedido al backend
        respuesta = requests.get(f"{URL_BACKEND}/reservas", timeout=5)

        if respuesta.status_code == 200:
            reservas = respuesta.json()

            if reservas:
                return reservas
            else:
                return []
                
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con el backend de reservas: {e}")
        return []

@reservas_bp.route('/<int:id_reserva>/mireserva', methods=['GET'])
@loginRequired
def getReservaPorId(id_reserva):

    id_valido = validarId(id_reserva)
    if not id_valido:
        abort(404)

    esAdmin = session.get('rol') == 'admin' # Se mantiene tu chequeo de rol

    try:
        
        if esAdmin:
            respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        else:
            respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}/mireserva", timeout=5)

        if respuesta.status_code == 400:
            abort(400)
        if respuesta.status_code == 404:
            abort(404)

        if respuesta.status_code == 200:
            miReserva = respuesta.json()
            
            esUsuario = session.get('id_usuario') == miReserva.get('id_usuario')
            
            if not (esUsuario or esAdmin):
                abort(403)
            
   
            url_asistencia = f"http://192.168.1.50:5000/reservas/{id_reserva}/confirmar-asistencia"
            qr.add_data(url_asistencia)
            qr.make(fit=True)
            imagen_qr = qr.make_image(fill_color="black", back_color="white")
            
            buffer_memoria = io.BytesIO()
            imagen_qr.save(buffer_memoria, format="PNG")
            buffer_memoria.seek(0)
            qr_base64 = base64.b64encode(buffer_memoria.read()).decode('utf-8')
            qr.clear() # Limpiamos el objeto QR

            # Le pasamos la reserva de la API y el QR recién horneado a miReserva.html
            flash("Estos son los detalles de su reserva", "success")
            return render_template("miReserva.html", title="Mi reserva", reserva=miReserva, qr_code=qr_base64)
        else:
            abort(500)
    
    except requests.exceptions.RequestException:
        abort(500)




@reservas_bp.route('/<id_reserva>/modificar', methods=['GET', 'POST']) 
@loginRequired
def modificarReserva(id_reserva):

    id_valido = validarId(id_reserva)
    if not id_valido:
        abort(400)

    try:
        if request.method == "POST":
            nombre = request.form.get('nombre', '').strip()
            fecha = request.form.get('fecha', '').strip()  
            hora = request.form.get('hora', '').strip()
            mesa = request.form.get('mesa', '').strip()
            personas = request.form.get('cantidad_personas', '').strip()

            # Conversión de formato de fecha obligatorio ("DD-MM")
            fecha_para_api = fecha
            if '-' in fecha and len(fecha) == 10:
                partes = fecha.split('-')
                fecha_para_api = f"{partes[2]}-{partes[1]}"

            if not validarFecha(fecha):
                reserva_falsa = {
                    'id': id_reserva,
                    'nombre': nombre,
                    'fecha': fecha,
                    'hora': hora,
                    'mesa': mesa,
                    'cantidad_personas': personas
                }
                return render_template("formularioReserva.html", reserva=reserva_falsa)

            # Traemos la reserva real para validar el dueño
            verificada = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
            if verificada.status_code == 404:
                abort(404)
   
            reserva_api = verificada.json()
            esUsuario = session.get('id_usuario') == reserva_api.get('id_usuario')

            # Candado estricto: Solo el dueño modifica
            if not esUsuario:
                abort(403) 
            
            payload = {
                'nombre': nombre,
                'fecha': fecha_para_api,
                'hora': hora,
                'mesa': int(mesa) if mesa.isdigit() else mesa,
                'cantidad_personas': int(personas) if personas.isdigit() else personas,
                'id_usuario': session.get('id_usuario')
            }  
    
            reservaActualizada = apiBackend.put(f"{URL_BACKEND}/reservas/{id_reserva}", json=payload, timeout=5)

            if reservaActualizada.status_code == 200:
                flash("¡Reserva actualizada con éxito!", "success")
                return redirect(url_for("reservas.getReservaPorId", id_reserva=id_reserva))
            else:
                #  Restaurado el abort(500) estándar
                abort(500)

        respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)

        if respuesta.status_code == 404:
            abort(404)

        if respuesta.status_code == 200:
            miReserva = respuesta.json()
            esUsuario = session.get('id_usuario') == miReserva.get('id_usuario')

            # Candado estricto para ver la vista
            if not esUsuario:
                abort(403)

            return render_template("formularioReserva.html", reserva=miReserva)
        else:
            abort(500)

    except requests.exceptions.RequestException as e:
        print(f" Error de conexión: {e}")
        abort(500)

@reservas_bp.route('/<int:id_reserva>/eliminar', methods=['POST', 'GET']) # 🌟 Agregamos GET por si acaso
@loginRequired
def cancelarReserva(id_reserva):
    idValido = validarId(id_reserva)
    if not idValido:
        abort(400)
    
    try:
        verificacion = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        if verificacion.status_code == 404:
            abort(404)
            
        miReserva = verificacion.json()
        
        esUsuario = session.get('id_usuario') == miReserva.get('id_usuario')
        esAdmin = session.get('rol') == 'admin'
        
        if not (esUsuario or esAdmin):
            abort(403) 

        # Si entra por GET (escribiendo la URL o enlace directo), lo manejamos de forma segura:
        if request.method == 'GET':
            # Si es admin, lo mandamos al detalle para que use el botón de cancelar original tipo POST
            return redirect(url_for('reservas.getReservaPorId', id_reserva=id_reserva))

        
        respuesta = apiBackend.delete(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        
        if respuesta.status_code == 200:
            flash('Reserva eliminada correctamente', 'success')
            
            # 🌟 CORREGIDO: Redirección limpia sin usar reservasList
            if esAdmin:
                return redirect('/admin') 
            
            return redirect(url_for('home')) 
        else:
            abort(500)
            
    except requests.exceptions.RequestException:
        abort(500)


@reservas_bp.route('/<int:id_reserva>/confirmar-asistencia', methods=['GET', 'POST'])
@loginRequired
def confirmarAsistenciaQR(id_reserva):
    if session.get('usuario', {}).get('rol') != 'admin' and session.get('rol') != 'admin':
        abort(403) 

    idValido = validarId(id_reserva)
    if not idValido:
        abort(400)

    try:
        if request.method == 'POST':
     
            respuesta_get = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
            
            if respuesta_get.status_code == 200:
                datos_originales = respuesta_get.json()
                
              
                fecha_original = datos_originales.get('fecha', '')
                fecha_para_api = fecha_original
                if '-' in fecha_original and len(fecha_original) == 10:
                    partes = fecha_original.split('-')
                    fecha_para_api = f"{partes[2]}-{partes[1]}"

    
                hora_original = datos_originales.get('hora', '')
                hora_para_api = hora_original
                if hora_original and len(hora_original) == 8 and hora_original.count(':') == 2:
                    hora_para_api = hora_original[:5]

                # 2. 📝 Pisamos el campo 'estado' con el string en minúsculas válido
                payload = {
                    'id_usuario': datos_originales.get('id_usuario'),
                    'nombre': datos_originales.get('nombre'),
                    'fecha': fecha_para_api, 
                    'hora': hora_para_api,
                    'mesa': int(datos_originales.get('mesa')) if str(datos_originales.get('mesa')).isdigit() else datos_originales.get('mesa'),
                    'cantidad_personas': int(datos_originales.get('cantidad_personas')),
                    'estado': 'completada'  # 👈 Cambiado a minúsculas para respetar tu DB
                }
                
                # 3. 🚀 Enviamos la actualización limpia mediante PUT
                respuesta_put = apiBackend.put(f"{URL_BACKEND}/reservas/{id_reserva}", json=payload, timeout=5)

                if respuesta_put.status_code in [200, 204]:
                    flash("Asistencia registrada correctamente", "success")
                    return redirect('/admin')
            
            # Si algo falla en los pasos internos
            flash("El servidor de reservas rechazó la actualización.", "danger")
            return redirect('/admin')

        # Método GET original
        respuesta_get = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        if respuesta_get.status_code == 404:
            abort(404)
            
        datos_reserva = respuesta_get.json()
        return render_template('confirmarAsistencia.html', reserva=datos_reserva)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        flash("Error de conexión al procesar la asistencia.", "danger")
        return redirect('/admin')


@reservas_bp.route('/<int:id_reserva>/exito', methods=['GET'])
def reservaExitosa(id_reserva):

    idValido = validarId(id_reserva)
    if idValido == False:
        abort(400)
    
    try:
        sesion = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)

        if sesion.status_code == 404:
            abort(404)
        
        if sesion.status_code == 200:
            miReserva = sesion.json()
           
            id_sesion = session.get('id_usuario')
            id_reserva_user = miReserva.get('id_usuario')

            if id_sesion is None or id_reserva_user is None or int(id_sesion) != int(id_reserva_user):
                abort(403)

            informacion_qr = (
                f"--- CONFIRMACIÓN DE RESERVA ---\n"
                f"ID de Reserva: {miReserva.get('id')}\n"
                f"Nombre: {miReserva.get('nombre')}\n"
                f"Fecha: {miReserva.get('fecha')}\n"
                f"Hora: {miReserva.get('hora')} hs\n"
                f"Mesa: {miReserva.get('mesa')}\n"
                f"Personas: {miReserva.get('cantidad_personas')} personas"
            )
            
            qr.add_data(informacion_qr)
            qr.make(fit=True)
            imagen_qr = qr.make_image(fill_color="black", back_color="white")
            buffer_memoria = io.BytesIO()
            imagen_qr.save(buffer_memoria, format="PNG")
            buffer_memoria.seek(0)
            qr_base64 = base64.b64encode(buffer_memoria.read()).decode('utf-8')
            qr.clear()

            return render_template('reserva_exito.html', reserva=miReserva, qr_code=qr_base64)
        
        else:
            abort(500)

    except requests.exceptions.RequestException:
        abort(500)

def enviarQrPorMail(destinatario, datos, qr_base64):
    from app import mail  # Para evitar importaciones circulares
    try:
        # 1. Armamos el objeto Message indicando el asunto y el destinatario
        mensaje = Message(
            subject=f"Reserva Nro. #{datos.get('id_reserva') or datos.get('id')} - Los Horneros",
            recipients=[destinatario]
        )

        mensaje.body = f"¡Hola! Tu reserva fue confirmada para la fecha {datos.get('fecha')} a las {datos.get('hora')} hs."
        mensaje.html = render_template('comprobante_email.html', reserva=datos)

        if "," in qr_base64:
            qr_base64 = qr_base64.split(",")[1]

        datosBinarios = base64.b64decode(qr_base64)

        mensaje.attach(
            filename=f"qrreserva{datos.get('id_reserva') or datos.get('id')}.png",
            content_type="image/png",
            data=datosBinarios,
            headers=[['Content-ID', '<codigo_qr>']]
        )

        mail.send(mensaje)
        return True
    except Exception:

        return False