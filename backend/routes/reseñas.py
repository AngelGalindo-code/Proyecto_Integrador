from flask import Blueprint, jsonify, request
from database.conexion import get_connection

reseñas_bp = Blueprint("reseñas", __name__)


# Obtiene todas las reseñas existentes
@reseñas_bp.route("/resenas", methods=["GET"])
def obtener_resenas():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT u.nombre,
        r.id_comentario,
        r.comentario,
        r.valoracion
FROM resenas r 
INNER JOIN usuarios u
ON r.id_usuario = u.id 
ORDER BY valoracion DESC
""")

        resenas = cursor.fetchall()

        return jsonify({"reseñas": resenas}), 200

    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor {e}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Muestra todas las reseñas de un usuario.
@reseñas_bp.route("/usuarios/<int:id_usuario>/resenas", methods=["GET"])
def mostrar_todas_reseñas(id_usuario):
    con = None
    cursor = None
    try:
        con = get_connection()
        cursor = con.cursor()

        cursor.execute("SELECT * FROM resenas WHERE id_usuario = %s", (id_usuario,))
        reseñas = cursor.fetchall()

        if not reseñas:
            return jsonify([]), 200

        return jsonify(reseñas), 200

    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor {str(e)}"}), 500

    finally:
        if cursor: cursor.close()
        if con: con.close()


# Usuario quiere ver una reseña en especifico.
@reseñas_bp.route("/reseñas/<int:id_comentario>", methods=["GET"])
def mostrar_reseña(id_comentario):
    con = None
    cursor = None

    try:
        con = get_connection()
        cursor = con.cursor()

        # verificamos que exista la reseña
        cursor.execute(
            "SELECT * FROM resenas WHERE id_comentario = %s", (id_comentario,)
        )
        reseña = cursor.fetchone()

        if reseña is None:
            return jsonify({"mensaje": "La reseña no existe."}), 404

        return jsonify(reseña), 200

    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


# Usuario agrega una reseña
@reseñas_bp.route("/reseñas", methods=["POST"])
def crear_reseña():
    data = request.json

    if not data:
        return jsonify({"mensaje": "Campo vacio"}), 400

    id_usuario = data.get("id_usuario")
    comentario = data.get("comentario")
    valoracion = data.get("valoracion")

    if comentario is None or valoracion is None or id_usuario is None:
        return jsonify({"mensaje": "Faltan datos"}), 400

    # verificar valoración este entre los valores estimados
    if valoracion < 1 or valoracion > 5:
        return jsonify({"mensaje": "La valoración debe ser entre 1 y 5"}), 400

    con = None
    cursor = None

    try:
        con = get_connection()
        cursor = con.cursor()

        # verificar que exista el usuario
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
        usuario = cursor.fetchone()

        if usuario is None:
            return jsonify({"mensaje": "El usuario no existe"}), 404

        # solo se puede reseñar si existe la reserva y el estado esta en estado finalizada.
        cursor.execute(
            "SELECT * FROM reservas WHERE id_usuario = %s AND estado = %s",
            (id_usuario, "Finalizada"),
        )

        reserva = cursor.fetchall()

        if reserva is None:
            return (
                jsonify({"mensaje": "El usuario aun no asistio al restaurante."}),
                404,
            )

        # Agregar la reseña
        cursor.execute(
            "INSERT INTO resenas (id_usuario, comentario, valoracion) VALUES (%s, %s, %s)",
            (id_usuario, comentario, valoracion),
        )

        con.commit()

        return "", 201

    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


# Usuario edita reseña
@reseñas_bp.route("/reseñas/<int:id_comentario>", methods=["PUT"])
def modificar_reseña(id_comentario):

    con = None
    cursor = None

    try:
        con = get_connection()
        cursor = con.cursor()
        data = request.json

        if not data:
            return jsonify({"mensaje": "campo vacio"}), 400

        comentario = data.get("comentario")
        valoracion = data.get("valoracion")
        id_usuario = data.get("id_usuario")

        if comentario is None or valoracion is None or id_usuario is None:
            return jsonify({"mensaje": "Faltan datos"}), 400

        # verificar valoración este entre los valores estimados
        if valoracion < 1 or valoracion > 5:
            return jsonify({"mensaje": "La valoración debe ser entre 1 y 5"}), 400

        # verificar si existe la reseña
        cursor.execute(
            "SELECT * FROM resenas WHERE id_comentario = %s", (id_comentario,)
        )
        reseña = cursor.fetchone()

        if reseña is None:
            return jsonify({"mensaje": "La reseña no existe."}), 404

        # verificar que el usuario que quiera modificar la reseña el autor
        if reseña["id_usuario"] != id_usuario:
            return (
                jsonify({"mensaje": "No tiene permisos para modificar esta reseña"}),
                403,
            )

        # modificar reseña
        cursor.execute(
            "UPDATE resenas SET comentario = %s, valoracion = %s WHERE id_comentario = %s",
            (comentario, valoracion, id_comentario),
        )

        con.commit()

        return "", 204

    except Exception as e:
        return jsonify({"mensaje": f"Error del servidor {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


# Usuario elimina reseña
@reseñas_bp.route("/reseñas/<int:id_comentario>", methods=["DELETE"])
def eliminar_reseña(id_comentario):
    con = None
    cursor = None

    try:
        con = get_connection()
        cursor = con.cursor()
        data = request.json

        if not data:
            return jsonify({"mensaje": "Campo vacio"}), 400

        id_usuario = data.get("id_usuario")

        if id_usuario is None:
            return jsonify({"mensaje": "Falta id_usuario"}), 400

        # verificar si existe la reseña
        cursor.execute(
            "SELECT * FROM resenas WHERE id_comentario = %s", (id_comentario,)
        )
        reseña = cursor.fetchone()

        if reseña is None:
            return jsonify({"mensaje": "La reseña no existe."}), 404

        # verificar que solo el autor de la reseña sea capaz de eliminarla.

        if reseña["id_usuario"] != id_usuario:
            return (
                jsonify({"mensaje": "No tiene permisos para eliminar esta reseña"}),
                403,
            )

        cursor.execute("DELETE FROM resenas WHERE id_comentario = %s", (id_comentario,))
        con.commit()

        return "", 204

    except Exception as e:

        return jsonify({"mensaje": f"Error del servidor {str(e)}"}), 500

    finally:

        if cursor:
            cursor.close()

        if con:
            con.close()

