import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from constantes import URL_BACKEND

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route('/usuario/perfil', methods=['GET'])
def perfil_usuario():
    
    if 'usuario' not in session or 'token' not in session:
        return redirect(url_for('login')) 
    
    user_actual = session['usuario']
    token = session['token'] 
    
    #Configurar las cabeceras con el token para el Backend
    autorizacion_headers= {
        "Authorization": f"Bearer {token}"
    }
    
    datos_ranking = {}
    lista_reservas = []
    lista_resenas = []
    
    try:

        respuesta_ranking = requests.get(f"{URL_BACKEND}/usuarios/{user_actual['id']}/ranking", headers=autorizacion_headers, timeout=5)
        if respuesta_ranking.status_code == 200:
            datos_ranking = respuesta_ranking.json()

        respuesta_reservas = requests.get(f"{URL_BACKEND}/usuarios/{user_actual['id']}/reservas", headers=autorizacion_headers, timeout=5)
        if respuesta_reservas.status_code == 200:
            lista_reservas = respuesta_reservas.json()

        repuestas_resenas = requests.get(f"{URL_BACKEND}/usuarios/{user_actual['id']}/resenas", headers=autorizacion_headers, timeout=5)
        if repuestas_resenas.status_code == 200:
            lista_resenas = repuestas_resenas.json()
            
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con los servicios del backend: {e}")
        
    return render_template('panel_usuario.html', usuario=user_actual, ranking=datos_ranking, reservas=lista_reservas, resenas=lista_resenas)

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
        respuesta = requests.put(f"{URL_BACKEND}/usuarios/{id}", json=payload)

        if respuesta.status_code == 404:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')
        
        if respuesta.status_code == 200:
            flash("Tus datos se actualizaron correctamente", "success")
            return redirect(url_for('usuarios.panel_usuario'))
        
        flash("No se pudo actualizar el usuario")
        return render_template('panel_usuario.html')
    
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
        return render_template('panel_usuario.html')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error al actualizar usuario')
   
