from flask import Flask, session, render_template, redirect, url_for
from dotenv import load_dotenv 
import os

# Cargamos las variables del archivo .env al sistema operativo
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

from routes.auth import auth_bp
from routes.usuarios import usuarios_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp
from routes.reseñas import resenas_bp
from routes.categoria import categoria_bp
from routes.platos import platos_bp

from routes.reseñas import resenas_destacadas, obtener_estado_resena

app.secret_key = os.getenv("SECRET_KEY", "clave_de_desarrollo_local")

app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(resenas_bp)
app.register_blueprint(categoria_bp)
app.register_blueprint(platos_bp)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    usuario_sesion = session.get("usuario")
    
    if usuario_sesion:
        id_usuario = usuario_sesion.get("id")
        estado_reserva_usuario = obtener_estado_resena(id_usuario)
    else:
        id_usuario = None
        estado_reserva_usuario = False

    resenas_del_home = resenas_destacadas()

    return render_template(
        'home.html', 
        menu={'comidas': []}, 
        resenas=resenas_del_home, 
        activar_resena=estado_reserva_usuario
    )
if __name__ == '__main__':
    app.run(debug=True, port=8080)
