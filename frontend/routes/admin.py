from flask import Blueprint, render_template, redirect, url_for, flash, session
import requests
from constantes import URL_BACKEND

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/admin', methods=['GET']) 
def panelAdmin():
    
    if session.get('usuario', {}).get('rol') != 'admin':
        flash('Acceso denegado')
        return redirect('/')
        
    return render_template('admin_dashboard.html', title='Panel de Administración')

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
        
         
@admin_bp.route('/admin/usuarios', methods=['GET'])
def adminUsuarios():


    if session.get('rol') != 'admin':

        flash('Acceso denegado')

        return redirect('/')
        
    try:
        respuesta = requests.get(f"{URL_BACKEND}/admin/usuarios", timeout=5)
        
        if respuesta.status_code == 404:
            flash('No hay usuarios registrados')
            return render_template('errors/sinusuarios.html')

        if respuesta.status_code == 200:
            usuarios = respuesta.json()  
            return render_template('adminUsuarios.html', title='Usuarios', usuarios=usuarios)

        return render_template('errorGenerico.html', message='Error al obtener usuarios')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error inesperado al obtener usuarios')       
        
        
@admin_bp.route('/admin/usuarios/<int:id>', methods=['GET'])

def adminUsuarioPorId(id):

    if session.get('rol') != 'admin':

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
        
        return render_template('errorGenerico.html', message='No se pudo procesar la busqueda del usuario')
    
    except Exception:
        return render_template('errorGenerico.html', message='Error inesperado al obtener el usuario')