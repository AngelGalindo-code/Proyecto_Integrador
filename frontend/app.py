from flask import Flask, render_template, Blueprint
from dotenv import load_dotenv 
import os
from flask_mail import Mail

# Cargamos las variables del archivo .env al sistema operativo
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

from routes.usuarios import usuarios_bp
from routes.admin import admin_bp
from routes.reservas import reservas_bp

app.secret_key = os.getenv("SECRET_KEY", "clave_de_desarrollo_local")

# COnfiguracion para el mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'loshornerosrestaurante@gmail.com' # Modificar 
app.config['MAIL_PASSWORD'] = 'clave' # Contrasenia de google
app.config['MAIL_DEFAULT_SENDER'] = ('Los Horneros', 'loshornerosrestaurante@gmail.com') # Modificar mail de restaurante

mail = Mail(app)

app.register_blueprint(reservas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
