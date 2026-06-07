from flask import Blueprint, request, jsonify, session
from database.conexion import get_connection

from database.queries_entidades.db_usuarios import (
    obtener_usuario_por_email,
    obtener_usuario_por_id,
    insertar_usuario,
    actualizar_usuario_completo,
    actualizar_usuario_parcial
)
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
    
    except Exception:
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
        cursor = conn.cursor(dictionary=True)

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

def actualizar_completamente_usuario(id):

    if id <= 0:
        return jsonify({"message": "ID de usuario invalido."}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "No se recibieron datos para actualizar."}), 400
    
    nombre = data.get("nombre")
    numero = data.get("numero")
    email = data.get("email")

    if not nombre or not numero or not email:
        return jsonify({"message": "Faltan datos obligatorios para la actualizacion completa."}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        usuario = obtener_usuario_por_id(cursor, id)
        if not usuario:
            return jsonify({"message": "El usuario no fue encontrado."}), 404

        actualizar_usuario_completo(cursor, id, nombre, numero, email)
        conn.commit()
        
        return jsonify({"message": "Tus datos se actualizaron correctamente."}), 200
    except Exception:
        return jsonify({"message": "Error al actualizar usuario."}), 500
    
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
     
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        usuario = obtener_usuario_por_id(cursor, id)
        if not usuario:
            return jsonify({"message": "El usuario no fue encontrado."}), 404
        
        campos_a_editar = {}

        if "nombre" in data:
            campos_a_editar["nombre"] = data["nombre"]

        if "numero" in data:
            campos_a_editar["numero"] = data["numero"]

        if "email" in data:
            campos_a_editar["email"] = data["email"]

        actualizar_usuario_parcial(cursor, id, campos_a_editar)
        conn.commit()

        if not campos_a_editar:
            return jsonify({"message": "No se enviaron campos validos para modificar."}), 400

        actualizar_usuario_parcial(cursor, id, campos_a_editar)
        conn.commit()

        return jsonify({"message": "Campos modificados con exito."}), 200
    except Exception:
        return jsonify({"message": "Error al actualizar usuario parcialmente."}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   
   
@usuarios_bp.route('/usuarios/<id>/eliminar', methods=['POST'])

def eliminarUsuario(id):

    if id <= 0:
        return jsonify({"message": "El ID es invalido."}), 400
    
    try:
        
        eliminado = eliminarUsuarioPorId(id) 
        if not eliminado:
            return jsonify({"message": "No existe un usuario con ese ID."}), 404

        return jsonify({"message": "Usuario eliminado correctamente."}), 200
    except Exception:
        return jsonify({"message": "Error al eliminar usuario."}), 50
        
         
@usuarios_bp.route('/admin/usuarios', methods=['GET'])

def adminUsuarios():

    try:

        if session.get('rol') != 'admin':

            flash('Acceso denegado')

            return redirect('/')

        usuarios = getUsuarios()

        if not usuarios:

            flash('No hay usuarios registrados')

            return render_template('errors/sinusuarios.html')

        return render_template('adminUsuarios.html', title='Usuarios',usuarios=usuarios)

    except Exception:
        return render_template('errorGenerico.html',message='Error al obtener usuarios')       
        
        
        
            
@usuarios_bp.route('/admin/usuarios/<id>', methods=['GET'])

def adminUsuarioPorId(id):

    try:

        id = int(id)

        if session.get('rol') != 'admin':

            flash('Acceso denegado')

            return redirect('/')

        usuario = getUsuarioPorId(id)

        if not usuario:

            flash('El usuario no fue encontrado')

            return render_template('errors/404_notFound.html')

        return render_template('adminUsuario.html',title='Usuario', usuario=usuario)

    except ValueError:

        flash('El ID es invalido')

        return render_template('errors/404_notFound.html')

    except Exception:
        return render_template('errorGenerico.html', message='Error al obtener el usuario')
    
