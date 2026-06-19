from database.queries import *
from database.conexion import get_connection
from pymysql import Error

def obtener_usuario_por_email(cursor, email):
    cursor.execute(OBTENER_USUARIO_POR_EMAIL, (email,))
    return cursor.fetchone()  

def obtener_usuario_por_id(cursor, id_usuario):
    cursor.execute(OBTENER_USUARIO_POR_ID, (id_usuario,))
    return cursor.fetchone()

def insertar_usuario(cursor, nombre, numero, email, rol="usuario"):
    cursor.execute(INSERTAR_USUARIO, (nombre, numero, email, rol))

def actualizar_usuario_completo(cursor, id_usuario, nombre, numero, email):
    cursor.execute(ACTUALIZAR_USUARIO_COMPLETO, (nombre, numero, email, id_usuario))

def actualizar_usuario_parcial(cursor, id_usuario, campos_actualizar):
   
    campos = []
    valores = []

    for clave, valor in campos_actualizar.items():
        campos.append(f"{clave} = %s")
        valores.append(valor)

    query = f"""
    UPDATE usuarios 
    SET {', '.join(campos)} 
    WHERE id = %s
    """
    valores.append(id_usuario)
    cursor.execute(query, tuple(valores))

def getUsuarios():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True) 
    try:
        cursor.execute("SELECT id, nombre, email, rol FROM usuarios")
        usuarios = cursor.fetchall()
        return usuarios
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

def getUsuarioPorId(id_usuario):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (id_usuario,))
        usuario = cursor.fetchone() 
        return usuario
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

def eliminarUsuarioPorId(id_usuario):
    conexion = get_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
        conexion.commit()
       
        return cursor.rowcount > 0 
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()