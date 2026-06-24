from flask import Blueprint, session, request, flash, redirect, url_for
from constantes import URL_BACKEND
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
        return redirect(url_for("home.pagina_principal"))


    elif resultado == 404:
        flash("No se encontró el usuario", "error")
        return redirect(url_for("home.pagina_principal"))

    elif resultado == 201:
        flash("Reseña cargada", "success")

    else:
        flash("Hubo un error con el servidor", "error")
        return redirect(url_for("home.pagina_principal"))


    respuesta_resena = confirmar_reseña(id_usuario)

    if respuesta_resena == 404:
        flash("La reseña no existe", "error")

    elif respuesta_resena == 400:
        flash("Id no valida o no se recibio nada en el body", "error")

    elif respuesta_resena == 204:
        flash("Reseña guardada con exito", "success")

    else:
        flash("Hubo un error con el servidor", "error")
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
            f"{URL_BACKEND}/resenas",
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("reseñas")

        return {}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")

        return {}

    except Exception as e:
        logger.error(f"Error inesperado al obtener las resenas: {e}")

        return {}


def guardar_resena(id_usuario, comentario, valoracion):
    try:
        response = requests.post(
            f"{URL_BACKEND}/resenas",
            json={
                "id_usuario": id_usuario,
                "comentario": comentario,
                "valoracion": valoracion,
            },
            timeout=10,
        )

        return response.status_code

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")

        return 500

    except Exception as e:
        logger.error(f"Error inesperado al obtener las resenas: {e}")

        return 500
    

def confirmar_reseña(id_usuario):
    try:
        payload = {"estado_reserva": "RESEÑADO"}
        respuesta = requests.patch(
            f"{URL_BACKEND}/reservas/usuario/{id_usuario}", json=payload, timeout=5
        )

        return respuesta.status_code

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")
        return 500

    except Exception as e:
        logger.error(f"Error inesperado al intentar confirmar la reseña: {e}")
        return 500


def obtener_resena_id(id_usuario):
    try:
        response = requests.get(f"{URL_BACKEND}/resenas/usuario/{id_usuario}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            cambiar_estrellas(data)
            return data

        return {}

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")

        return {}

    except Exception as e:
        logger.error(f"Error inesperado al obtener las resenas: {e}")
        return {}


@resenas_bp.route("/modificar/<int:id_comentario>", methods=["POST"])
def modificar_resena(id_comentario):
    id_usuario = session["usuario"]["id"]
    comentario = request.form.get("ucomentario", "").strip()
    valoracion = int(request.form.get("uestrellas", 0))

    resultado = modificar_resena_id(id_comentario, comentario, valoracion, id_usuario)

    if resultado == 400:
        flash(
            "No se enviaron los todos los datos o hubo una valoracion invalida", "error"
        )

    elif resultado == 404:
        flash("Se intento modificar una reseña que no es suya", "error")

    elif resultado == 204:
        flash("Resena modificada, success")

    else:
        flash("Error en el servidor", "error")


    return redirect(url_for("usuarios.perfil_usuario"))


def modificar_resena_id(id_comentario, comentario, valoracion, id_usuario):
    try:
        response = requests.put(
            f"{URL_BACKEND}/reseñas/{id_comentario}",
            json={
                "id_usuario": id_usuario,
                "comentario": comentario,
                "valoracion": valoracion,
            },
            timeout=10,
        )

        return response.status_code

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")

        return 500

    except Exception as e:
        logger.error(f"Error inesperado al eliminar la resena: {e}")
        return 500

@resenas_bp.route("/eliminar/<int:id_comentario>", methods=["POST"])
def eliminar_resena(id_comentario):

    id_usuario = session["usuario"]["id"]
    resultado = eliminar_resena_id(id_usuario, id_comentario)

    if resultado == 400:
        flash("Faltan campos en el body", "error")

    elif resultado == 404:
        flash("La reseña no existe", "error")

    elif resultado == 204:
        flash("Reseña eliminada con exito", "success")

    else:
        flash("Error en el servidor", "error")

    return redirect(url_for("usuarios.perfil_usuario"))


def eliminar_resena_id(id_usuario, id_comentario):
    try:
        response = requests.delete(
            f"{URL_BACKEND}/reseñas/{id_comentario}",
            json={"id_usuario": id_usuario},
            timeout=10,
        )

        return response.status_code

    except requests.exceptions.ConnectionError:
        logger.error(f"No se pudo conectar con la API en {URL_BACKEND}")
        return 500

    except Exception as e:
        logger.error(f"Error inesperado al eliminar la resena: {e}")
        return 500
