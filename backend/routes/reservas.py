from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for
from validators.db import *

# Se toman funciones de validaciones de un archivo llamado db.py
# Se toma el nombre de templates que validan errores, listas, etc
# Falta la validacion de errores

reservas_bp = Blueprint("reservas", __name__)

# Implementar el uso de sessions


#Crear reserva
@reservas_bp.route('/reservas', methods=['POST'])
def crearReserva():

    try:

        
        form_data = request.form

        
        id_usuario = form_data.get('id_usuario')
        fecha = form_data.get('fecha')
        hora = form_data.get('hora')
        mesa = form_data.get('mesa')
        cantidad_personas = form_data.get(
            'cantidad_personas'
        )

        #Llamar a la función DB

        flash(
            'Reserva creada correctamente',
            'success'
        )

        return redirect(
            url_for(
                'reservas.reservasList'
            )
        )

    except Exception:

        return render_template(
            'errorGenerico.html',
            message='Error al crear reserva'
        )


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

# Copiando el modelo del backend del trabajo del fixture 
@reservas_bp.route('/', methods=['GET'])
def reservasList():

    try:
        reservas = getReservas()
    
    except Exception as e:
        return render_template('sinreservas.html', message='No se Encontraron reservas')

    return render_template('lista.html', title='Reservas', reservas=reservas)

@reservas_bp.route('/<id_reserva>/mireserva', methods=['GET'])
def getReservaPorId(id_reserva):

    try:
        id_reserva = int(id_reserva)

    except ValueError:
        return render_template('errorGenerico.html', message='Error de datos')
    
    miReserva = getReservaPorId(id_reserva)

    if not miReserva:
        return render_template('404_notfound.html', message=f'No se pudo encontrar tu reserva con el id de reserva: {id_reserva}')
    
    return render_template('miReserva.html', title='Mi Reserva', reserva=miReserva)



@reservas_bp.route('/<id_reserva>/modificar', methods=['GET', 'POST'])
def modificarRerserva(id_reserva):

    try:
        id_reserva = int(id)
    except ValueError:
        flash("El ID de la reserva proporcionado no es válido.")
        return redirect(url_for('reservas.reservasList'))

    form_data = request.form

    try:
        modificarReserva(
            id_reserva=id_reserva,
            fecha=form_data.get('fecha'),
            hora=form_data.get('hora'),
            mesa=int(form_data.get('mesa')),
            cantidad_personas=int(form_data.get('cantidad_personas'))
        )
        flash('Reserva modificada correctamente.', 'info')
        
    except ValueError as e:
        # Ver trabajo de fixture
        mensaje_error = e.args[0] if e.args else "Error al modificar la reserva."
        flash(mensaje_error)
        # Por si falla, me manda de nuevo a reservar
        return redirect(url_for('reservasList'))

    return redirect(url_for('reservasList'))


@reservas_bp.route('/reservar', methods=['POST'])
def crearReserva():

    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        fecha = request.form['fecha']
        hora = request.form['hora']
        mesa = request.form['mesa']
        cantidadPersonas = request.form['cantidad']
        preferencia = request.form['preferencia']

        return redirect(url_for('getReservaPorId', id_reserva=id_reserva)) 
    else:
        return render_template('formularioReserva.html')


@reservas_bp.route('/<id_reserva>/eliminar', methods=['DELETE'])
def cancelarReserva():
    try:
        id_reserva = int(id)
    except ValueError:
        flash("El ID de la reserva a eliminar no es válido.", "danger")
        return redirect(url_for('reservas.get_reservas'))

    eliminado = eliminarReservaPorId(id_reserva)

    if not eliminado:
        # En vez de jsonify, mostramos un template de error 404 estructurado
        return render_template('404_notfound.html', mensaje=f"No se encontró la reserva con ID {id_reserva} para ser cancelada.")

    flash('La reserva ha sido cancelada exitosamente.', 'warning')
    
    return redirect(url_for('reservas.get_reservas'))
