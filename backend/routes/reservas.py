from flask import Blueprint, request, jsonify, session, json, abort
from werkzeug.exceptions import HTTPException
from database.conexion import get_connection 
from datetime import datetime
from queries import *

reservas_api_bp = Blueprint("reservas_api", __name__)
FORMATO_FECHA = "%d-%m"

@reservas_api_bp.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        'code' : e.code,
        'name' : e.name,
        'description' : e.description,
    })

    response.content_type = 'application/json'

    return response



@reservas_api_bp.route('/reservas', methods=['GET'])
def getReservas():
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_BASE_RESERVAS)
            reservas = cursor.fetchall()

            if not reservas:
                abort(404, description='No se encontraron reservas registradas') # abort le pasa directamente el error a handle_exception
            
            return jsonify(reservas), 200
            
    except Exception as e:

        abort(500, description='Error al consultar la base de datos')
    
    finally:
        conexion.close()



@reservas_api_bp.route('/reservas/<int:id_reserva>', methods=['GET'])
def obtenerReservaPorId(id_reserva):

    if id_reserva <= 0:
        return jsonify({"error": "Bad Request", "message": "El ID de la reserva debe ser un número entero mayor a cero"}), 400

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_GET_POR_ID, (id_reserva,))
            mi_reserva = cursor.fetchone()

            if not mi_reserva:
                abort(404, description='No se encontró ninguna reserva con ese ID')
            
            return jsonify(mi_reserva), 200
            
    except Exception as e:
        abort(500, description='Error en el servidor al buscar la reserva')
    finally:
        conexion.close()



@reservas_api_bp.route('/reservas/<int:id_reserva>', methods=['PUT'])
def actualizarReserva(id_reserva):
    if id_reserva <= 0:
        abort(400, description='ID de reserva inválido')

    body = request.get_json(silent=True)
    if not body:
        abort(404, description='No se recibió información en el cuerpo de la petición')

    nombre = body.get("nombre")
    fecha = body.get("fecha")
    mesa = body.get("mesa")
    cantidad_personas = body.get("cantidad_personas")
    hora = body.get("hora") 

    if nombre is None or fecha is None or mesa is None or cantidad_personas is None or hora is None:
        abort(400, description='Faltan campos obligatorios (nombre, fecha, mesa, cantidad_personas, hora)')

    try:
        fecha_actual = datetime.now()
        fecha_reserva = datetime.strptime(fecha, FORMATO_FECHA)
        fecha_reserva = fecha_reserva.replace(year=fecha_actual.year)
        
        if fecha_reserva.date() < fecha_actual.date():
            abort(400, description='La fecha de la reserva no puede ser anterior a la fecha actual')

    except (ValueError, TypeError):
        abort(400, description='El formato de fecha es incorrecto. Debe respetar el formato: dia-mes')

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_GET_POR_ID, (id_reserva,))
            existe_reserva = cursor.fetchone()
            if not existe_reserva:
                abort(404, description='No se ha podido encontrar una reserva con ese ID')

            cursor.execute(MESA_RESERVADA_SQL, (fecha, mesa, hora))
            reserva_existente = cursor.fetchone()
            
            if reserva_existente and reserva_existente["id_reserva"] != id_reserva:
                abort(409, description=f'La mesa {mesa} ya está reservada para la fecha {fecha} y hora {hora}.')

            cursor.execute(UPDATE_SQL, (nombre, fecha, mesa, cantidad_personas, id_reserva))
            conexion.commit()

            return jsonify({"message": "Reserva actualizada exitosamente de forma completa"}), 200

    except Exception as e:
        abort(500, description='Error interno del servidor al modificar datos"')
    
    finally:
        conexion.close()



@reservas_api_bp.route('/reservas/<int:id_reserva>', methods=['DELETE'])
def eliminarReserva(id_reserva):
    if id_reserva <= 0:
        return jsonify({"error": "Bad Request", "message": "ID de reserva inválido"}), 400

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_GET_POR_ID, (id_reserva,))
            reserva = cursor.fetchone()

            if not reserva:
                return jsonify({"error": "Not Found", "message": f"No se encontró la reserva con ID {id_reserva}"}), 404
            cursor.execute(DELETE_SQL, (id_reserva,))
            conexion.commit()

            return jsonify({"message": "La reserva fue cancelada y eliminada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": "Error en el servidor al intentar eliminar la reserva"}), 500
    finally:
        conexion.close()