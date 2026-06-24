from flask import Flask, render_template, redirect, url_for
from dotenv import load_dotenv 
import os
import requests
from constantes import URL_BACKEND

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
    resenas_del_home = {} 
    platos_dinamicos = []

    try:
        parametros = {"disponible": "true"}
        respuesta = requests.get(f"{URL_BACKEND}/platos", params=parametros, timeout=5)
        
        if respuesta.status_code == 200:
            platos_dinamicos = respuesta.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el backend para buscar a los platos: {e}")

    return render_template('home.html', menu={'comidas': platos_dinamicos}, resenas=resenas_del_home)