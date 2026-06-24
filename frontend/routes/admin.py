from flask import Blueprint, render_template, redirect, url_for, flash, session
import requests
from constantes import URL_BACKEND
from routes.reservas import obtener_reservas_backend
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/admin', methods=['GET']) 
def panelAdmin():
    if session.get('usuario', {}).get('rol') != 'admin':
        flash('Acceso denegado')
        return redirect('/')
        
    usuarios = [] 
    try:
        respuesta = requests.get(f"{URL_BACKEND}/admin/usuarios", timeout=5)
        if respuesta.status_code == 200:
            usuarios = respuesta.json()
    except Exception as e:
        print("Error al conectar con el backend:", str(e))

    categorias = []
    try:
        res_cat = requests.get(f"{URL_BACKEND}/nombres", timeout=5)
        if res_cat.status_code == 200:
            categorias = res_cat.json().get("categoria", [])
    except Exception as e:
        print("Error al conectar con el backend (categorías):", str(e))

    # 📥 Traemos el universo completo de reservas
    todas_las_reservas = obtener_reservas_backend()

    fecha_actual_str = datetime.now().strftime("%Y-%m-%d")

    # Calculamos las métricas de HOY para los contadores superiores
    total_reservas_hoy = 0
    total_comensales_hoy = 0
    total_cancelaciones_hoy = 0

    for reserva in todas_las_reservas:
        if str(reserva.get('fecha')) == fecha_actual_str:
            total_reservas_hoy += 1
            cantidad = reserva.get('cantidad_personas', 0)
            total_comensales_hoy += int(cantidad)
            if reserva.get('estado') == 'cancelado':
                total_cancelaciones_hoy += 1

    ranking_usuarios = []
    platos = []

    # Renderizamos el Dashboard enviándole TODO el listado a la tabla
    return render_template(
        'admin_dashboard.html', 
        title='Panel de Administración', 
        lista_usuarios=usuarios,
        categorias=categorias,                     
        lista_reservas_hoy=todas_las_reservas, # 🌟 CAMBIO CLAVE: Mandamos la lista completa
        total_reservas_hoy=total_reservas_hoy,
        total_comensales_hoy=total_comensales_hoy,
        total_cancelaciones_hoy=total_cancelaciones_hoy,
        ranking_usuarios=ranking_usuarios,  
        platos=platos                        
    )

@admin_bp.route('/admin/usuarios/<int:id>', methods=['POST'])
def eliminarUsuario(id):
   
    if session.get('usuario', {}).get('rol') != 'admin':
        flash('No tiene permisos para eliminar usuarios')
        return redirect('/') 
        
    try:
        respuesta = requests.post(f"{URL_BACKEND}/admin/usuarios/{id}", timeout=5)

        if respuesta.status_code == 404:
            flash('El usuario que intenta eliminar no existe')
            return render_template('errors/404_notFound.html')
            
        if respuesta.status_code == 200:
            flash('Usuario eliminado correctamente')
            return redirect(url_for('admin.panelAdmin'))
            
        flash('Error al intentar eliminar el usuario en el servidor.', 'danger')
        return redirect(url_for('admin.panelAdmin'))

    except Exception as e:
        print(f"Error inesperado al eliminar: {str(e)}")
        flash('Ocurrió un error inesperado al intentar procesar la baja.', 'danger')
        return redirect(url_for('admin.panelAdmin'))
    

@admin_bp.route('/admin/usuarios/<int:id>', methods=['GET'])
def adminUsuarioPorId(id):
    
    if session.get('usuario', {}).get('rol') != 'admin': 
        flash('Acceso denegado')
        return redirect('/')
        
    try:
        respuesta = requests.get(f"{URL_BACKEND}/admin/usuarios/{id}", timeout=5)

        if respuesta.status_code == 404:
            flash('El usuario no fue encontrado')
            return render_template('errors/404_notFound.html')

        if respuesta.status_code == 200:

            usuario = respuesta.json()
            return render_template('adminUsuario.html', title='Usuario', usuario=usuario)
        
        return render_template('errorGenerico.html', message='No se pudo procesar la búsqueda del usuario')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error inesperado al obtener el usuario')