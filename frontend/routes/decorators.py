from flask import session, abort
from functools import wraps

def adminRequired(f):
    @wraps(f) 
    def decorarFuncion(*args, **kwargs):
        # Busca el rol de forma segura adentro del diccionario 'usuario'
        rol_usuario = session.get('usuario', {}).get('rol')
        
        if rol_usuario != 'admin':
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorarFuncion


def loginRequired(f):
    @wraps(f)
    def decorarFuncion(*args, **kwargs):

        id_usuario = session.get('id_usuario') or session.get('usuario', {}).get('id')
        
        if not id_usuario:
            abort(403)

        return f(*args, **kwargs)
    
    return decorarFuncion