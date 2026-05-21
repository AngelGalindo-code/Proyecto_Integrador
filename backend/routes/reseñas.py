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

#Usuario agrega una reseña
@reseñas_bp.route ('/reseñas', methods = ['POST'])
def crear_reseña ():
    con = None
    cursor = None

    try:
         con = get_db()
         cursor = con.cursor()
         data = request.json

         if not data:
            return jsonify({"mensaje": "Campo vacio"}), 400
         
         comentario = data.get("comentario")
         valoracion = data.get("valoracion")
         id_usuario = data.get("id_usuario")

         if comentario is None or valoracion is None or id_usuario is None:
            return jsonify({ "mensaje": "Faltan datos"}), 400
 
         #verificar valoración este entre los valores estimados
         if valoracion < 1 or valoracion > 5:
            return jsonify({"mensaje": "La valoración debe ser entre 1 y 5"}), 400
         
         #verificar que exista el usuario
         cursor.execute(
             'SELECT * FROM usuarios WHERE id = %s',
             (id_usuario,)
         )        
         usuario = cursor.fetchone()
         
         if usuario is None:
             return jsonify({"mensaje": "El usuario no existe"}), 404
         
         #solo se puede reseñar una vez que acuden al lugar luego de una reserva.
         cursor.execute (
             'SELECT * FROM reservas WHERE id_usuario = %s',
             (id_usuario,)
             )
         reserva = cursor.fetchone()

         if reserva is None:
             return jsonify({"mensaje":"Debe haber asistido al restaurante para reseñar."}), 400
         
         #Agregar la reseña
         cursor.execute(
             'INSERT INTO reseñas (id_usuario, comentario, valoracion) VALUES (%s, %s, %s)',
             (id_usuario, comentario, valoracion)
             )
         
         con.commit()

         return jsonify({"mensaje": "Reseña guardada con exito."}), 201

    except Exception:
        return jsonify({"mensaje":"Error del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
