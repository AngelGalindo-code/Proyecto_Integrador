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

