from flask import Blueprint, render_template, request, redirect, url_for, flash, session

login_bp = Blueprint("formulario_login", __name__)

@login_bp.route("/", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":

        nombre = request.form.get("unombre", "").strip()
        email = request.form.get("uemail", "").strip()

        if not nombre or not email:
            flash("Nombre o email no ingresados", "error")

        resultado = obtener_usuario(nombre, email)

        if not resultado:
            flash("Usuario o email incorrecto", "error")

        flash(f"¡Bienvenido de nuevo, {resultado['usuario']['nombre']}!", "success")