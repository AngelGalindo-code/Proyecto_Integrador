from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for, abort, session 
from constantes import URL_BACKEND
from decorators.decorators import adminRequired, loginRequired

reservas_bp = Blueprint("reservas", __name__)

# Se toma el nombre de templates que validan errores, listas, etc
# Falta la validacion de errores
# Implementar el uso de sessions

# Errores ---> Ver manejo de errores con BluePrint ---> Errores especificos segun la ruta /reservas

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
    return render_template('errors/400_badRequest.html')


@reservas_bp.route("/hacer-reserva", methods=["GET"])
def mostrarFormulario():

    return render_template(
        "formulario-reserva.html",
        subtitulo_reserva = "Reserva Ahora",
        titulo_principal = "Haz una reserva",
        horario ="Martes a Domingos de 8:00h a 23:00h",
        direccion = "Calle Pepito 123, Buenos Aires")

@reservas_bp.route("/reservas", methods=["POST"])
def crearReserva():

    if not request.form:
        flash("Sin informacion en el formulario", "danger")
        return redirect(url_for("reservas.mostrarFormulario")), 400
    
    try:    
        from_data = request.form

        id_usuario = session.get("id_usuario")
        cantidad_personas = from_data.get("cantidad_personas")
        mesa = from_data.get("mesa")

        input_fecha_hora = from_data.get("fecha_hora")
        if input_fecha_hora and "T" in input_fecha_hora:
            fecha, hora = input_fecha_hora.split("T")
        
        else:
            fecha, hora = None, None

        if not all([id_usuario, fecha, hora, mesa, cantidad_personas]):
            flash("Faltan datos", "danger")
            return redirect(url_for("reservas.mostrarFormulario")), 400
        
        payload = {
            "id_usuario": id_usuario,
            "fecha": fecha,
            "hora": hora,
            "mesa": mesa,
            "cantidad_personas": cantidad_personas
        }

        respuesta = requests.post(f"{URL_BACKEND}/reservas", json=payload)

        if respuesta.status_code == 201:
            flash("Reserva hecha", "success")
            return redirect(url_for("reservas.mostrarFormulario"))
        
        if respuesta.status_code == 409:
            flash("Mesa ya reservada para esa fecha y hora", "warning")
            return redirect(url_for("reservas.mostrarFormulario"))
        
        flash("No se pudo crear la reserva", "danger")
        return redirect(url_for("reservas.mostrarFormulario"))
    
    except Exception as e:
        print(f"error en la conexion: {e}")
        flash("No pudimos procesar tu reserva, intente otra vez")
        return redirect(url_for("reservas.mostrarFormulario")), 500

#Ver reservas admin
@reservas_bp.route('/admin/reservas', methods=['GET'])
def adminReservas():

    try:
        reservas = getReservas()
        
        if not reservas:

            return render_template(
                'sinreservas.html',
                message='No existen reservas'
            )

        return render_template(
            'adminReservas.html',
            title='Reservas',
            reservas=reservas
        )

    except Exception:

        return render_template(
            'errorGenerico.html',
            message='Error al obtener reservas'
        )

@reservas_bp.route('/admin', methods=['GET'])
@adminRequired
def reservasList():

    reservas = getReservas()

    if not reservas:
        return render_template('listaVacia.html')
   
    return render_template('lista.html', title='Reservas', reservas=reservas)


@reservas_bp.route('/<int:id_reserva>/mireserva', methods=['GET'])
@loginRequired
def getReservaPorId(id_reserva):

    id_valido = validarId(id_reserva)

    if not id_valido:
        abort(404)

    miReserva = obtenerReservaPorId(id_reserva)
    
    if not miReserva:
        abort(404)

    if session.get('id_usuario') != miReserva.get('id_usuario'):
        abort(403)
    
    return render_template('miReserva.html', title='Mi reserva', reserva=miReserva)




@reservas_bp.route('/<id_reserva>/modificar', methods=['GET', 'POST']) 
def modificarRerserva(id_reserva):

    id_valido = validarId(id_reserva)
    if not id_valido:
        return render_template('errors/404_notFound.html')
    
    if request.method == 'POST':

        actualizada = actualizarReserva(
            nombre = request.form.get('nombre'),
            fecha = request.form.get('fecha'),
            mesa = request.form.get('mesa'),
            cantidad_personas = request.form.get('cantidad_personas'),
            id_reserva = id_reserva
        )

        if actualizada:
            return redirect(url_for('.getReservaPorId', id_reserva=id_reserva))
    
        else:
            return render_template('errors/404_notFound.html')
    
    miReserva = getReservaPorId(id_reserva)

    if not miReserva:
        return render_template('errors/404_notFound.html')
    
    return render_template('formularioReserva.html', reserva=miReserva)



@reservas_bp.route('/<id_reserva>/eliminar', methods=['POST'])
@loginRequired
def cancelarReserva(id_reserva):
    idValido = validarId(id_reserva)

    if idValido == False:
        abort(400)
    
    miReserva = obtenerReservaPorId(id_reserva)
    if not miReserva:
        abort(404)

    if session.get('id_usuario') != miReserva.get('id_usuario'):
        abort(403)

    eliminado = eliminarReserva(id_reserva)
        
    return redirect(url_for('reservas.crearReserva'))
