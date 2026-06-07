def obtener_usuario_por_email(cursor, email):
    query = "SELECT id, rol FROM usuarios WHERE email = %s"
    cursor.execute(query, (email,))
    return cursor.fetchone()  


def obtener_usuario_por_id(cursor, id_usuario):
    query = "SELECT id, nombre, numero, email, rol FROM usuarios WHERE id = %s"
    cursor.execute(query, (id_usuario,))
    return cursor.fetchone()


def insertar_usuario(cursor, nombre, numero, email, rol="usuario"):
    query = """
    INSERT INTO usuarios (nombre, numero, email, rol) 
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (nombre, numero, email, rol))


def actualizar_usuario_completo(cursor, id_usuario, nombre, numero, email):
    query = """
    UPDATE usuarios 
    SET nombre = %s, numero = %s, email = %s 
    WHERE id = %s
    """
    cursor.execute(query, (nombre, numero, email, id_usuario))


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