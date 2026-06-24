from flask import Flask, render_template, redirect, url_for
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
    # diccionario vacio para que no explote
    resenas_del_home = {} 

    return render_template('home.html', menu={'comidas': []}, resenas=resenas_del_home)
if __name__ == '__main__':
    app.run(debug=True, port=8080)
