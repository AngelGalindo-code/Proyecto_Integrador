from flask import Flask, render_template, Blueprint, flash, request, redirect, url_for, abort, session 
from decorators.decorators import adminRequired, loginRequired
import requests 
from constantes import URL_BACKEND

platos_bp = Blueprint("platos", __name__)
apiBackend = requests.Session()

# Consultar por los server error en la parte backend
@platos_bp.errorhandler(405)
def method_not_allowed(e):

    return render_template('400.html'), 405

@platos_bp.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500_serverError.html'), 500

@platos_bp.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404_notFound.html'), 404

@platos_bp.errorhandler(403)
def acces_forbidden(e):
    return render_template('errors/403_forbidden.html'), 403

@platos_bp.errorhandler(400)
def bad_request(e):
    return render_template('errors/400_badRequest.html'), 400

@platos_bp.route('/admin/platos/crear', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def crearPlato():

    if request.method == 'GET':
        return render_template('platos/formularioCrearPlato.html')
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        precio = request.form.get('precio', '').strip()
        idCategoria = request.form.get('id_categoria', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        disponible = request.form.get("disponible", "0")



        if not all([nombre, precio, idCategoria]):
            flash("Complete los campos obligatorios", "error")
            return redirect("/admin/dashboard")

        try:
            payload = {
                "nombre": nombre,
                "precio": float(precio),
                "id_categoria": int(idCategoria),
                "descripcion": descripcion if descripcion else None,
                "disponible": True if disponible == "1" else False
            }
            respuesta = requests.post(f"{URL_BACKEND}/platos/platos", json=payload, timeout=5)

            if respuesta.status_code == 201:
                flash("Plato agregado con exito", "success")
            elif respuesta.status_code == 400:
                data = respuesta.json()
                message = data.get("errors", [{}])[0].get("description", "datos invalidos")
                flash(message, "error")
            else:
                flash("Error al crear el plato", "error")

        except (requests.exceptions.RequestException, ValueError):
            flash("No se pudo conectar con el servidor", "error")
        
        return redirect(url_for('admin.panelAdmin'))
    
@platos_bp.route('/admin/platos/editar', methods=['POST'])
@loginRequired
@adminRequired
def editarPlato():
        id_plato = request.form.get("id_plato")
        nombre_nuevo = request.form.get("nombre", "").strip()
        id_categoria_nuevo = request.form.get("id_categoria", "").strip()
        precio_nuevo = request.form.get("precio", "").strip()
        disponible_nuevo = request.form.get("disponible", "").strip()
        descrip_nuevo = request.form.get("descripcion", "").strip()

        if not id_plato:
            flash("Seleccione el plato a editar")
            return redirect ("/admin/dashboard")
        
        payload = {}
        if nombre_nuevo:
            payload["nombre"] = nombre_nuevo
        if id_categoria_nuevo:
            payload["id_categoria"] = id_categoria_nuevo
        if precio_nuevo:
            payload["precio"] = precio_nuevo
        if disponible_nuevo:
            payload["disponible"] = disponible_nuevo
        if descrip_nuevo:
            payload["descripcion"] = descrip_nuevo

        try:
            respuesta = requests.post(f"{URL_BACKEND}/platos/{id_plato}/editar", json=payload, timeout=5)
            
            if respuesta.status_code == 200:
                flash("Plato editado con exito", "success")
                return redirect(url_for('admin.panelAdmin'))
            elif respuesta.status_code == 400:
                data =  respuesta.json()
                message = data.get("errors", [{}])[0].get("descripcion", "Datos invalidos")
                flash(message, "error")
            else:
                flash("Error inesperado", "error")
                
        except (requests.exceptions.RequestException, ValueError):
            flash("No se pudo conectar con el servidor", "error")
        return redirect(url_for('admin.panelAdmin'))
    
@platos_bp.route('/admin/platos', methods=['GET'])
@adminRequired  # Tu decorador para que solo el admin lo vea
def listarPlatosAdmin():
    try:

        respuesta = apiBackend.get(f"{URL_BACKEND}/platos", timeout=5)

        if respuesta.status_code == 200:
            lista_platos = respuesta.json()
            
            return render_template('listaPlatosAdmin.html', platos=lista_platos)
        
        elif respuesta.status_code == 404:
            abort(404)
        else:
            abort(500)

    except requests.exceptions.RequestException:
        abort(500)

@platos_bp.route('/menu', methods=['GET']) # Menu/Carta -> Lo pueden ver todos
def listarPlatos():
    parametros = {
        "disponible": "true" # Para que solo aparezcan los que estan disponibles
    }

    try:
        respuesta = apiBackend.get(f"{URL_BACKEND}/platos", params=parametros, timeout=5)

        if respuesta.status_code == 200:
            cartaPlatos = respuesta.json()
            
            return render_template('menuClientes.html', platos=cartaPlatos)
        
        else:
            abort(500)

    except requests.exceptions.RequestException:
        abort(500)


@platos_bp.route('/admin/eliminar/plato', methods=['POST'])
@loginRequired
@adminRequired  
def eliminarPlato():
    
    id_plato = request.form.get("id_plato")
    if not id_plato:
        flash("Seleccione el plato")
        return redirect("/admin/dashboard")
    
    payload = {"id_plato": int(id_plato)}

    try:
        respuesta = requests.post(f"{URL_BACKEND}/platos/admin/eliminar", json=payload)

        if respuesta.status_code == 204:
            flash("El plato se elimino", "success")
            return redirect(url_for('admin.panelAdmin'))
        
        elif respuesta.status_code in [400, 404, 409]:
            data = respuesta.json()
            message = data.get("errors", [{}])[0].get("description", "No se pudo eliminar")
            flash(message, "error")
        else:
            flash("Error al eliminar", "error")

    except requests.exceptions.RequestException:
        flash("No se pudo conectar con el servidor", "error")

    return redirect(url_for('admin.panelAdmin'))

@platos_bp.route('/admin/platos/buscar', methods=['GET', 'POST'])
@adminRequired  
def buscarPlatoPorId():
    if request.method == 'GET':
        return render_template('buscadorAdmin.html', plato=None)

    if request.method == 'POST':
        idIngresado = request.form.get('id_plato', '').strip()

        if not idIngresado:
            abort(400)

        try:
            idEntero = int(idIngresado)

            if idEntero <= 0:
                abort(400)

            urlBusqueda = f"{URL_BACKEND}/platos/{idEntero}"
            respuesta = apiBackend.get(urlBusqueda, timeout=5)

            if respuesta.status_code == 200:
                platoEncontrado = respuesta.json()

                return render_template('buscadorAdmin.html', plato=platoEncontrado)
            
            elif respuesta.status_code == 404:
                abort(404)
            else:
                abort(500)

        except (requests.exceptions.RequestException, ValueError):
            abort(400)