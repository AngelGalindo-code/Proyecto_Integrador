from flask import Blueprint, jsonify, request

import mysql.connector

reseñas_bp = Blueprint("reseñas",__name__)

def get_db():

    return mysql.connector.connect(

    host="localhost",

    user="root",

    password="",

    database="Restaurante"
    )

#Muestra todas las reseñas de un usuario.
@reseñas_bp.route ('/usuarios/reseñas/<int:id_usuario>', methods = ['GET'])
def mostrar_todas_reseñas (id_usuario):
    con = None
    cursor = None
    try:
        con = get_db()
        cursor = con.cursor()
        
        cursor.execute(
            'SELECT * FROM reseñas WHERE id_usuario = %s',
            (id_usuario,)
                       )
        reseñas = cursor.fetchall()

        if len(reseñas) == 0:
            return jsonify({"mensaje":"Actualmente no existen reseñas."}),404
        
        return jsonify(reseñas), 200
    
    except Exception:
        return jsonify({"mensaje":"Error del servidor"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

#Usuario quiere ver una reseña en especifico.
@reseñas_bp.route ('/reseñas/<int:id_comentario>', methods = ['GET'])
def mostrar_reseña (id_comentario):
    con = None
    cursor = None

    try:
        con = get_db()
        cursor = con.cursor()
        
        #verificamos que exista la reseña
        cursor.execute(
            'SELECT * FROM reseñas WHERE id_comentario = %s',
            (id_comentario,)
                       )
        reseña = cursor.fetchone()

        if reseña is None:
            return jsonify({"mensaje":"La reseña no existe."}),404
        
        return jsonify(reseña), 200
    
    except Exception:
        return jsonify({"mensaje":"Error del servidor"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()