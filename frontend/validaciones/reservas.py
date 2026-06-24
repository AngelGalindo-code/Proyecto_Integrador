from flask import flash
from datetime import datetime

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
        formatoHTML = "%Y-%m-%d"
        
        
        fechaActual = datetime.now().date()
        fechaReserva = datetime.strptime(fecha, formatoHTML).date()

        if fechaReserva < fechaActual:
            flash("La fecha de la reserva no puede ser anterior a la fecha actual.", "error")
            return False
            
        # Si todo está bien, devolvemos True (o el objeto fechaReserva si lo usas en otro lado)
        return True
        
    except (ValueError, TypeError):
        flash("El formato de fecha recibido es incorrecto.", "error")
        return False


def validarMesaDisponible(fecha, mesa, hora):

    disponibilidad = verDisponibilidadMesa(fecha, mesa, hora)

    if not disponibilidad:
        return False # No damos mensaje, ya que se encuentra en validarDisponibilidadMesa
    
    return True
    
        