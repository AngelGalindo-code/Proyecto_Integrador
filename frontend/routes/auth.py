from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from constantes import URL_BACKEND
import logging
import requests

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET'])
def mostrar_login():
    return render_template('formulario_login.html')


@auth_bp.route('/registro', methods=['GET'])
def mostrar_registro():
    return render_template('formulario_registro.html')


@auth_bp.route("/login", methods=["POST"])

def iniciar_sesion():
    if request.method == "POST":

        nombre = request.form.get("unombre", "").strip()
        email = request.form.get("uemail", "").strip()

        if not nombre or not email:
            flash("Nombre o email no ingresados", "error")
            return redirect(url_for("auth.iniciar_sesion"))
    
        resultado = obtener_usuario(nombre, email)

        if not resultado:
            flash("Usuario o email incorrecto", "error")
            return redirect(url_for("auth.iniciar_sesion"))
        
        session['token'] = resultado['token']
        session['usuario'] = resultado['usuario']

        flash(f"¡Bienvenido de nuevo, {resultado['usuario']['nombre']}!", "success")
        return redirect(url_for('home'))

    return render_template("formulario_login.html")

@auth_bp.route('/logout')
def logout():
    session.clear() 
    flash("Sesion cerrada correctamente")
    return redirect(url_for('home'))

@auth_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    if not request.form:
        flash("No se recibio informacion en el formulario.", "error")
        return redirect(url_for('auth.mostrar_registro'))

 
    nombre = request.form.get("unombre")
    email = request.form.get("uemail")
    numero = request.form.get("utelefono") 

    
    if not nombre or not numero or not email:
        flash("Faltan datos obligatorios por completar", "error")
        return redirect(url_for('auth.mostrar_registro'))
    
   
    if len(str(nombre).strip()) == 0 or not numero.isdigit() or '@' not in email:
        flash("Formatos de campos invalidos", "error")
        return redirect(url_for('auth.mostrar_registro'))
    
    try: 
        payload = {"nombre": nombre, "numero": numero, "email": email}
        respuesta = requests.post(f"{URL_BACKEND}/usuarios", json=payload)

        if respuesta.status_code == 409:
            flash("Este email ya esta registrado.", "error")
            return redirect(url_for('auth.mostrar_registro'))

        if respuesta.status_code == 201:
            flash("Usuario creado con exito", "success")
            return redirect(url_for('auth.mostrar_login'))
        
        flash("No se pudo crear el usuario", "error")
        return redirect(url_for('auth.mostrar_registro'))
    
    except Exception:
        return render_template('errorGenerico.html', message="Error del servidor al intentar crear el usuario")

def obtener_usuario(nombre, email):
    try:
        response = requests.post(
            f"{URL_BACKEND}/usuarios/login",
            json={"usuario": nombre, "email": email},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return {"token": data["token"], "usuario": data["usuario"]}

        return {}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")
        return {}
    except Exception as e:
        logger.error(f"Error inesperado al hacer login: {e}")
        return {}