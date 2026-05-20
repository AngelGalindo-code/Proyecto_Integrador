from flask import request, jsonify, session

usuarios_bp = Blueprint("usuarios", __name__) 

@usuarios_bp.route('/usuarios', methods=['POST'])

def crear_usuario():
    body = request.get_json(silent=True)

    if not body:
        return jsonify({"error": "Bad Request", "message": "cuerpo vacio"}), 400

    nombre = body.get("nombre")
    numero = body.get("numero")
    email = body.get("email")

    if nombre is None or numero is None or email is None:
        return jsonify({"error": "Bad request", "message" : "Faltan datos"}), 400
    
    
    if len(str(nombre)) == 0 or not numero.isdigit() or '@' not in email:
        return jsonify({"error": "Bad Request", "message": "Formatos de campos invalidos"}), 400
    
    conn = None
    cursor = None
    
    try: 
        conn = get_conection()
        cursor = conn.cursor()
        
        check_query = "SELECT id FROM usuarios WHERE email = %s"
        cursor.execute(check_query, (email,))

        existe = cursor.fetchone

        if existe:
            return jsonify({"error": "Conflict", "message": "Este email ya está registrado"}), 409
        else:
            rol_por_defecto = "usuario"

            query = """INSERT into usuarios (nombre, numero, email, rol) VALUES (%s, %s, %s, %s)
            """
        cursor.execute(query, (nombre, numero, email, rol_por_defecto))
        conn.commit()
        return jsonify({"message" : "usuario creado"}), 201
    
    except Exception:
        return jsonify({"message" : "Error del servidor"}), 500
         
    finally:
        if cursor:
                cursor.close()
        if conn:
                conn.close()

@usuarios_bp.route('/login', methods=['POST'])

def login():
    body = request.get_json()

    email = body.get("email")

    if email is None:
        return jsonify({"error": "Bad Request", "message": "no se ingreso ningun email"}), 400

    try: 
        conn = get_conection()
        cursor = conn.cursor()

        query = """
        SELECT id, rol FROM usuarios WHERE email = %s
        """
        cursor.execute(query, (email,))
        usuario = cursor.fetchone() 
        

        if not usuario:
            return jsonify({"error": "Not Found", "message": "El email no está registrado"}), 404
        
        else:
            session["id_usuario"] = usuario[0]
            session["rol"] = usuario[1]

            return jsonify({"message": f"Has ingresado como {usuario[1]}", "id": usuario[0], "rol": usuario[1]}), 200
    except Exception:
        return jsonify({"message" : "Error del servidor"}), 500
         
    finally:
        if cursor:
                cursor.close()
        if conn:
                conn.close()

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])

def actualizar_completamente_usuario(id):
     
    if id <= 0:
        return jsonify({"error" : "Bad Request", "message" : "Id invalido"}), 400

    body = request.get_json(silent= True)

    if body == None:
        return jsonify({"error" : "Bad Request", "message" : "No se recibio informacion en el cuerpo de la peticion"}), 400
    
    nombre = body.get("nombre")
    numero = body.get("numero")
    email = body.get("email")

    if nombre is None or numero is None or email is None:
        return jsonify({"error": "Bad Request", "message": "Faltan campos obligatorios"}), 400
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        check_query = """
        SELECT * FROM usuarios WHERE id = %s
        """
        cursor.execute(check_query, id,)

        usuario = cursor.fetchone()

        if not usuario:
             return jsonify({"error": "Not Found", "message": "Usuario no encontrado"}), 404
        
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE usuarios SET nombre = %s, numero = %s,
        email = %s WHERE id = %s
        """
        cursor.execute(query, id)
        conn.commit()
        
        return jsonify({"message": "Usuario actualizado por completo"}), 200
    
    except Exception :
        return jsonify({"message" : "Error del servidor"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()