import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from frontend.constantes import URL_BACKEND

reservas_bp = Blueprint("reservas", __name__)


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