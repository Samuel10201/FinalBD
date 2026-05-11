from functools import wraps
from flask import session, redirect, flash


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debe iniciar sesion', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def rol_requerido(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'usuario' not in session:
                flash('Debe iniciar sesion', 'error')
                return redirect('/login')
            if session['usuario']['rol'] == 'ADMINISTRADOR':
                return f(*args, **kwargs)
            if session['usuario']['rol'] not in roles:
                flash('No tiene permisos para acceder a esta pagina', 'error')
                return redirect('/login')
            return f(*args, **kwargs)
        return decorated
    return decorator
