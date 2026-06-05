from flask import request, jsonify, session
# Agregar librerias 

usuarios_bp = Blueprint("usuarios", __name__) 

@usuarios_bp.route('/usuarios', methods=['POST'])

def crear_usuario():

    if not request.form:
        flash("No se recibió información en el formulario.")
        return redirect('/registro'), 400

    nombre = request.form.get("nombre")
    numero = request.form.get("numero")
    email = request.form.get("email")

    if not nombre or not numero or not email:
        flash("Faltan datos obligatorios por completar")
        return redirect('/registro'), 400
    
    if len(str(nombre).strip()) == 0 or not numero.isdigit() or '@' not in email:
        flash("Formatos de campos invalidos. Por favor, revisa los datos ingresados")
        return redirect('/registro'), 400
    
    conn = None
    cursor = None
    
    try: 
        conn = get_conection()
        cursor = conn.cursor()
        
        check_query = "SELECT id FROM usuarios WHERE email = %s"
        cursor.execute(check_query, (email,))

        existe = cursor.fetchone

        if existe:
                flash("Este email ya está registrado.", "error")
                return render_template('registro.html')

        query = """INSERT into usuarios (nombre, numero, email, rol) VALUES (%s, %s, %s, %s)
            """
        cursor.execute(query, (nombre, numero, email, rol_por_defecto))
        conn.commit()

        flash("¡Usuario creado con exito!")
        return redirect(url_for('publicas.index'))
    
    except Exception:
        return render_template('errorGenerico.html', message="Error del servidor al intentar crear el usuario")
         
    finally:
        if cursor:
                cursor.close()
        if conn:
                conn.close()

@usuarios_bp.route('/login', methods=['POST'])

def login():
    if request.method == 'POST':

        email = request.form.get("email")

    if email is None :

        flash("No se ingresó ningún email.", "error")
        return render_template('registro.html'), 400

    try: 
        conn = get_conection()
        cursor = conn.cursor()

        query = """
        SELECT id, rol FROM usuarios WHERE email = %s
        """
        cursor.execute(query, (email,))
        usuario = cursor.fetchone() 
        

        if not usuario:
            flash("El usuario no fue encontrado o el email es incorrecto.", "error")
            return render_template('login.html'), 404
            
        else:
            session["id_usuario"] = usuario[0]
            session["rol"] = usuario[1]

            flash(f"¡Bienvenido! Has ingresado como {usuario[1]}.", "success")
                
            return redirect(url_for('publicas.index'))
    except Exception:
        return render_template('errorGenerico.html', message="Error del servidor al intentar logearse")
         
    finally:
        if cursor:
                cursor.close()
        if conn:
                conn.close()

@usuarios_bp.route('/usuarios/<int:id>', methods=['POST'])

def actualizar_completamente_usuario(id):

    if not request.form:
        flash("No se recibió información en el formulario.")
        return redirect('/panel-usuario'), 400
    
    nombre = request.form.get("nombre")
    numero = request.form.get("numero")
    email = request.form.get("email")

    if not nombre or not numero or not email:
        flash("Faltan datos obligatorios por completar")
        return redirect('/panel-usuario'), 400
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        check_query = """
        SELECT * FROM usuarios WHERE id = %s
        """
        cursor.execute(check_query, (id,))

        usuario = cursor.fetchone()

        if not usuario:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE usuarios SET nombre = %s, numero = %s,
        email = %s WHERE id = %s
        """
        cursor.execute(query, id)
        conn.commit()
        
        flash("Tus datos se actualizaron correctamente", "success")
        return redirect(url_for('usuarios.panel_usuario'))
    
    except Exception :
        return render_template('errorGenerico.html', message='Error al actualizar usuario')
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@usuarios_bp.route('/usuarios/<int:id>', methods=['POST'])

def actualizar_parcialmente_ususario(id):
    
    if id <= 0:
        flash("ID de usuario inválido", "error")
        return render_template('panel_usuario.html'), 400
    
    if not request.form:
        flash("No se recibió información en el formulario.")
        return redirect('/registro'), 400
    
    nombre = request.form.get("nombre")
    numero = request.form.get("numero")
    email = request.form.get("email")
     
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor

        check_query = """
        SELECT * FROM usuarios WHERE id = %s
        """
        cursor.execute(check_query, id)

        usuario = cursor.fetchone

        if not usuario:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        conn = get_connection()
        cursor = conn.cursor()

        campos = []
        valores = []

        if nombre is not None:
            campos.append("nombre = %s")
            valores.append(nombre)

        if numero is not None:
            campos.append("numero = %s")
            valores.append(numero)

        if email is not None:
            campos.append("email = %s")
            valores.append(email)

        if not campos:
            cursor.close()
            conn.close()

            return jsonify({"error": "Bad Request", "message": "no se enviaron campos para actualizar"}), 400
        else:
            query = f"""
            UPDATE usuarios SET {', '. join(campos)} WHERE id = %s
            """
            valores.append(id)

            cursor.execute(query, tuple(valores))
        
        flash("Campos modificados con exito.", "success")
        return redirect(url_for('usuarios.panel_usuario'))

    except Exception :
        return render_template('errorGenerico.html', message='Error al actualizar usuario')
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   
   
@usuarios_bp.route('/usuarios/<id>/eliminar', methods=['POST'])

def eliminarUsuario(id):

    try:

        id = int(id)

        if session.get('rol') != 'admin':

            flash('No tiene permisos para eliminar usuarios')

            return redirect('/') 

        eliminado = eliminarUsuarioPorId(id)

        if not eliminado:

            flash('No existe un usuario con ese ID :(')

            return render_template('errors/404_notFound.html')# -> reemplazo de jsonify por render_template y manejo de errores mediante html reutilizable
        # PD: con fran mantuvimos la estructura asi en reservas.py 

        flash(
            'Usuario eliminado correctamente')

        return redirect(
            url_for('usuarios.adminUsuarios'))

    except ValueError:

        flash('El ID es invalido')

        return render_template('errors/404_notFound.html') 

    except Exception:
        return render_template('errorGenerico.html', message='Error al eliminar usuario')
        
        
         
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
    
