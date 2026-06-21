from flask import Blueprint, request, jsonify
from database.conexion import get_connection
from database.queries_entidades.db_usuarios import *
from datetime import datetime, timezone, timedelta
import jwt
import os

usuarios_bp = Blueprint("usuarios", __name__)
@usuarios_bp.route('/usuarios', methods=['POST'])

def crear_usuario():

    data = request.get_json()
    if not data:
        return jsonify({"message": "No se recibieron datos en la peticion."}), 400

    nombre = data.get("nombre")
    numero = data.get("numero")
    email = data.get("email")

    
    if not nombre or not numero or not email:
        return jsonify({"message": "Faltan datos obligatorios"}), 400
    
    if len(str(nombre).strip()) == 0 or not str(numero).isdigit() or '@' not in str(email):
        return jsonify({"message": "Formatos de campos invalidos"}), 400
    
    conn = None
    cursor = None
    try: 
        conn = get_connection()
        cursor = conn.cursor()
        

        existe = obtener_usuario_por_email(cursor, email)
        if existe:
            return jsonify({"message": "Este email ya esta registrado."}), 409

        insertar_usuario(cursor, nombre, numero, email)
        conn.commit()

        return jsonify({"message": "Usuario creado con exito!"}), 201
    
    except Exception as e:
        print("error:", str(e)) 
        return jsonify({"message": "Error del servidor al intentar crear el usuario."}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   

@usuarios_bp.route('/login', methods=['POST'])

def login():
    body = request.get_json()

    nombre_usuario = body.get("usuario")
    email = body.get("email")

    if email is None or nombre_usuario is None:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "el nombre o el usuario no han sido ingresados",
                }
            ),
            400,
        )

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        usuario = obtener_usuario_por_email(cursor, email)

        if not usuario:
            return (
                jsonify(
                    {"error": "Not Found", "message": "El usuario no está registrado"}
                ),
                404,
            )

        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": str(usuario["id"]),
            "rol": usuario["rol"],
            "iat": ahora,
            "exp": ahora + timedelta(hours=8),  # expira en 8 horas
        }

        token = jwt.encode(
            payload, os.getenv("JWT_SECRET", "change-me-please"), algorithm="HS256"
        )

        return (
            jsonify(
                {
                    "usuario": {
                        "id": usuario["id"],
                        "nombre": usuario["nombre"],
                        "email": usuario["email"],
                        "numero": usuario["numero"],
                        "rol": usuario["rol"],
                    },
                    "token": token,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": f"Error del servidor {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@usuarios_bp.route('/usuarios/<int:id>', methods=['POST'])
def actualizar_parcialmente_ususario(id):
    if id <= 0:
        return jsonify({"message": "ID de usuario invalido."}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "No se recibio informacion para editar."}), 400
    try:
        usuario = getUsuarioPorId(id)
        if not usuario:
            return jsonify({"message": "El usuario no fue encontrado."}), 404
        
        campos_a_editar = {}
        if "nombre" in data:
            campos_a_editar["nombre"] = data["nombre"]
        if "numero" in data: 
            campos_a_editar["numero"] = data["numero"]
        if "email" in data:  
            campos_a_editar["email"] = data["email"]

        if not campos_a_editar:
            return jsonify({"message": "No se enviaron campos validos para modificar."}), 400

        actualizar_usuario_parcial(id, campos_a_editar)

        return jsonify({"message": "Campos modificados con exito."}), 200
    except Exception as e:
        print("error:", str(e)) 
        return jsonify({"message": f"Error del servidor: {str(e)}"}), 500 
    
@usuarios_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
def eliminarUsuario(id):
    try:
        
        id_entero = int(id)
        if id_entero <= 0:
            return jsonify({"message": "El ID es invalido."}), 400
        
    
        eliminado = eliminarUsuarioPorId(id_entero) 
        if not eliminado:
            return jsonify({"message": "No existe un usuario con ese ID."}), 404

        return jsonify({"message": "Usuario eliminado correctamente."}), 200

    except ValueError:
        
        return jsonify({"message": "El ID debe ser un numero entero."}), 400

    except Exception:
       
        return jsonify({"message": "Error al eliminar usuario."}), 500
         
@usuarios_bp.route('/admin/usuarios', methods=['GET'])
def adminUsuarios():
    try:
        # Comentado temporalmente para pruebas en Postman
        # if session.get('rol') != 'admin':
        #if session.get('rol') != 'admin':
        #    return jsonify({"message": "Acceso denegado. Se requieren permisos de administrador."}), 403

        usuarios = getUsuarios()

        if not usuarios:
            return jsonify({"message": "No hay usuarios registrados.", "usuarios": []}), 200

    
        return jsonify({"message": "Usuarios obtenidos correctamente.", "usuarios": usuarios}), 200

    except Exception:
        return jsonify({"message": "Error al obtener usuarios."}), 500       
        
        
@usuarios_bp.route('/admin/usuarios/<int:id>', methods=['GET'])
def adminUsuarioPorId(id):
    try:
        id_entero = int(id)
        if id_entero <= 0:
            return jsonify({"message": "El ID es invalido."}), 400
            
        # Comentado temporalmente para pruebas en Postman
        # if session.get('rol') != 'admin':
        #     return jsonify({"message": "Acceso denegado. Se requieren permisos de administrador."}), 403

        usuario = getUsuarioPorId(id_entero)

        if not usuario:
            return jsonify({"message": "El usuario no fue encontrado."}), 404
    
        return jsonify({"message": "Usuario encontrado.", "usuario": usuario }), 200

    except Exception as e:
        print(f"Error en ruta adminUsuarioPorId: {e}")
        return jsonify({"message": "Error al obtener el usuario."}), 500