from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for, abort, session 
from routes.decorators import adminRequired, loginRequired
from validaciones.reservas import *
import requests 
from constantes import URL_BACKEND

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
            
            if not reservas:
                flash("No se encontraron reservas")
                return render_template("listaVacia.html")
            
            flash("Aca se encuentra el listado de todas las reservas")
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
            if session.get('id_usuario') != miReserva.get('id_usuario'):
                abort(403)
            
            flash("Estos son los detalles de su reserva", "success")
            return render_template("miReserva.html", title="Mi reserva", reserva=miReserva)
        
        else:
            abort(500)
    
    except requests.exceptions.RequestException:
        abort(500)
            
            




@reservas_bp.route('/<id_reserva>/modificar', methods=['GET', 'POST']) 
@loginRequired
def modificarRerserva(id_reserva):

    id_valido = validarId(id_reserva)

    if not id_valido:
        abort(400)

    try:
        if request.method == "POST":
                verificada = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
                
                if verificada.status_code == 404:
                    abort(404)
   
                reserva = verificada.json()

                if session.get('id_usuario') != reserva.get('id_usuario'):
                    abort(403)
                
                payload = {
                    'nombre' : request.form.get('nombre', '').strip(),
                    'fecha' : request.form.get('fecha', '').strip(),
                    'mesa' : request.form.get('mesa').strip(),
                    'cantidad_personas' : request.form.get('cantidad_personas', '').strip()
                }  
        
                reservaActualizada = apiBackend.put(f"{URL_BACKEND}/reservas/{id_reserva}/modificar", json=payload, timeout=5)

                if reservaActualizada.status_code == 200:
                    flash("Reserva actualizada con exito", "success")
                    return redirect(url_for(".getReservaPorId", id_reserva=id_reserva))
        
                else:
                    abort(500)

        
        respuesta = apiBackend.get(f"{URL_BACKEND}/reservas/{id_reserva}/modificar", timeout=5)

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
        if session.get('id_usuario') != miReserva.get('id_usuario'):
            abort(403) 

        respuesta = apiBackend.delete(f"{URL_BACKEND}/reservas/{id_reserva}", timeout=5)
        
        if respuesta.status_code == 200:
            flash('Reserva eliminada correctamente', 'success')
            return redirect(url_for('home')) 
        else:
            abort(500)
            
    except requests.exceptions.RequestException:
        abort(500)



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

# Ver Flask-email para el envio del qr, o que solo que en la vista.