from models.db import get_connection, close_connection


# --- Autenticacion ---

def login(correo, contrasena):
    """Verifica credenciales. Retorna datos del usuario si son correctas, None si no."""
    pass


def obtener_usuario(tipo_id, id):
    """Busca y retorna un usuario por su llave compuesta (tipo_id, id)."""
    pass


# --- CRUD Usuarios ---

def listar_usuarios():
    """Retorna lista de todos los usuarios."""
    pass


def crear_usuario(tipo_id, id, nombre, correo, contrasena, rol):
    """Crea un usuario nuevo (ADMIN, SUPERVISOR o ASISTENTE). Retorna el usuario creado."""
    pass


def actualizar_usuario(tipo_id, id, nombre, correo, rol, estado):
    """Actualiza los datos de un usuario existente."""
    pass


def desactivar_usuario(tipo_id, id):
    """Cambia estado a INACTIVO. Si es estudiante, desactiva ambos registros."""
    pass
