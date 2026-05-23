from flask import flash
from sqlalchemy import create_engine, text
from querys import *

# Url de la base de datos
DATABASE_URL = ""

motor = create_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=3600

)


def getReservas() -> list[dict]:
    
    with motor.connect() as conexion:
        ejecucion = conexion.execute(text(SQL_BASE_RESERVAS)) # Se debe de pasar en formato texto
        reservas = [dict(fila) for fila in ejecucion.mappings().fetchall()] # Aca los profes usaron una funcion que convertia en diccionario

        return reservas
    
def getReservaPorId(id_reserva):
    
    with motor.connect() as conexion:
        ejecucion = conexion.execute(text(SQL_GET_POR_ID), {'id_reserva' : id_reserva})
        miReserva = ejecucion.mappings().fetchone() 

        if miReserva:
            miReserva = dict(miReserva)

            return miReserva
        
        flash('No se encontro ninguna reserva con ese ID')


def actualizarReserva(nombre, fecha, mesa, cantidad_personas, id_reserva):

    with motor.connect() as conexion:
        ejecucion = conexion.execute(text(SQL_GET_POR_ID),{'id_reserva' : id_reserva})
        miReserva = ejecucion.mappings().fetchone()

        if miReserva:
            ejecucion = conexion.execute(text(UPDATE_SQL), 
                                         {'nombre' : nombre,
                                          'fecha' : fecha,
                                          'mesa' : mesa,
                                          'cantidad_personas' : cantidad_personas,
                                          'id_reserva' : id_reserva
                                          })

            conexion.commit()
            flash('Reserva actualizada exitosamente')

            return None


        else:
            flash('No se ha podido encontrar una reserva con ese ID') # Ver si es buena practica que no retorne nada
            return False