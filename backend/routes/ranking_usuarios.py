from flask import Blueprint, jsonify
from database.conexion import get_connection
from database.queries import (
    RANKING_OBTENER_TODOS,
    RANKING_OBTENER_POR_USUARIO,
    RANKING_SUMAR_CANCELACION,
    RANKING_REINICIAR,
    RANKING_ELIMINAR_USUARIO,
    RANKING_OBTENER_USUARIO_RESERVA,
    DELETE_SQL
)

ranking_usuarios_bp = Blueprint("ranking_usuarios", __name__)

def ejecutar_query(query, parametros=(), fetch_all=False, fetch_one=False, commit=False):
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, parametros)
            
            if commit:
                conexion.commit()
                
            if fetch_all:
                return cursor.fetchall()
            if fetch_one:
                return cursor.fetchone()
                
            return True
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise e
    finally:
        if conexion:
            conexion.close()

@ranking_usuarios_bp.route("/admin/usuarios/ranking", methods=["GET"])
def ver_ranking():
    try:
        ranking = ejecutar_query(RANKING_OBTENER_TODOS, fetch_all=True)
        return jsonify(ranking), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500

@ranking_usuarios_bp.route("/usuarios/<int:id_usuario>/ranking", methods=["GET"])
def ver_ranking_usuario(id_usuario):
    try:
        usuario = ejecutar_query(RANKING_OBTENER_POR_USUARIO, (id_usuario,), fetch_one=True)
        #Si el usuario es nuevo y no tiene historial de ranking, devolvemos 
        # una estructura limpia en 0 con 200 OK para no trabar el Frontend
        if not usuario:
            return jsonify({"id_usuario": id_usuario, "puntos": 0, "cancelaciones": 0}), 200
            
        return jsonify(usuario), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500

@ranking_usuarios_bp.route("/usuarios/<int:id_usuario>/ranking/cancelacion", methods=["PUT"])
def sumar_cancelacion(id_usuario):
    try:
        ejecutar_query(RANKING_SUMAR_CANCELACION, (id_usuario,), commit=True)
        return jsonify({"mensaje": "Cancelación registrada"}), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500

@ranking_usuarios_bp.route("/admin/usuarios/<int:id_usuario>/ranking/reiniciar", methods=["POST"])
def reiniciar_ranking(id_usuario):
    try:
        ejecutar_query(RANKING_REINICIAR, (id_usuario,), commit=True)
        return jsonify({"mensaje": "Ranking reiniciado"}), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500

@ranking_usuarios_bp.route("/admin/usuarios/<int:id_usuario>/ranking", methods=["DELETE"])
def eliminar_ranking(id_usuario):
    try:
        ejecutar_query(RANKING_ELIMINAR_USUARIO, (id_usuario,), commit=True)
        return jsonify({"mensaje": "Usuario eliminado del ranking"}), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500

@ranking_usuarios_bp.route("/reservas/<int:id_reserva>", methods=["DELETE"])
def cancelar_reserva(id_reserva):
    conexion = get_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(RANKING_OBTENER_USUARIO_RESERVA, (id_reserva,))
            reserva = cursor.fetchone()

            if not reserva:
                return jsonify({"mensaje": "Reserva no encontrada"}), 404

            cursor.execute(DELETE_SQL, (id_reserva,))
            cursor.execute(RANKING_SUMAR_CANCELACION, (reserva["id_usuario"],))
            
            conexion.commit()
            return jsonify({"mensaje": "Reserva cancelada y ranking actualizado"}), 200
    except Exception as e:
        conexion.rollback()
        return jsonify({"mensaje": f"Error del servidor: {e}"}), 500
    finally:
        conexion.close()