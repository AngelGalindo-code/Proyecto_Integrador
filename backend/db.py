import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="roundhouse.proxy.rlwy.net",
        user="root",
        password="FUibWHMPCpWeDRAoHRstKuBpPAuwNPPA",
        database="restaurante",
        port=31261
    )