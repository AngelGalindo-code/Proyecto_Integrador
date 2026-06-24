from flask import Blueprint, jsonify, request
from database.conexion import get_connection

platos_bp = Blueprint("platos", __name__)


def _construir_query_platos(
    categoria_id=None, disponible=None, precio_max=None, precio_min=None
):
    query = "SELECT * FROM platos WHERE 1=1"
    valores = []

    if categoria_id:
        query += " AND id_categoria = %s"
        valores.append(categoria_id)

    if disponible is not None:
        es_disponible = 1 if disponible.lower() in ["true", "1", "yes"] else 0
        query += " AND disponible = %s"
        valores.append(es_disponible)

    if precio_max:
        query += " AND precio <= %s"
        valores.append(float(precio_max))

    if precio_min:
        query += " AND precio >= %s"
        valores.append(float(precio_min))

    return query, valores


@platos_bp.route("/platos", methods=["GET"])
def obtener_todos_platos():
    try:
        categoria_id = request.args.get("categoria")
        disponible = request.args.get("disponible")
        precio_max = request.args.get("precio_max")
        precio_min = request.args.get("precio_min")

        conn = get_connection()
        cursor = conn.cursor()
        query, valores = _construir_query_platos(
            categoria_id=categoria_id,
            disponible=disponible,
            precio_max=precio_max,
            precio_min=precio_min,
        )

        cursor.execute(query, valores)
        filas = cursor.fetchall()
        platos = list(filas)

        cursor.close()
        conn.close()

        return jsonify({"platos":platos}), 200

    except Exception as e:
        return jsonify({
            "code":"500",
            "message":"Internal Server Error",
            "level": "error",
            "description": str(e)
        }), 500


@platos_bp.route("/platos/<int:id>", methods=["GET"])
def obtener_plato_por_id(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM platos WHERE id_plato = %s"
        cursor.execute(query, (id,))
        plato = cursor.fetchone()

        if not plato:
            return jsonify(not_found), 404

        return jsonify(plato), 200
    except Exception as e:
        return jsonify(server_error), 500


@platos_bp.route("/platos", methods=["POST"])
def crear_plato():
    try:
        datos = request.get_json()
        if (
            not datos
            or "nombre" not in datos
            or "precio" not in datos
            or "id_categoria" not in datos
        ):
            error_400 = {
                "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
            return jsonify(error_400), 400

        nombre = datos["nombre"]
        descripcion = datos.get("descripcion", None)
        precio = datos["precio"]  # validar precio?
        disponible = datos.get("disponible", True)
        imagen = datos.get("imagen", None)
        id_categoria = datos["id_categoria"]

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO platos (nombre, descripcion, precio, disponible, id_categoria)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (nombre, descripcion, precio, disponible, id_categoria)

        cursor.execute(query, valores)
        conn.commit()

        nuevo_id = cursor.lastrowid  # guarda el id autoincremental

        cursor.close()
        conn.close()

        return (
            jsonify({"mensaje": "Plato creado exitosamente", "id_plato": nuevo_id}),
            201,
        )

    except Exception as e:
        error_500 = {
            "errors": [
                {
                    "code": "500",
                    "message": "Internal Server Error",
                    "level": "error",
                    "description": str(e),
                }
            ]
        }
        return jsonify(error_500), 500


@platos_bp.route("/platos/<int:id>", methods=["PATCH"])
def actualizar_plato(id):
    try:
        datos = request.get_json()
        if not datos:
            error_400 = {
                "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
            return jsonify(error_400), 400
        campos_permitidos = [
            "nombre",
            "descripcion",
            "precio",
            "disponible",
            "id_categoria",
        ]

        valores = []
        clausulas = []

        for llave, valor in datos.items():
            if llave in campos_permitidos:
                clausulas.append(f"{llave} = %s")
                valores.append(valor)
            else:
                error_400 = {
                    "errors": [
                {
                        "code": "400",
                        "message": "Bad Request",
                        "level": "error",
                        "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
                return jsonify(error_400), 400 

        if not clausulas:
            error_400 = {
                "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
            return jsonify(error_400), 400

        query = f"UPDATE platos SET {', '.join(clausulas)} WHERE id_plato = %s"
        valores.append(id)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, valores)
        conn.commit()

        filas_afectadas = (
            cursor.rowcount
        )  # rowcount cuenta cuántas filas se modificaron

        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            return (
                jsonify(
                    {
                        "mensaje": "No se realizaron cambios (el plato no existe o los datos son idénticos)"
                    }
                ),
                200,
            )

        return jsonify({"mensaje": "Plato actualizado exitosamente"}), 200

    except Exception as e:
        error_500 = {
            "errors": [
                {
                    "code": "500",
                    "message": "Internal Server Error",
                    "level": "error",
                    "description": str(e),
                }
            ]
        }
        return jsonify(error_500), 500


@platos_bp.route("/admin/eliminar", methods=["DELETE"])
def eliminar_plato():

    data = request.json

    if not data:
        error_400 = {
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
        return jsonify(error_400), 400
    
    id = data.get("id_plato")
    
    if not isinstance(id, int) or id <= 0:
        error_400 = {
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
        return jsonify(error_400), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()

        
        query = """
            DELETE FROM platos 
            WHERE id_plato = %s
        """

        cursor.execute(query, (id,))

        if cursor.rowcount == 0:
            error_404 = {
                "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "No se ha mandado el nombre de la categoria o se mandado un dato invalido",
                }
            ]
        }
            return jsonify(error_404), 404
        
        conn.commit()
        return "", 204
    
    except Exception as e:
        print("ERROR", str(e))
        error_500 = {
            "errors": [
                {
                    "code": "500",
                    "message": "Internal Server Error",
                    "level": "error",
                    "description": str(e),
                }
            ]
        }
        return jsonify(error_500), 500
    
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()

