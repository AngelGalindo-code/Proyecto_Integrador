from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for
from database.validators.db_mysql import *
from validaciones.reservas import *



# Se toman funciones de validaciones de un archivo llamado db_sqlalchemy.py
# Se toma el nombre de templates que validan errores, listas, etc
# Falta la validacion de errores

reservas_bp = Blueprint("reservas", __name__)

# Implementar el uso de sessions


# Errores ---> Ver manejo de errores con BluePrint ---> Errores especificos segun la ruta /reservas
@reservas_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404_notFound.html'), 404

@reservas_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('500_serverError.html'), 500



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
# Aun se encuentra incompleto. Ver implementacion del try-except
@reservas_bp.route('/', methods=['GET'])
def reservasList():

    reservas = getReservas()

    if not reservas:
        flash('No hay reservas!')

        return render_template('templates/errors/sinreservas.html', title='Error')
    
    else:
        flash('Aca se encuentra la lista de todas las reservas')

        return render_template('templates/lista.html', title='Reservas')


@reservas_bp.route('/<id_reserva>/mireserva', methods=['GET'])
def getReservaPorId(id_reserva):

    id_valido = validarId(id_reserva)

    if not id_valido:
        return render_template('errors/404_notFound.html')

    miReserva = getReservaPorId(id_reserva) # Ver implementacion del try-except y validacion de id

    if not miReserva:
        flash('No hay reservas con ese ID')

        return render_template('errors/404_notFound.html')
    
    return render_template('miReserva.html', title='Mi reserva')




@reservas_bp.route('/<id_reserva>/modificar', meethods=['GET', 'POST']) 
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
    
    return render_template('formularioReserva.html')



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

    eliminado = eliminarReserva(id_reserva)

    if not eliminado:
        # En vez de jsonify, mostramos un template de error 404 estructurado
        return render_template('404_notfound.html', mensaje=f"No se encontró la reserva con ID {id_reserva} para ser cancelada.")

    flash('La reserva ha sido cancelada exitosamente.') # Ver que ya esta contemplado en eliminarReserva
    
    return redirect(url_for('reservas.get_reservas'))
