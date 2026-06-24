from flask import Flask, session, render_template, redirect, url_for
from flask_mail import Mail  # Configuración del servidor de correos
from dotenv import load_dotenv 
import os
import requests
from constantes import URL_BACKEND

# Cargamos las variables del archivo .env al sistema operativo
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

# Configuración del servidor de correos (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # Tu correo de Gmail
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")  # Tu Contraseña de Aplicación
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

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
    platos_dinamicos = []

    try:
        parametros = {"disponible": "true"}
        respuesta = requests.get(f"{URL_BACKEND}/platos", params=parametros, timeout=5)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            platos_dinamicos = datos.get("platos", []) 
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el backend: {e}")

    return render_template(
        'home.html', 
        menu={'comidas': platos_dinamicos}, 
        resenas=resenas_del_home, 
        activar_resena=estado_reserva_usuario
    )

if __name__ == '__main__':
    app.run(debug=True, port=8080)