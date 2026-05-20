from flask import Blueprint, request, jsonify
from db import get_connection

categorias_bp = Blueprint("categorias", __name__)

@categorias_bp.route("/", methods=["GET"])
def listar_comidas_categoria():  
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query_platos_por_categoria =  """
        SELECT c.id_categoria,
        c.nombre_categoria, 
        p.nombre_plato, 
        p.precio 
FROM categorias c
INNER JOIN platos p
ON c.id_categoria = p.id_categoria
"""
        cur.execute(
           query_platos_por_categoria
        )

        categorias = cur.fetchall()

        if not categorias:
            error_404 = {
                "errors": [
                    {
                        "code": "404",
                        "message": "Not Found",
                        "level": "error",
                        "description": "No se encontro ninguna comida de esta categoria",
                    }
                ]
            }
            return jsonify(error_404), 404

        resultado_categorias = []
        platos_categoria = {}
        for categoria in categorias:

            id_categoria = categoria["id_categoria"]
            nombre_categoria = categoria["nombre_categoria"]
            nombre_plato = categoria["nombre_plato"]
            precio = categoria["precio"]

            if id_categoria not in platos_categoria:
                platos_categoria[id_categoria] = {
                    "id_categoria": id_categoria,
                    "nombre_categoria": nombre_categoria,
                    "plato": [{"nombre_plato": nombre_plato, "precio": precio}],
                }

            else:
                platos_categoria[id_categoria]["plato"].append(
                    {"nombre_plato": nombre_plato, "precio": precio}
                )

        for categoria in platos_categoria.values():
            resultado_categorias.append(categoria)

        return jsonify({"categoria": resultado_categorias}), 200

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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@categorias_bp.route("/nombres", methods=["GET"])
def obtener_nombres_categorias():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query_obtener_categorias =  """
        SELECT * FROM categorias ORDER BY nombre_categoria
        """

        cur.execute(
           query_obtener_categorias
        )

        categorias = cur.fetchall()

        if not categorias:
            error_404 = {
                "errors": [
                    {
                        "code": "404",
                        "message": "Not Found",
                        "level": "error",
                        "description": "No se encontro ninguna comida de esta categoria",
                    }
                ]
            }
            return jsonify(error_404), 404
        

        return jsonify({"categoria": categorias}), 200

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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@categorias_bp.route("/categorias", methods=["POST"]) #usuario admin
def agregar_categoria():
    data = request.json
    nombre_categoria = data.get("nombre_categoria")

    if (
        not nombre_categoria
        or not isinstance(nombre_categoria, str)
        or not nombre_categoria.strip()
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

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query_validar_existencia_id = """
        SELECT * FROM categorias 
WHERE nombre_categoria = %s      
"""
        cur.execute(query_validar_existencia_id, (nombre_categoria,))
        categoria = cur.fetchone()
        if categoria:
            error_409 = {
                "errors": [
                    {
                        "code": "409",
                        "message": "Conflict",
                        "level": "error",
                        "description": "La categoria ya existe",
                    }
                ]
            }
            return jsonify(error_409), 409

        querey_insertar_valores = """
INSERT INTO categorias (nombre_categoria) VALUES
                    (%s)
"""
        cur.execute(querey_insertar_valores, (nombre_categoria,))
        conn.commit()

        return "", 201
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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@categorias_bp.route("/categorias/<int:id>", methods=["PUT"]) #usuario admin
def modificar_nombre(id):
    data = request.json
    if not data or id <= 0 or "nombre_categoria" not in data:
        error_400 = {
            "errors": [
                {
                    "code": "400",
                    "message": "Bad Request",
                    "level": "error",
                    "description": "Se ha mandado un dato invalido o no se recibio el nombre de la categoria a cambiar.",
                }
            ]
        }
        return jsonify(error_400), 400


    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        nombre_categoria = data.get("nombre_categoria")
        cur.execute("SELECT * FROM categorias WHERE nombre_categoria = %s", (nombre_categoria,))

        categoria = cur.fetchone()
        if categoria:
            error_409 = {
                "errors": [
                    {
                        "code": "409",
                        "message": "Conflict",
                        "level": "error",
                        "description": "La categoria ya existe",
                    }
                ]
            }
            return jsonify(error_409), 409
        cur.execute("SELECT * FROM categorias WHERE id_categoria = %s", (id,))
        categoria = cur.fetchone()

       
        
        if not categoria:
            error_404 = {
                "errors": [
                    {
                        "code": "404",
                        "message": "Not Found",
                        "level": "error",
                        "description": "No se encontro una categoria con ese id",
                    }
                ]
            }
            return jsonify(error_404), 404

        cur.execute(
            """
UPDATE categorias 
SET nombre_categoria = %s
WHERE id_categoria = %s 
""",
            (nombre_categoria, id),
        )
        conn.commit()

        return "", 204
    
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
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()