from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tu_contraseña",
        database="Restaurante"
    )

def ejecutar(sql, datos=(), fetch=False):
    con = conectar()
    cur = con.cursor(dictionary=True)
    cur.execute(sql, datos)

    resultado = cur.fetchall() if fetch else None

    con.commit()
    cur.close()
    con.close()

    return resultado


@app.route("/admin/usuarios/ranking", methods=["GET"])
def ver_ranking():
    ranking = ejecutar("""
        SELECT u.id, u.nombre, u.email, r.cant_cancelaciones
        FROM ranking_usuarios r
        JOIN usuarios u ON r.id_usuario = u.id
        ORDER BY r.cant_cancelaciones DESC
    """, fetch=True)

    return jsonify(ranking)


@app.route("/admin/usuarios/<int:id_usuario>/ranking", methods=["GET"])
def ver_ranking_usuario(id_usuario):
    usuario = ejecutar("""
        SELECT u.id, u.nombre, u.email, r.cant_cancelaciones
        FROM ranking_usuarios r
        JOIN usuarios u ON r.id_usuario = u.id
        WHERE u.id = %s
    """, (id_usuario,), fetch=True)

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    return jsonify(usuario[0])


@app.route("/usuarios/<int:id_usuario>/ranking/cancelacion", methods=["PUT"])
def sumar_cancelacion(id_usuario):
    ejecutar("""
        INSERT INTO ranking_usuarios (id_usuario, cant_cancelaciones)
        VALUES (%s, 1)
        ON DUPLICATE KEY UPDATE
        cant_cancelaciones = cant_cancelaciones + 1
    """, (id_usuario,))

    return jsonify({"mensaje": "Cancelación registrada"})


@app.route("/admin/usuarios/<int:id_usuario>/ranking/reiniciar", methods=["PUT"])
def reiniciar_ranking(id_usuario):
    ejecutar("""
        INSERT INTO ranking_usuarios (id_usuario, cant_cancelaciones)
        VALUES (%s, 0)
        ON DUPLICATE KEY UPDATE
        cant_cancelaciones = 0
    """, (id_usuario,))

    return jsonify({"mensaje": "Ranking reiniciado"})


@app.route("/admin/usuarios/<int:id_usuario>/ranking", methods=["DELETE"])
def eliminar_ranking(id_usuario):
    ejecutar("""
        DELETE FROM ranking_usuarios
        WHERE id_usuario = %s
    """, (id_usuario,))

    return jsonify({"mensaje": "Usuario eliminado del ranking"})


@app.route("/reservas/<int:id_reserva>", methods=["DELETE"])
def cancelar_reserva(id_reserva):
    reserva = ejecutar("""
        SELECT id_usuario
        FROM reservas
        WHERE id_reserva = %s
    """, (id_reserva,), fetch=True)

    if not reserva:
        return jsonify({"mensaje": "Reserva no encontrada"}), 404

    id_usuario = reserva[0]["id_usuario"]

    ejecutar("""
        DELETE FROM reservas
        WHERE id_reserva = %s
    """, (id_reserva,))

    ejecutar("""
        INSERT INTO ranking_usuarios (id_usuario, cant_cancelaciones)
        VALUES (%s, 1)
        ON DUPLICATE KEY UPDATE
        cant_cancelaciones = cant_cancelaciones + 1
    """, (id_usuario,))

    return jsonify({"mensaje": "Reserva cancelada y ranking actualizado"})


if __name__ == "__main__":
    app.run(debug=True)