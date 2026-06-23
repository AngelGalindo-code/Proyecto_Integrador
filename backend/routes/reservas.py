from flask import Blueprint, request, jsonify, json, abort
from werkzeug.exceptions import HTTPException
from database.conexion import get_connection 
from datetime import datetime
from database.queries import *

reservas_bp = Blueprint("reservas", __name__)
FORMATO_FECHA = "%d-%m"

@reservas_bp.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        'code' : e.code,
        'name' : e.name,
        'description' : e.description,
    })

    response.content_type = 'application/json'

    return response

@reservas_bp.route('/reservas', methods=['POST'])
def crearReserva():
    body = request.get_json(silent=True)
    if not body:
        abort(400, description='No se recibieron datos')

    id_usuario = body.get("id_usuario")
    nombre = body.get("nombre")
    fecha = body.get("fecha")
    hora = body.get("hora")
    mesa = body.get("mesa")
    cantidad_personas = body.get("cantidad_personas")
    estado = body.get("estado", "pendiente")  # Ver el nombre que tiene en la Base de datos

    if not all([id_usuario, nombre, fecha, hora, mesa, cantidad_personas]):
        abort(400, description='Faltan campos obligatorios para registrar la reserva (id_usuario, nombre, fecha, hora, mesa, cantidad_personas)')

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            # Combinamos la fecha y la hora en el formato correcto: '2026-06-22 14:03:00'
            fecha_hora_combinada = f"{fecha} {hora}:00"

            query_insert = """
                INSERT INTO reservas (id_usuario, nombre, fecha, hora, mesa, cantidad_personas, estado) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Pasamos 'fecha_hora_combinada' en el lugar correspondiente a la columna 'hora'
            cursor.execute(query_insert, (id_usuario, nombre, fecha, fecha_hora_combinada, mesa, cantidad_personas, estado))
            id_nueva_reserva = cursor.lastrowid
            
            conexion.commit()
            
            conexion.commit()

            return jsonify({
                "id": id_nueva_reserva,
                "id_usuario": id_usuario,
                "nombre": nombre,
                "fecha": fecha,
                "hora": hora,
                "mesa": mesa,
                "cantidad_personas": cantidad_personas,
                "estado": estado,
                "message": "Reserva creada con éxito"
            }), 201

    except Exception as e:
        conexion.rollback()
        print(f"error: {str(e)}") 
        abort(500, description=f'Error interno de servidor: {str(e)}')


@reservas_bp.route('/reservas', methods=['GET'])
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



@reservas_bp.route('/reservas/<int:id_reserva>', methods=['GET'])
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
                
            reserva_mapeada = {
                "id": mi_reserva.get('id_reserva') or mi_reserva.get('id'),
                "id_usuario": mi_reserva.get('id_usuario'), 
                "nombre": mi_reserva.get('nombre'),
                "mesa": mi_reserva.get('mesa'),
                "cantidad_personas": mi_reserva.get('cantidad_personas'),
                "fecha": str(mi_reserva.get('fecha')),
                "hora": str(mi_reserva.get('hora'))
            }
            return jsonify(reserva_mapeada), 200
            
    except Exception as e:
        abort(500, description='Error en el servidor al buscar la reserva')
    finally:
        conexion.close()



@reservas_bp.route('/reservas/<int:id_reserva>', methods=['PUT'])
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



@reservas_bp.route('/reservas/<int:id_reserva>', methods=['DELETE'])
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