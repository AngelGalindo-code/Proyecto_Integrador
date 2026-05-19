from flask import Blueprint, jsonify, request
from errores import bad_request, not_found, server_error, conflict
from db import get_connection

platos_bp = Blueprint('platos', __name__)

def construir_query_platos(categoria_id=None, disponible=None, precio_max=None, precio_min=None):
    query = "SELECT * FROM platos WHERE eliminado = 0"
    valores = []

    if categoria_id:
        query += " AND id_categoria = %s"
        valores.append(categoria_id)

    if disponible is not None:
        es_disponible = 1 if disponible.lower() in ['true', '1', 'yes'] else 0
        query += " AND disponible = %s"
        valores.append(es_disponible)

    if precio_max:
        query += " AND precio <= %s"
        valores.append(float(precio_max))

    if precio_min:
        query += " AND precio >= %s"
        valores.append(float(precio_min))

    return query, valores

@platos_bp.route('/platos', methods=['GET'])
def obtener_todos_platos():
    try:
        categoria_id = request.args.get('categoria')
        disponible = request.args.get('disponible')
        precio_max = request.args.get('precio_max')
        precio_min = request.args.get('precio_min')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query, valores = construir_query_platos(
            categoria_id=categoria_id, 
            disponible=disponible, 
            precio_max=precio_max, 
            precio_min=precio_min
        )

        cursor.execute(query, valores)
        platos = cursor.fetchall()
        
        cursor.close()
        conn.close()

        return jsonify(platos), 200
        
    except Exception as e:
        return jsonify(server_error), 500

@platos_bp.route('/platos/<int:id>', methods=['GET'])
def obtener_plato_por_id(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM platos WHERE id = %s AND eliminado = 0"
        cursor.execute(query, (id,))
        plato = cursor.fetchone()
        
        if not plato:
            return jsonify(not_found), 404
            
        return jsonify(plato), 200
    except Exception as e:
        return jsonify(server_error), 500
