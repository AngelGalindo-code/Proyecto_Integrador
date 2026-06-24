import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 10599)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl={"ssl_ca": "certificates/ca.pem"},
            cursorclass = DictCursor
        )
        return connection
        
    except pymysql.MySQLError as e:
        print(f" Error al conectar a MySQL en Aiven: {e}")
        return e