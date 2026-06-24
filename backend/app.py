from flask import Flask
from flask_cors import CORS  

from routes.categorias import categorias_bp
from routes.platos import platos_bp
from routes.ranking_usuarios import ranking_usuarios_bp as ranking_bp
from routes.reseñas import reseñas_bp
from routes.reservas import reservas_bp
from routes.usuarios import usuarios_bp

app = Flask(__name__)
CORS(app) 

app.register_blueprint(categorias_bp, url_prefix='/categorias')
app.register_blueprint(platos_bp, url_prefix='/platos')
app.register_blueprint(ranking_bp)
app.register_blueprint(reseñas_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(usuarios_bp)

if __name__ == '__main__':
    app.run(debug=True, port=10599)