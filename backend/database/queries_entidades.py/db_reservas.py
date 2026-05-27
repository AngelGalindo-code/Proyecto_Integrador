from flask import flash
from queries import *


def getReservas():

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(SQL_BASE_RESERVAS)
    reservas = cursor.fetchall()

    if not reservas:
        flash('No se encontraron reservas')
        
    cursor.close()
    return reservas 


def getReservaPorId(id_reserva):

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(SQL_GET_POR_ID, (id_reserva,))
    miReserva = cursor.fetchone()

    if not miReserva:
        flash('No se encontró ninguna reserva con ese ID')

    cursor.close()

    return miReserva


def actualizarReserva(nombre, fecha, mesa, cantidad_personas, id_reserva):

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(SQL_GET_POR_ID, (id_reserva,))
    miReserva = cursor.fetchone()

    if miReserva:
        cursor.execute(UPDATE_SQL, (nombre, fecha, mesa, cantidad_personas, id_reserva))
        conexion.commit()
        flash('Reserva actualizada exitosamente')
        reserva = True
    
    else:
        flash('No se ha podido encontrar una reserva con ese ID')
        resultado = False



    cursor.close()
    return resultado

def eliminarReserva(id_reserva):

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(SQL_GET_POR_ID, (id_reserva,))
    miReserva = cursor.fetchone()

    if miReserva:
        cursor.execute(DELETE_SQL, (id_reserva,))
        conexion.commit()
        flash('Reserva eliminada exitosamente')
        resultado = True
    
    else:
        flash('No se ha podido encontrar una reserva con ese ID')
        resultado = False

    cursor.close()
    return resultado


def verDisponibilidadMesa(fecha, mesa, hora):

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(MESA_RESERVADA_SQL, (fecha, mesa, hora))
    reservaExistente = cursor.fetchone()

    if reservaExistente:
        flash(f"La mesa {mesa} ya está reservada para la fecha {fecha} y hora {hora}. Por favor elija otra mesa o una fecha diferente")
        return False
    
    return True
