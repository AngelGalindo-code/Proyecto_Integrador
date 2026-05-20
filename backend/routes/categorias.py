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


