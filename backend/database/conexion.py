import os
import pymysql
from pymysql.cursors import DictCursor #devuelve datos en forma de diccionarios clave valor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        # desde .env obtenemos el host de la base de datos (puede ser 'db' para docker o un host externo)
        host = os.getenv("DB_HOST")
        
        config = {
            "host": host,
            "port": int(os.getenv("DB_PORT", 3306)),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "cursorclass": DictCursor
        }

        # usamos SSL solo si estamos en un entorno externo
        if host != "db":
            config["ssl"] = {"ssl_ca": "certificates/ca.pem"}

        connection = pymysql.connect(**config)
        return connection
        
    except pymysql.MySQLError as e:
        print(f"Error al conectar a MySQL: {e}")
        return None