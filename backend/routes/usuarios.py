from flask import Blueprint, render_template, request, redirect, url_for, flash, session


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
        
        existe = obtener_usuario_por_email(cursor, email)

        if existe:
                flash("Este email ya está registrado.", "error")
                return render_template('registro.html')

        insertar_usuario(cursor, nombre, numero, email)
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

        usuario = obtener_usuario_por_email(cursor, email)

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

    if id <= 0:
        flash("ID de usuario invalido", "error")
        return render_template('panel_usuario.html'), 400
    
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

        usuario = obtener_usuario_por_id(cursor, id)

        if not usuario:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        conn = get_connection()
        cursor = conn.cursor()

        actualizar_usuario_completo(cursor, id, nombre, numero, email)
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
        flash("ID de usuario invalido", "error")
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

        actualizar_usuario_parcial(cursor, id, campos_a_editar)
        conn.commit()

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
    
