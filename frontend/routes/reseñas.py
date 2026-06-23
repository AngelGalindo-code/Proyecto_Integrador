from flask import Blueprint, session, request, flash
from constantes import API_BASE_URL
import logging
import requests


resenas_bp = Blueprint("resenas", __name__)


@resenas_bp.route("/", methods=["POST"])
def publicar_resena():

    id_usuario = session["usuario"]["id"]
    comentario = request.form.get("ucomentario", "").strip()
    valoracion = int(request.form.get("uestrellas", 0))

    resultado = guardar_resena(id_usuario, comentario, valoracion)

    if resultado == 400:
        flash(
            "No se han ingresado todos los datos o la valoracion no es valida",
            "error",
        )


    if resultado == 404:
        flash("No se encontró el usuario", "error")


    if resultado == 201:
        flash("Reseña cargada", "success")


    confirmar_reseña(id_usuario)
    return redirect(url_for("home.pagina_principal"))


def resenas_destacadas():

    resenas = obtener_resenas()

    cambiar_estrellas(resenas)

    resenas_filtradas = {}

    # filtrar reseñas sin comentarios, comentarios muy largos e id repetidas
    for resena in resenas:
        if (
            resena["comentario"] != ""
            and resena["nombre"] not in resenas_filtradas
            and len(resena["comentario"]) <= 45
        ):
            resenas_filtradas[resena["nombre"]] = {
                "comentario": resena["comentario"],
                "valoracion": resena["valoracion"],
            }

        if len(resenas_filtradas) == 4:
            break

    return resenas_filtradas

def cambiar_estrellas(resenas):

    for resena in resenas:
        estrellas = []

        for i in range(resena["valoracion"]):
            estrellas.append("★")

        while len(estrellas) != 5:
            estrellas.append("☆")

        resena["valoracion"] = "".join(estrellas)


logger = logging.getLogger(__name__)

def obtener_resenas():
    try:

        response = requests.get(
            f"{API_BASE_URL}/resenas",
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("reseñas")

        return {}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

        return {}

    except Exception as e:
        logger.error(f"Error inesperado al obtener las resenas: {e}")

        return {}


def guardar_resena(id_usuario, comentario, valoracion):
    try:
        response = requests.post(
            f"{API_BASE_URL}/resenas",
            json={
                "id_usuario": id_usuario,
                "comentario": comentario,
                "valoracion": valoracion,
            },
            timeout=10,
        )

        return response.status_code

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {API_BASE_URL}")

        abort(500)

    except Exception as e:
        logger.error(f"Error inesperado al obtener las resenas: {e}")

        abort(500)

