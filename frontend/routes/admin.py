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

    todas_las_reservas = obtener_reservas_backend()

    fecha_actual_str = datetime.now().strftime("%Y-%m-%d")

    reservas_hoy = []
    for reserva in todas_las_reservas:
        # Si la fecha de la reserva coincide con el día de hoy, la guardamos
        if str(reserva.get('fecha')) == fecha_actual_str:
            reservas_hoy.append(reserva)

    total_reservas = len(reservas_hoy)
    total_comensales = 0
    total_cancelaciones = 0

    for reserva in reservas_hoy:
        # Sumamos la cantidad de comensales de forma segura
        cantidad = reserva.get('cantidad_personas', 0)
        total_comensales = total_comensales + int(cantidad)
        
        # Contamos si la reserva fue cancelada
        if reserva.get('estado') == 'cancelado':
            total_cancelaciones = total_cancelaciones + 1

    # Renderizamos el Dashboard enviándole todas las variables limpias
    return render_template(
        'admin_dashboard.html', 
        title='Panel de Administración', 
        lista_usuarios=usuarios,
        lista_reservas_hoy=reservas_hoy,           # Puebla la tabla de reservas activas
        total_reservas_hoy=total_reservas,         # Tarjeta 1
        total_comensales_hoy=total_comensales,     # Tarjeta 2
        total_cancelaciones_hoy=total_cancelaciones # Tarjeta 3
    )
@admin_bp.route('/admin/usuarios/<int:id>/eliminar', methods=['POST'])
def eliminarUsuario(id):

    if session.get('rol') != 'admin':

        flash('No tiene permisos para eliminar usuarios')

        return redirect('/') 
        
    try:
       
        respuesta = requests.delete(f"{URL_BACKEND}/admin/usuarios/{id}", timeout=5)

        if respuesta.status_code == 404:
            flash('El usuario que intenta eliminar no existe')
            return render_template('errors/404_notFound.html')
            
        if respuesta.status_code == 200:
            flash('Usuario eliminado correctamente')
            return redirect(url_for('admin.adminUsuarios'))
            
        return render_template('errorGenerico.html', message='Error al intentar eliminar el usuario en el servidor')

    except Exception:
        return render_template('errorGenerico.html', message='Error inesperado al eliminar usuario')
    

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