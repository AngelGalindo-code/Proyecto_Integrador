from flask import Blueprint, request, flash, render_template,redirect, url_for
from decorators.decorators import adminRequired, loginRequired
from constantes import URL_BACKEND
import requests

categoria_bp = Blueprint("categoria", __name__)



@categoria_bp.route("/admin", methods=["POST"])
@loginRequired
@adminRequired
def crearCategoria():
    nombre_categoria = request.form.get("nombre_categoria")

    if not nombre_categoria or not nombre_categoria.strip():
        flash("Indique el nombre de la categoria")
        return render_template("admin_dashboard.html")
    
    try:
        response = requests.post(f"{URL_BACKEND}/admin", json = {"nombre_categoria": nombre_categoria.strip()})
        if response.status_code == 201:
            flash("La categoria se creo", "success")

        elif response.status_code in [400, 409]:
            data = response.json()
            message = data.get("errors", [{}])[0].get("description", "datos invalidos")
            flash(message, "error")

        else:
            flash("Ocurrio un error inespertado", "error")

    except request.exception.RequestException:
        flash("No se pudo conectar con el servidor", "error")

    return redirect(url_for("admin.panelAdmin"))



@categoria_bp.route("/admin/categoria/editar", methods=["POST"])
@loginRequired
@adminRequired
def editarCategoria():

    id_cat = request.form.get("id_categoria")
    nuevo_nombre = request.form.get("nombre_categoria")

    if not nuevo_nombre or not nuevo_nombre.strip():
        flash("Indique el nuevo nombre", "error")
        return redirect(url_for("admin.panelAdmin"))
    
    payload = {"id_categoria": int(id_cat), "nombre_categoria": nuevo_nombre.strip()}

    try:
        response = requests.post(f"{URL_BACKEND}/admin/editar", json = payload)

        if response.status_code == 204:
            flash("Categoria modificada", "success")

        elif response.status_code in [400,404,409]:
            data = response.json()
            message = data.get("errors", [{}])[0].get("description", "No se pudo editar")
            flash(message, "error")

        else:
            flash("Error inesperado al modificar", "error")

    except request.exception.RequestException:
        flash("No se pudo conectar con el servidor", "error")

    return redirect(url_for("admin.panelAdmin"))



@categoria_bp.route("/admin/categoria/eliminar", methods=["POST"])
@loginRequired
@adminRequired
def eliminarCategoria():

    id_cat = request.form.get("id_categoria")

    payload = {"id_categoria": int(id_cat)}

    try:
        response = requests.post(f"{URL_BACKEND}/admin/eliminar", json = payload)

        if response.status_code == 204:
            flash("La categoria se elimino", "success")
            
        elif response.status_code in [400, 404, 409]:
            data = response.json()
            message = data.get("errors",[{}])[0].get("descripcion", "No se puedo eliminar")
            flash(message, "error")
            
        else:
            flash("Error al eliminar", "error")

    except request.exception.RequestException:
        flash("No se pudo conectar con el servidor", "error")   

    return redirect(url_for("admin.panelAdmin"))