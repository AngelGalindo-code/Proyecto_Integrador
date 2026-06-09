import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from constantes import URL_BACKEND

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():

    
    if not request.form:
        flash("No se recibio información en el formulario.")
        return redirect('/registro'), 400

    nombre = request.form.get("nombre")
    numero = request.form.get("numero")
    email = request.form.get("email")

    if not nombre or not numero or not email:
        flash("Faltan datos obligatorios por completar")
        return redirect('/registro'), 400
    
    if len(str(nombre).strip()) == 0 or not numero.isdigit() or '@' not in email:
        flash("Formatos de campos invalidos")
        return redirect('/registro'), 400
    
    try: 
        payload = {"nombre": nombre, "numero": numero, "email": email}
        respuesta = requests.post(f"{URL_BACKEND}/api/usuarios", json=payload)

        if respuesta.status_code == 409:
            flash("Este email ya esta registrado.", "error")
            return render_template('formulario_registro.html')

        if respuesta.status_code == 201:
            flash("Usuario creado con exito")
            return redirect(url_for('publicas.index'))
        
        flash("No se pudo crear el usuario")
        return render_template('formulario_registro.html')
    
    except Exception:
        return render_template('errorGenerico.html', message="Error del servidor al intentar crear el usuario")
    
@usuarios_bp.route('/login', methods=['POST'])

def login():
    email = request.form.get("email")

    if email is None:
        flash("No se ingreso ningun email.", "error")
        return render_template('formulario_registro.html')

    try: 
        payload_login = {"email": email}
        respuesta = requests.post(f"{URL_BACKEND}/api/usuarios/login", json=payload_login)

        if respuesta.status_code == 404:
            flash("El usuario no fue encontrado o el email es incorrecto.", "error")
            return render_template('errors/404_notFound.html')
            
        if respuesta.status_code == 200:
            usuario = respuesta.json() 
            
            session["id_usuario"] = usuario.get("id")
            session["rol"] = usuario.get("rol")

            flash(f"Bienvenido, Has ingresado como {usuario.get('rol')}.", "success")
            return redirect(url_for('publicas.index'))
            
        flash("Error de credenciales.", "error")
        return render_template('formulario_login.html')
    
    except Exception:
        return render_template('errorGenerico.html', message="Error del servidor al intentar logearse")
    
@usuarios_bp.route('/usuarios/<int:id>', methods=['POST'])
def actualizar_completamente_usuario(id):
    if id <= 0:
        flash("ID de usuario invalido", "error")
        return render_template('panel_usuario.html'), 400
    
    if not request.form:
        flash("No se recibio informacion en el formulario.")
        return redirect('/panel-usuario'), 400
    
    nombre = request.form.get("nombre")
    numero = request.form.get("numero")
    email = request.form.get("email")

    if not nombre or not numero or not email:
        flash("Faltan datos obligatorios")
        return redirect('/panel-usuario'), 400

    try:
        payload = {"nombre": nombre, "numero": numero, "email": email}
        respuesta = requests.put(f"{URL_BACKEND}/api/usuarios/{id}", json=payload)

        if respuesta.status_code == 404:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        if respuesta.status_code == 200:
            flash("Tus datos se actualizaron correctamente", "success")
            return redirect(url_for('usuarios.panel_usuario'))
        
        flash("No se pudo actualizar el usuario")
        return render_template('panel-usuario.html')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error al actualizar usuario')
    
@usuarios_bp.route('/usuarios/<int:id>', methods=['POST'])

def actualizar_parcialmente_ususario(id):
    
    if id <= 0:
        flash("ID de usuario invalido", "error")
        return render_template('panel_usuario.html'), 400
    
    if not request.form:
        flash("No se recibio informacion en el formulario.")
        return redirect('/panel-usuario'), 400
    
    campos_a_editar = {}

    if request.form.get("nombre"): campos_a_editar["nombre"] = request.form.get("nombre")
    if request.form.get("numero"): campos_a_editar["numero"] = request.form.get("numero")
    if request.form.get("email"): campos_a_editar["email"] = request.form.get("email")

    try:
        respuesta = requests.patch(f"{URL_BACKEND}/api/usuarios/{id}", json=campos_a_editar)

        if respuesta.status_code == 404:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        if respuesta.status_code == 200:
            flash("Campos modificados con exito.", "success")
            return redirect(url_for('usuarios.panel_usuario'))

        
        flash("No se pudo actualizar el usuario")
        return render_template('panel-usuario.html')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error al actualizar usuario')
   
