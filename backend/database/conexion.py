import os
import pymysql
from pymysql.cursors import DictCursor #devuelve datos en forma de diccionarios clave valor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Establece la conexion con el servidor MySQL de Aiven en la nube
    utilizando SSL obligatorio. 
    """
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 10599)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl={"ssl_ca": "certificates/ca.pem"},    # activa el modo SSL obligatorio que pide Aiven
            cursorclass = DictCursor
        )

        return connection
        
    except pymysql.MySQLError as e:
        print(f" Error al conectar a MySQL en Aiven: {e}")
        return e
