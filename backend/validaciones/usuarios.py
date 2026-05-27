def validar_id(id):
    """Valida que la ID sea un número vlido mayor a cero."""
    if id <= 0:
        return {"error": "Bad Request", "message": "Id invalido"}


def validar_nombre_usuario(nombre):
    """Valida el formato del nombre de usuario."""
    largo = len(str(nombre).strip())
    if largo == 0:
        return {"error": "Bad Request", "message": "El nombre no puede estar vacio"}
    if largo > 50:
        return {"error": "Bad Request", "message": "El nombre no puede tener mas de 50 caracteres"}


def validar_email_usuario(email):
    """Valida el formato del email del usuario."""
    if str(email).count('@') != 1:
        return {"error": "Bad Request", "message": "Formato de email invalido"}


def validar_numero_usuario(numero):
    """Valida el formato del numero de telefono del usuario."""
    if not str(numero).isdigit():
        return {"error": "Bad Request", "message": "Formato de numero invalido"}


def validar_usuario_existe(usuario):
    """Valida si el usuario existe"""
    if not usuario:
        return {"error": "Not Found", "message": "El email no esta registrado"}

def validar_body(body):

    """Valida que el cuerpo de la petición no esté vacío."""
    
    if body is None:
        return {"error": "Bad Request", "message": "No se recibio informacion en el cuerpo de la peticion"}
    
def validar_actualizacion_completa(id, body):
    """Valida el PUT y devuelve un diccionario con el error si falla."""
    error_id = validar_id(id)
    if error_id: 
        return error_id

    if not body:
        return {"error": "Bad Request", "message": "No se recibio informacion en el cuerpo de la peticion"}

    nombre = body.get("nombre")
    numero = body.get("numero")
    email = body.get("email")

    if nombre is None or numero is None or email is None:
        return {"error": "Bad Request", "message": "Faltan campos obligatorios"}
        
    error = validar_nombre_usuario(nombre)
    if error: 
        return error

    error = validar_numero_usuario(numero)
    if error: 
        return error

    error = validar_email_usuario(email)
    if error: 
        return error