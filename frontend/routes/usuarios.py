import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from constantes import URL_BACKEND

from routes.reseñas import obtener_resena_id

usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route('/perfil', methods=['GET'])
def perfil_usuario():
    
    if 'usuario' not in session or 'token' not in session:
        return redirect(url_for('auth.mostrar_login'))

    user_actual = session['usuario']
    token = session['token'] 
    
    #Configurar las cabeceras con el token para el Backend
    autorizacion_headers= {
        "Authorization": f"Bearer {token}"
    }
    
    datos_ranking = {}
    lista_reservas = []
    lista_resenas = obtener_resena_id(user_actual['id'])
    
    try:

        respuesta_ranking = requests.get(f"{URL_BACKEND}/usuarios/{user_actual['id']}/ranking", headers=autorizacion_headers, timeout=5)
        if respuesta_ranking.status_code == 200:
            datos_ranking = respuesta_ranking.json()

        respuesta_reservas = requests.get(f"{URL_BACKEND}/usuarios/{user_actual['id']}/reservas", headers=autorizacion_headers, timeout=5)
        if respuesta_reservas.status_code == 200:
            lista_reservas = respuesta_reservas.json()

            for reserva in lista_reservas:
                # el HTML busca "id_reserva", pero la base de datos devuelve "id" o "id_reserva"
                if 'id_reserva' not in reserva and 'id' in reserva:
                    reserva['id_reserva'] = reserva['id']
            
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con los servicios del backend: {e}")
        
    return render_template('panel_usuario.html', usuario=user_actual, ranking=datos_ranking, reservas=lista_reservas, resenas=lista_resenas)

@usuarios_bp.route('/perfil/editar', methods=['GET'])

def mostrar_formulario_editar():
    if 'usuario' not in session:
        return redirect(url_for('auth.mostrar_login'))
        
    return render_template('panel_usuario.html', usuario=session['usuario'], editar=True)

@usuarios_bp.route('/perfil/editar', methods=['POST'])

def actualizar_parcialmente_usuario():
    if 'usuario' not in session:
        return redirect(url_for('auth.mostrar_login'))
        
    id = session['usuario']['id']
    
    if id <= 0:
        flash("ID de usuario invalido", "error")
        return render_template('panel_usuario.html'), 400
    
    if not request.form:
        flash("No se recibio informacion en el formulario.", "error")
        return redirect(url_for('usuarios.perfil_usuario')), 400
    
    # Armamos el payload solo con los campos que el usuario relleno
    campos_a_editar = {}
    if request.form.get("nombre"): 
        campos_a_editar["nombre"] = request.form.get("nombre")
    if request.form.get("numero"): 
        campos_a_editar["numero"] = request.form.get("numero")
    if request.form.get("email"): 
        campos_a_editar["email"] = request.form.get("email")

    if not campos_a_editar:
        flash("No se ingresaron modificaciones.", "error")
        return redirect(url_for('usuarios.perfil_usuario'))

    try:
        respuesta = requests.post(f"{URL_BACKEND}/usuarios/{id}", json=campos_a_editar)

        if respuesta.status_code == 404:
            flash('El usuario no fue encontrado', "error")
            return render_template('errors/404_notFound.html')
        
        if respuesta.status_code == 200:
            session['usuario'].update(campos_a_editar)
            session.modified = True
            
            flash("Campos modificados con exito.", "success")
            return redirect(url_for('usuarios.perfil_usuario'))

        flash("No se pudo actualizar el usuario", "error")
        return redirect(url_for('usuarios.perfil_usuario'))
    
    except Exception:
        return render_template('errorGenerico.html', message='Error al actualizar usuario parcialmente')