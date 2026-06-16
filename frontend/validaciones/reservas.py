from flask import flash
from datetime import datetime
from database.db_reservas import verDisponibilidadMesa


# En la query falta la hora!
formatoFecha = "%d-%m" # No creo que sea necesario el anio, ya que se entiende que corre el anio actual



def validarId(id_reserva):

    try:
        id_reserva = int(id_reserva)

        if id_reserva <= 0:

            flash("El ID de la reserva debe ser un número entero y mayor a cero")
            return False
            
        return id_reserva
    
    except (ValueError, TypeError):
        flash("Solo debe proporcionar un número entero como ID de la reserva")
        return False
    

def validarFecha(fecha):
        
    try:
        fechaActual = datetime.now()
        fechaReserva = datetime.strptime(fecha, formatoFecha)

        if fechaReserva < fechaActual:
            flash(f"La fecha de la reserva no puede ser anterior o igual a la fecha actual: {fechaActual}")
            return False
            
        return fechaReserva
        
    except ValueError or TypeError:
        flash("El formato de fecha es incorrecto. Por favor respetar el siguiente formato: dia-mes-anio")
        return False
        


def validarMesaDisponible(fecha, mesa, hora):

    disponibilidad = verDisponibilidadMesa(fecha, mesa, hora)

    if not disponibilidad:
        return False # No damos mensaje, ya que se encuentra en validarDisponibilidadMesa
    
    return True
    
        