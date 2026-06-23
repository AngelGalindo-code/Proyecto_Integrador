from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for, abort, session 
from routes.decorators import adminRequired, loginRequired
from validaciones.reservas import *
import requests 
from constantes import URL_BACKEND
from flask_mail import Message
# from app import mail ---> Se importa en la duncion de mail 

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
        return render_template('home.html', menu={'comidas': []}, error="Debes iniciar sesión para realizar una reserva.")

    if request.method == 'GET':
        return render_template('home.html', menu={'comidas': []})

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        fecha_hora = request.form.get('fecha_hora', '').strip()  
        mesa = request.form.get('mesa', '').strip()            
        personas = request.form.get('cantidad_personas', '').strip()

        if not all([nombre, fecha_hora, mesa, personas]):
            return render_template('home.html', menu={'comidas': []}, error="Todos los campos son obligatorios")

        try:
            fecha, hora = fecha_hora.split('T')
        except ValueError:
            return render_template('home.html', menu={'comidas': []}, error="Formato de fecha inválido")

        if not validarFecha(fecha):
            datosViejos = {'nombre': nombre, 'fecha_hora': fecha_hora, 'mesa': mesa, 'cantidad_personas': personas}
            return render_template('home.html', valores=datosViejos, menu={'comidas': []}, error="Fecha inválida")

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
                
                return render_template('home.html', menu={'comidas': []}, error="Error al procesar el identificador de la reserva.")
            
            return render_template('home.html', menu={'comidas': []}, error="El sistema de reservas rechazó la petición.")
                
        except requests.exceptions.RequestException:
            return render_template('home.html', menu={'comidas': []}, error="Error de comunicación con el servicio de reservas")
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



@reservas_bp.route('/reservar', methods=['GET', 'POST'])
@loginRequired
def crearReserva():
    if request.method == 'GET':
        return render_template('reservas/formularioCrearReserva.html')

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        fecha = request.form.get('fecha', '').strip()
        hora = request.form.get('hora', '').strip()
        personas = request.form.get('cantidad_personas', '').strip()

        if not all([nombre, fecha, hora, personas]):
            abort(400)

        if not validarFecha(fecha):

            datosViejos = {
                'nombre': nombre,
                'fecha': fecha,
                'hora': hora,
                'cantidad_personas': personas
            }

            return render_template('reservas/formularioCrearReserva.html', valores=datosViejos)

        try:
            payload = {
                'id_usuario': session.get('id_usuario'),
                'nombre': nombre,
                'fecha': fecha,
                'hora': hora,
                'cantidad_personas': int(personas),
                'estado': 'pendiente'
            }

            respuesta = apiBackend.post(f"{URL_BACKEND}/reservas", json=payload, timeout=5)

            if respuesta.status_code in [200, 201]:
                reserva_creada = respuesta.json()
                id_nueva_reserva = reserva_creada.get('id')
                
                flash("¡Reserva creada con éxito!", "success")
                return redirect(url_for('reservas.reservaExitosa', id_reserva=id_nueva_reserva))
            else:
                abort(500)

        except requests.exceptions.RequestException:
            abort(500)

@reservas_bp.route('/admin', methods=['GET'])
@adminRequired
def reservasList():

    try:
        respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/admin", timeout=5)

        if respuesta.status_code == 404:
            abort(404)
        
        if respuesta.status_code == 403:
            abort(403)

        if respuesta.status_code == 400:
            abort(400)

        if respuesta.status_code == 200:
            reservas = respuesta.json()
            
            return render_template("listas.html", reservas=reservas)
        
        else:
            abort(500)
        
    except requests.exceptions.RequestException:
        abort(500)
        

@reservas_bp.route('/<int:id_reserva>/mireserva', methods=['GET'])
@loginRequired
def getReservaPorId(id_reserva):

    id_valido = validarId(id_reserva)
    if not id_valido:
        abort(404)

    try:
        respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}/mireserva", timeout=5)

        if respuesta.status_code == 400:
            abort(400)
        if respuesta.status_code == 404:
            abort(404)

        if respuesta.status_code == 200:
            miReserva = respuesta.json()
            
            esUsuario = session.get('id_usuario') == miReserva.get('id_usuario')
            esAdmin = session.get('rol') == 'admin' # Ajustalo según cómo manejes los roles
            
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

            # Tambien le agrega el qr a la vista del cliente
            return render_template("miReserva.html", title="Mi reserva", reserva=miReserva, qr_code=qr_base64)
        else:
            abort(500)
    
    except requests.exceptions.RequestException:
        abort(500)
            
