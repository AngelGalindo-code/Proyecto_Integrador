from flask import Blueprint
from constantes import API_BASE_URL
import logging
import requests


resenas_bp = Blueprint("resenas", __name__)


def resenas_destacadas():

    resenas = obtener_resenas()

    cambiar_estrellas(resenas)

    resenas_filtradas = {}

    # filtrar reseñas sin comentarios, comentarios muy grandes y de id repetidas
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

