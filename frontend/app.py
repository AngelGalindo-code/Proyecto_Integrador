from flask import Flask, render_template, Blueprint
from dotenv import load_dotenv 
import os

# Cargamos las variables del archivo .env al sistema operativo
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

from routes.usuarios import usuarios_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp

app.secret_key = os.getenv("SECRET_KEY", "clave_de_desarrollo_local")

app.register_blueprint(reservas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
