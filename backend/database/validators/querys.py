SQL_BASE_RESERVAS = """
    SELECT 
        r.id_reservas    AS id_reserva,
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
    WHERE id_reserva = :id_reserva;
"""
UPDATE_SQL = """
    UPDATE reservas
    SET nombre = :nombre,
        fecha = :fecha,
        mesa = :mesa,
        cantidad_personas = :cantidad_personas
    WHERE id_reserva = :id_reserva;
"""

# Falta agregar DELETE