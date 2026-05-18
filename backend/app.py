from flask import Flask

from routes.platos import platos_bp

app = Flask(__name__)

app.register_blueprint(platos_bp)

if __name__ == "__main__":
    app.run(port=8080, debug=True)