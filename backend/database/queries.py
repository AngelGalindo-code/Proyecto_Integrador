SQL_BASE_RESERVAS = """
    SELECT 
        r.id_reserva     AS id_reserva,
        u.nombre         AS usuario,
        r.id_usuario     AS id_usuario,
        r.fecha          AS fecha,
        r.mesa           AS mesa,
        r.cantidad_personas AS cantidad_personas
    FROM reservas r
    JOIN usuarios u ON r.id_usuario = u.id_usuario
"""

SQL_GET_POR_ID = """
    SELECT id_reserva, nombre, mesa, cantidad_personas, fecha, hora
    FROM reservas
    WHERE id_reserva = %s;
"""

UPDATE_SQL = """
    UPDATE reservas
    SET nombre = %s,
        fecha = %s,
        mesa = %s,
        cantidad_personas = %s
    WHERE id_reserva = %s;
"""
DELETE_SQL = """
    DELETE FROM reservas
    WHERE id_reserva = %s;
"""

MESA_RESERVADA_SQL = """
    SELECT id_reserva 
    FROM reservas 
    WHERE fecha = %s AND mesa = %s AND hora = %s
"""
#usuarios

OBTENER_USUARIO_POR_EMAIL = "SELECT id, nombre, numero, email, rol FROM usuarios WHERE email = %s"

OBTENER_USUARIO_POR_ID = "SELECT id, nombre, numero, email, rol FROM usuarios WHERE id = %s"

LISTAR_TODOS_LOS_USUARIOS = "SELECT id, nombre, email, rol FROM usuarios"

INSERTAR_USUARIO = """
    INSERT INTO usuarios (nombre, numero, email, rol) 
    VALUES (%s, %s, %s, %s)
"""

ELIMINAR_USUARIO_POR_ID = "DELETE FROM usuarios WHERE id = %s"

ACTUALIZAR_USUARIO_COMPLETO = """
    UPDATE usuarios 
    SET nombre = %s, numero = %s, email = %s 
    WHERE id = %s
"""
# Falta hora en la BBDD

# QUERIES RANKING DE USUARIOS

RANKING_OBTENER_TODOS = """
    SELECT u.id, u.nombre, u.email, r.cant_cancelaciones
    FROM ranking_usuarios r
    JOIN usuarios u ON r.id_usuario = u.id
    ORDER BY r.cant_cancelaciones DESC
"""

RANKING_OBTENER_POR_USUARIO = """
    SELECT u.id, u.nombre, u.email, r.cant_cancelaciones
    FROM ranking_usuarios r
    JOIN usuarios u ON r.id_usuario = u.id
    WHERE u.id = %s
"""

RANKING_SUMAR_CANCELACION = """
    INSERT INTO ranking_usuarios (id_usuario, cant_cancelaciones)
    VALUES (%s, 1)
    ON DUPLICATE KEY UPDATE
    cant_cancelaciones = cant_cancelaciones + 1
"""

RANKING_REINICIAR = """
    INSERT INTO ranking_usuarios (id_usuario, cant_cancelaciones)
    VALUES (%s, 0)
    ON DUPLICATE KEY UPDATE
    cant_cancelaciones = 0
"""

RANKING_ELIMINAR_USUARIO = """
    DELETE FROM ranking_usuarios
    WHERE id_usuario = %s
"""

RANKING_OBTENER_USUARIO_RESERVA = """
    SELECT id_usuario
    FROM reservas
    WHERE id_reserva = %s
"""