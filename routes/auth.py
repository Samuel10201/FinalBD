from flask import Blueprint, render_template, request, redirect, session

auth_bp = Blueprint('auth', __name__)


# --- Login / Logout ---

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """GET: muestra formulario. POST: autentica con correo+contrasena, redirige segun rol."""
    pass


@auth_bp.route('/logout')
def logout():
    """Cierra la sesion y redirige al login."""
    pass


# --- Gestion de usuarios (ADMIN) ---

@auth_bp.route('/admin/usuarios')
def listar_usuarios():
    """Muestra lista de usuarios con opciones de CRUD."""
    pass


@auth_bp.route('/admin/usuarios/crear', methods=['GET', 'POST'])
def crear_usuario():
    """GET: formulario. POST: crea usuario (ADMIN, SUPERVISOR o ASISTENTE)."""
    pass


@auth_bp.route('/admin/usuarios/<tipo_id>/<id>/editar', methods=['GET', 'POST'])
def editar_usuario(tipo_id, id):
    """GET: formulario con datos actuales. POST: actualiza el usuario."""
    pass


@auth_bp.route('/admin/usuarios/<tipo_id>/<id>/desactivar', methods=['POST'])
def desactivar_usuario(tipo_id, id):
    """Cambia estado del usuario a INACTIVO. Si es estudiante, desactiva ambos."""
    pass
