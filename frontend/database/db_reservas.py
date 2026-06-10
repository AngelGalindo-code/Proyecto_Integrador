from flask import flash
from .queries import *
from .conexion import get_connection

# Las validaciones las hago aca mismo
def getReservas():

    conexion = get_connection()
    reservas = []

    with conexion.cursor() as cursor:
        cursor.execute(SQL_BASE_RESERVAS)
        reservas = cursor.fetchall()

    conexion.close()

    return reservas
    

def obtenerReservaPorId(id_reserva):

    conexion = get_connection()

    with conexion.cursor() as cursor:
        cursor.execute(SQL_GET_POR_ID, (id_reserva,))
        miReserva = cursor.fetchone()

        if not miReserva:
            flash('No se encontró ninguna reserva con ese ID', 'error')

    conexion.close()

    return miReserva



def actualizarReserva(nombre, fecha, mesa, cantidad_personas, id_reserva):

    conexion = get_connection()
    resultado = False

    with conexion.cursor() as cursor:
        cursor.execute(SQL_GET_POR_ID, (id_reserva,))
        miReserva = cursor.fetchone()

        if miReserva:
            cursor.execute(UPDATE_SQL, (nombre, fecha, mesa, cantidad_personas, id_reserva))
            conexion.commit() 
            flash('Reserva actualizada exitosamente', 'exito')
            resultado = True 
        else:
            flash('No se ha podido encontrar una reserva con ese ID', 'error')
            resultado = False

    conexion.close()

    return resultado

def eliminarReserva(id_reserva):

    conexion = get_connection()
    resultado = False

    with conexion.cursor() as cursor:
        cursor.execute(SQL_GET_POR_ID, (id_reserva,))
        miReserva = cursor.fetchone()

        if miReserva:
            cursor.execute(DELETE_SQL, (id_reserva,))
            conexion.commit()
            flash('Reserva eliminada exitosamente', 'success')
            resultado = True
        else:
            flash('No se ha podido encontrar una reserva con ese ID', 'error')
            resultado = False

    conexion.close()

    return resultado


def verDisponibilidadMesa(fecha, mesa, hora):

    conexion = get_connection()
    disponible = True

    with conexion.cursor() as cursor:
        cursor.execute(MESA_RESERVADA_SQL, (fecha, mesa, hora))
        reservaExistente = cursor.fetchone()

        if reservaExistente:
            flash(f"La mesa {mesa} ya está reservada para la fecha {fecha} y hora {hora}. Por favor elija otra mesa o una fecha diferente", 'error')
            disponible = False
    
    conexion.close()

    return disponible