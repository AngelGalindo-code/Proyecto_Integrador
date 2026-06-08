from flask import session, abort
from functools import wraps

# Creamos nuestro decorador para que solo el admin pueda ver la lista de reservas
def adminRequired(f):
    @wraps(f) # PAra que no confunda el nombre de las funciones

    def decorarFuncion(*args, **kwargs):
        if session.get('rol') != 'admin':
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorarFuncion


def loginRequired(f):
    @wraps(f)

    def decorarFuncion(*args, **kwargs):
        if not session.get('id_usuario'):
            abort(403)

        return f(*args, **kwargs)
    
    return decorarFuncion