from flask import Flask, Blueprint, render_template

app = Flask(
    __name__, 
    template_folder='frontend/templates', 
    static_folder='frontend/static'
)

publicas_bp = Blueprint('publicas', __name__)

@publicas_bp.route('/')
def index():
    return render_template('index.html')

@publicas_bp.route('/menu')
def menu():
    return render_template('menu.html')


usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/reserva')
def formulario_reserva():
    return render_template('formulario_reserva.html')

@usuarios_bp.route('/reserva/exito')
def reserva_exito():
    return render_template('reserva_exito.html')

@usuarios_bp.route('/panel-usuario')
def panel_usuario():
    return render_template('panel_usuario.html')


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login')
def formulario_login():
    return render_template('formulario_login.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')