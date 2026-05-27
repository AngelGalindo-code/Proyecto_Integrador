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
    WHERE fecha = %s AND mesa = %s AND hora = %s.
"""

# Falta hora en la BBDD
