from flask import Blueprint, render_template, request, redirect, url_for, flash, session

login_bp = Blueprint("formulario_login", __name__)

@login_bp.route("/", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":

        nombre = request.form.get("unombre", "").strip()
        email = request.form.get("uemail", "").strip()

        if not nombre or not email:
            flash("Nombre o email no ingresados", "error")
            return redirect(url_for("formulario_login.iniciar_sesion"))
    
        resultado = obtener_usuario(nombre, email)

        if not resultado:
            flash("Usuario o email incorrecto", "error")
            return redirect(url_for("formulario_login.iniciar_sesion"))
        
        session['token'] = resultado['token']
        session['usuario'] = resultado['usuario']

        flash(f"¡Bienvenido de nuevo, {resultado['usuario']['nombre']}!", "success")
        return redirect(url_for("principal.pagina_principal"))

    return render_template("formulario_login.html")