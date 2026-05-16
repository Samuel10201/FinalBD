from models.db import get_connection, close_connection
from psycopg2.errors import UniqueViolation
import bcrypt


# --- Autenticacion ---

def login(correo, contrasena):
    """Verifica credenciales. Retorna datos del usuario si son correctas, None si no."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tipo_id, id, nombre, correo, contrasena, rol, estado "
                "FROM usuario WHERE correo = %s",
                (correo,)
            )
            usuario = cur.fetchone()

        if not usuario or usuario['estado'] != 'ACTIVO':
            return None

        if not bcrypt.checkpw(contrasena.encode('utf-8'), usuario['contrasena'].encode('utf-8')):
            return None

        usuario = dict(usuario)
        del usuario['contrasena']
        return usuario
    finally:
        close_connection(conn)


def obtener_usuario(id):
    """Busca y retorna un usuario por su id (PK)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tipo_id, id, nombre, correo, rol, estado, fecha_creacion "
                "FROM usuario WHERE id = %s",
                (id,)
            )
            return cur.fetchone()
    finally:
        close_connection(conn)


def obtener_usuario_por_correo(correo):
    """Busca y retorna un usuario por su correo (UNIQUE)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tipo_id, id, nombre, correo, rol, estado, fecha_creacion "
                "FROM usuario WHERE correo = %s",
                (correo,)
            )
            return cur.fetchone()
    finally:
        close_connection(conn)


# --- CRUD Usuarios ---

def listar_usuarios_autocomplete(limite=500):
    """Retorna nombre y correo de usuarios activos para datalists de autocompletado."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT nombre, correo FROM usuario WHERE estado = 'ACTIVO' ORDER BY nombre LIMIT %s",
                (limite,)
            )
            return cur.fetchall()
    finally:
        close_connection(conn)


def listar_usuarios(buscar='', limite=20, offset=0):
    """Retorna lista de usuarios. Filtra por nombre, correo o id si se pasa buscar."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if buscar:
                filtro = f'{buscar}%'
                cur.execute(
                    "SELECT tipo_id, id, nombre, correo, rol, estado, fecha_creacion "
                    "FROM usuario WHERE nombre ILIKE %s OR correo ILIKE %s OR id ILIKE %s "
                    "ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s",
                    (filtro, filtro, filtro, limite, offset)
                )
            else:
                cur.execute(
                    "SELECT tipo_id, id, nombre, correo, rol, estado, fecha_creacion "
                    "FROM usuario ORDER BY fecha_creacion DESC LIMIT %s OFFSET %s",
                    (limite, offset)
                )
            return cur.fetchall()
    finally:
        close_connection(conn)


def crear_usuario(tipo_id, id, nombre, correo, contrasena, rol):
    """Crea un usuario nuevo (ADMIN, SUPERVISOR o ASISTENTE). Retorna el usuario creado."""
    hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuario (tipo_id, id, nombre, correo, contrasena, rol, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVO') "
                    "RETURNING tipo_id, id, nombre, correo, rol, estado",
                    (tipo_id, id, nombre, correo, hashed, rol)
                )
                return cur.fetchone()
    finally:
        close_connection(conn)


def actualizar_usuario(id, nombre, correo, rol, estado, contrasena=None, tipo_id=None):
    """Actualiza los datos de un usuario existente. Si contrasena no es None, tambien la cambia."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if contrasena else None
                if hashed:
                    cur.execute(
                        "UPDATE usuario "
                        "SET tipo_id = %s, nombre = %s, correo = %s, rol = %s, estado = %s, contrasena = %s "
                        "WHERE id = %s "
                        "RETURNING tipo_id, id, nombre, correo, rol, estado",
                        (tipo_id, nombre, correo, rol, estado, hashed, id)
                    )
                else:
                    cur.execute(
                        "UPDATE usuario SET tipo_id = %s, nombre = %s, correo = %s, rol = %s, estado = %s "
                        "WHERE id = %s "
                        "RETURNING tipo_id, id, nombre, correo, rol, estado",
                        (tipo_id, nombre, correo, rol, estado, id)
                    )
                return cur.fetchone()
    finally:
        close_connection(conn)


def desactivar_usuario(id):
    """Cambia estado a INACTIVO. Si es estudiante, desactiva ambos registros."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT codigo FROM estudiante WHERE id = %s",
                    (id,)
                )
                estudiante = cur.fetchone()

                if estudiante:
                    cur.execute(
                        "UPDATE estudiante SET estado = 'INACTIVO' WHERE codigo = %s",
                        (estudiante['codigo'],)
                    )

                cur.execute(
                    "UPDATE usuario SET estado = 'INACTIVO' WHERE id = %s",
                    (id,)
                )
    finally:
        close_connection(conn)
