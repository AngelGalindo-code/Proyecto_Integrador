from flask import Blueprint, render_template, request, redirect, url_for, flash, session

admin_bp = Blueprint("admin", __name__)

@admin_bp.route('/admin/usuarios/<id>/eliminar', methods=['POST'])

def eliminarUsuario(id):

    try:

        id = int(id)

        if session.get('rol') != 'admin':

            flash('No tiene permisos para eliminar usuarios')

            return redirect('/') 

        eliminado = eliminarUsuarioPorId(id)

        if not eliminado:

            flash('No existe un usuario con ese ID :(')

            return render_template('errors/404_notFound.html')# -> reemplazo de jsonify por render_template y manejo de errores mediante html reutilizable
        # PD: con fran mantuvimos la estructura asi en reservas.py 

        flash(
            'Usuario eliminado correctamente')

        return redirect(
            url_for('usuarios.adminUsuarios'))

    except ValueError:

        flash('El ID es invalido')

        return render_template('errors/404_notFound.html') 

    except Exception:
        return render_template('errorGenerico.html', message='Error al eliminar usuario')
        
        
         
@admin_bp.route('/admin/usuarios', methods=['GET'])

def adminUsuarios():

    try:

        if session.get('rol') != 'admin':

            flash('Acceso denegado')

            return redirect('/')

        usuarios = getUsuarios()

        if not usuarios:

            flash('No hay usuarios registrados')

            return render_template('errors/sinusuarios.html')

        return render_template('adminUsuarios.html', title='Usuarios',usuarios=usuarios)

    except Exception:
        return render_template('errorGenerico.html',message='Error al obtener usuarios')       
        
        
        
            
@admin_bp.route('/admin/usuarios/<int:id>', methods=['GET'])

def adminUsuarioPorId(id):

    try:

        id = int(id)

        if session.get('rol') != 'admin':

            flash('Acceso denegado')

            return redirect('/')

        usuario = getUsuarioPorId(id)

        if not usuario:

            flash('El usuario no fue encontrado')

            return render_template('errors/404_notFound.html')

        return render_template('adminUsuario.html',title='Usuario', usuario=usuario)

    except ValueError:

        flash('El ID es invalido')

        return render_template('errors/404_notFound.html')

    except Exception:
        return render_template('errorGenerico.html', message='Error al obtener el usuario')
    