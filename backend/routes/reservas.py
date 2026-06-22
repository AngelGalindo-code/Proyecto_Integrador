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
    cantidad_personas = body.get("cantidad_personas")
    estado = body.get("estado", "pendiente")  # Ver el nombre que tiene en la Base de datos

    if not all([id_usuario, nombre, fecha, hora, cantidad_personas]):
        abort(400, description='Faltan campos obligatorios para registrar la reserva (id_usuario, nombre, fecha, hora, cantidad_personas)')

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            
            query_insert = """
                INSERT INTO reservas (id_usuario, nombre, fecha, hora, cantidad_personas, estado) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_insert, (id_usuario, nombre, fecha, hora, cantidad_personas, estado))
            id_nueva_reserva = cursor.lastrowid
            
            conexion.commit()

            return jsonify({
                "id": id_nueva_reserva,
                "id_usuario": id_usuario,
                "nombre": nombre,
                "fecha": fecha,
                "hora": hora,
                "cantidad_personas": cantidad_personas,
                "estado": estado,
                "message": "Reserva creada con éxito"
            }), 201

    except Exception as e:
        
        conexion.rollback()
        abort(500, description=f'Error interno de servidor: {str(e)}')
    finally:
        conexion.close()

@reservas_bp.route('/reservas', methods=['GET'])
def getReservas():
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_BASE_RESERVAS)
            reservas = cursor.fetchall()
            if not reservas:
                abort(404, description='No se encontraron reservas registradas')
            return jsonify(reservas), 200
    except Exception:
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
            return jsonify(mi_reserva), 200
    except Exception:
        abort(500, description='Error en el servidor al buscar la reserva')
    finally:
        conexion.close()

@reservas_bp.route('/reservas/<int:id_reserva>/mireserva', methods=['GET'])
def obtenerMiReservaPorId(id_reserva):

    return obtenerReservaPorId(id_reserva)


@reservas_bp.route('/reservas/<int:id_reserva>', methods=['PUT'])
def actualizarReserva(id_reserva):
    if id_reserva <= 0:
        abort(400, description='ID de reserva inválido')

    body = request.get_json(silent=True)
    if not body:
        abort(400, description='No se recibió información en el cuerpo de la petición')

    if list(body.keys()) == ['estado']:
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("UPDATE reservas SET estado = %s WHERE id = %s", (body.get('estado'), id_reserva))
                conexion.commit()
                return jsonify({"message": f"Estado de reserva actualizado a {body.get('estado')}"}), 200
        except Exception:
            abort(500, description='Error al actualizar el estado de la asistencia')
        finally:
            conexion.close()

    nombre = body.get("nombre")
    fecha = body.get("fecha")
    mesa = body.get("mesa")
    cantidad_personas = body.get("cantidad_personas")
    hora = body.get("hora") 

    if nombre is None or fecha is None or cantidad_personas is None:
        abort(400, description='Faltan campos obligatorios para actualizar la reserva')

    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(SQL_GET_POR_ID, (id_reserva,))
            existe_reserva = cursor.fetchone()
            if not existe_reserva:
                abort(404, description='No se ha podido encontrar una reserva con ese ID')

            if mesa and hora:
                cursor.execute(MESA_RESERVADA_SQL, (fecha, mesa, hora))
                reserva_existente = cursor.fetchone()
                if reserva_existente and reserva_existente["id_reserva"] != id_reserva:
                    abort(409, description=f'La mesa {mesa} ya está reservada para la fecha {fecha}.')

            cursor.execute(UPDATE_SQL, (nombre, fecha, mesa, cantidad_personas, id_reserva))
            conexion.commit()
            return jsonify({"message": "Reserva actualizada exitosamente de forma completa"}), 200
    except Exception:
        abort(500, description='Error interno del servidor al modificar datos')
    finally:
        conexion.close()

@reservas_bp.route('/reservas/<int:id_reserva>/modificar', methods=['PUT'])
def modificarReservaFront(id_reserva):

    return actualizarReserva(id_reserva)

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
    except Exception:
        return jsonify({"error": "Internal Server Error", "message": "Error en el servidor al intentar eliminar la reserva"}), 500
    finally:
        conexion.close()