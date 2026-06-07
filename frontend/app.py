from flask import Flask
from dotenv import load_dotenv 
import os

# Cargamos las variables del archivo .env al sistema operativo
load_dotenv()

from routes.usuarios import usuarios_bp
from routes.admin import admin_bp

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "clave_de_desarrollo_local")


app.register_blueprint(usuarios_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True, port=8080)