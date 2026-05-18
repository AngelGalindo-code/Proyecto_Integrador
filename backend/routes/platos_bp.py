from flask import Blueprint, jsonify, request
from errores import bad_request, not_found, server_error, conflict
from db import get_connection

platos_bp = Blueprint('platos', __name__)

@platos_bp.route('/platos', methods=['GET'])
def obtener_todos_platos():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM platos")
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
        
        query = "SELECT * FROM platos WHERE id = %s"
        cursor.execute(query, (id,))
        plato = cursor.fetchone()
        
        if not plato:
            return jsonify(not_found), 404
            
        return jsonify(plato), 200
    except Exception as e:
        return jsonify(server_error), 500
    
@platos_bp.route('/platos', methods=['POST'])
def crear_plato():
    ...

@platos_bp.route('/platos/<int:id>', methods=['PUT'])
def actualizar_plato(id):
    ...

@platos_bp.route('/platos/<int:id>', methods=['DELETE'])
def eliminar_plato(id):