# El CSS utiliza el de crear Reserva de manera global, por lo que no necesita un Css aparte
@reservas_bp.route('/<id_reserva>/modificar', methods=['GET', 'POST']) 
@loginRequired
def modificarRerserva(id_reserva):

    id_valido = validarId(id_reserva)
    if not id_valido:
        abort(400)

    try:
        if request.method == "POST":
            nombre = request.form.get('nombre', '').strip()
            fecha = request.form.get('fecha', '').strip()
            mesa = request.form.get('mesa', '').strip()
            personas = request.form.get('cantidad_personas', '').strip()

            if not validarFecha(fecha):
                reserva_falsa = {
                    'id': id_reserva,
                    'nombre': nombre,
                    'fecha': fecha,
                    'mesa': mesa,
                    'cantidad_personas': personas
                }
                return render_template("modificarReserva.html", reserva=reserva_falsa)

            verificada = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
            if verificada.status_code == 404:
                abort(404)
   
            reserva_api = verificada.json()
            esAdmin = session.get('rol') == 'admin'
            esUsuario = session.get('id_usuario') == reserva_api.get('id_usuario')

            if not (esUsuario or esAdmin):
                abort(403) 
            
            payload = {
                'nombre': nombre,
                'fecha': fecha,
                'mesa': mesa,
                'cantidad_personas': int(personas) 
            }  
    
            reservaActualizada = apiBackend.put(f"{URL_BACKEND}/reservas/{id_reserva}/modificar", json=payload, timeout=5)

            if reservaActualizada.status_code == 200:
                flash("¡Reserva actualizada con éxito!", "success")
                return redirect(url_for("reservas.getReservaPorId", id_reserva=id_reserva))
            else:
                abort(500)

        respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)

        if respuesta.status_code == 404:
            abort(404)

        if respuesta.status_code == 200:
            miReserva = respuesta.json()

            if session.get('id_usuario') != miReserva.get('id_usuario'):
                abort(403)

            return render_template("modificarReserva.html", reserva=miReserva)
        else:
            abort(500)

    except requests.exceptions.RequestException:
        abort(500)

@reservas_bp.route('/<int:id_reserva>/eliminar', methods=['POST'])
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
        
        # Como en modificar para que el admin tambien pueda cancelar reservas
        esUsuario = session.get('id_usuario') == miReserva.get('id_usuario')
        esAdmin = session.get('rol') == 'admin'
        
        if not (esUsuario or esAdmin):
            abort(403) 

        # Si pasa la seguridad, le pegamos al DELETE del backend
        respuesta = apiBackend.delete(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        
        if respuesta.status_code == 200:
            flash('Reserva eliminada correctamente', 'success')
            
            if esAdmin:
                return redirect(url_for('reservas.reservasList'))
            
            return redirect(url_for('home')) 
        else:
            abort(500)
            
    except requests.exceptions.RequestException:
        abort(500)

@reservas_bp.route('/<int:id_reserva>/confirmar-asistencia', methods=['GET', 'POST'])
@loginRequired
def confirmarAsistenciaQR(id_reserva):

    if session.get('rol') != 'admin':
        abort(403) 

    idValido = validarId(id_reserva)
    if not idValido:
        abort(400)

    try:
        if request.method == 'POST':
            payload = {'estado': 'completada'}
            respuesta = apiBackend.put(f"{URL_BACKEND}/reservas/{id_reserva}", json=payload, timeout=5)

            if respuesta.status_code == 200:
                flash("Asistencia registrada correctamente", "success")
                return render_template('asistenciaExitosa.html', id_reserva=id_reserva)
            elif respuesta.status_code == 404:
                abort(404)
            else:
                abort(500)

        respuesta_get = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        if respuesta_get.status_code == 404:
            abort(404)
            
        datos_reserva = respuesta_get.json()
        
        return render_template('confirmarAsistencia.html', reserva=datos_reserva)

    except requests.exceptions.RequestException:
        abort(500)


# Enviar el qr por mail
# Funcion auxiliar --> Modularizarla o dejarla en este archivo
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
            filename=f"qr_reserva_{datos.get('id_reserva') or datos.get('id')}.png",
            content_type="image/png",
            data=datosBinarios,
            headers=[['Content-ID', '<codigo_qr>']]
        )

        mail.send(mensaje)
        return True
    except Exception:

        return False


@reservas_bp.route('/<int:id_reserva>/exito', methods=['GET', 'POST'])
@loginRequired
def reservaExitosa(id_reserva):
    idValido = validarId(id_reserva)
    if not idValido:
        abort(400)
    
    try:
        sesion = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)

        if sesion.status_code == 404:
            abort(404)
        if sesion.status_code != 200:
            abort(500)
            
        miReserva = sesion.json()

        if session.get('id_usuario') != miReserva.get('id_usuario'):
            abort(403)

        url_asistencia = f"http://192.168.1.50:5000/reservas/{id_reserva}/confirmar-asistencia" # Cambiar Ips
        qr.add_data(url_asistencia)
        qr.make(fit=True)
        imagen_qr = qr.make_image(fill_color="black", back_color="white")
        
        buffer_memoria = io.BytesIO()
        imagen_qr.save(buffer_memoria, format="PNG")
        buffer_memoria.seek(0)
        qr_base64 = base64.b64encode(buffer_memoria.read()).decode('utf-8')
        qr.clear()

        # A partir de aca, cuando ya apreto el boton de enviar mail
        if request.method == 'POST':

            correoUsuario = session.get('email') or miReserva.get('email_usuario') or "loshorneros@gmail.com"
            
            datos_reserva = {
                'id': id_reserva,
                'nombre': miReserva.get('nombre'),
                'fecha': miReserva.get('fecha'),
                'hora': miReserva.get('hora'),
                'mesa': miReserva.get('mesa'), 
                'personas': miReserva.get('cantidad_personas')
            }

            enviado = enviarQrPorMail(correoUsuario, datos_reserva, qr_base64)
            
            if enviado:
                flash("¡Comprobante enviado con éxito a tu casilla de correo!", "success")
            else:
                flash("Tu reserva está segura, pero hubo un problema técnico al enviar el correo.", "error")
            
            return redirect(url_for('reservas.reservaExitosa', id_reserva=id_reserva))

        return render_template('reserva_exito.html', reserva=miReserva, qr_code=qr_base64)

    except requests.exceptions.RequestException:
        abort(500)