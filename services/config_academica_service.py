from models.db import get_connection, close_connection
import bcrypt


# --- Estudiantes ---

def listar_estudiantes(correo=None, tipo_id=None, id_num=None, estado=None, limit=20, offset=0):
    """Retorna lista de estudiantes, con filtros opcionales y paginacion."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = (
                "SELECT e.codigo, e.nombre, e.estado, e.fecha_nacimiento, e.direccion, u.tipo_id, e.id, u.correo "
                "FROM estudiante e "
                "JOIN usuario u ON e.id = u.id "
                "WHERE 1=1 "
            )
            params = []
            if correo:
                query += "AND u.correo ILIKE %s "
                params.append(f"{correo}%")
            if tipo_id:
                query += "AND u.tipo_id = %s "
                params.append(tipo_id)
            if id_num:
                query += "AND e.id ILIKE %s "
                params.append(f"{id_num}%")
            if estado:
                query += "AND e.estado = %s "
                params.append(estado)

            query += "ORDER BY e.codigo LIMIT %s OFFSET %s"
            params.append(limit)
            params.append(offset)

            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def obtener_estudiante(codigo):
    """Retorna un estudiante por su codigo."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT e.codigo, e.nombre, e.estado, e.fecha_nacimiento, e.direccion, u.tipo_id, e.id, u.correo "
                "FROM estudiante e "
                "JOIN usuario u ON e.id = u.id "
                "WHERE e.codigo = %s",
                (codigo,)
            )
            return cur.fetchone()
    finally:
        close_connection(conn)


def crear_estudiante(codigo, nombre, fecha_nacimiento, direccion, tipo_id, id, correo, contrasena):
    """Crea usuario (rol ESTUDIANTE) + estudiante en una transaccion BEGIN/COMMIT."""
    hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuario (tipo_id, id, nombre, correo, contrasena, rol, estado) "
                    "VALUES (%s, %s, %s, %s, %s, 'ESTUDIANTE', 'ACTIVO')",
                    (tipo_id, id, nombre, correo, hashed)
                )
                cur.execute(
                    "INSERT INTO estudiante (codigo, nombre, estado, fecha_nacimiento, direccion, id) "
                    "VALUES (%s, %s, 'ACTIVO', %s, %s, %s)",
                    (codigo, nombre, fecha_nacimiento, direccion, id)
                )
    finally:
        close_connection(conn)


def actualizar_estudiante(codigo, nombre, fecha_nacimiento, direccion, estado):
    """Actualiza los datos de un estudiante existente."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE estudiante SET nombre = %s, fecha_nacimiento = %s, direccion = %s, estado = %s "
                    "WHERE codigo = %s",
                    (nombre, fecha_nacimiento, direccion, estado, codigo)
                )
                # Tambien actualizar el nombre y estado en la tabla usuario
                cur.execute(
                    "UPDATE usuario SET nombre = %s, estado = %s "
                    "WHERE id = (SELECT id FROM estudiante WHERE codigo = %s)",
                    (nombre, estado, codigo)
                )
    finally:
        close_connection(conn)


def desactivar_estudiante(codigo):
    """Desactiva estudiante y su usuario (estado = INACTIVO)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuario SET estado = 'INACTIVO' "
                    "WHERE id = (SELECT id FROM estudiante WHERE codigo = %s)",
                    (codigo,)
                )
                cur.execute(
                    "UPDATE estudiante SET estado = 'INACTIVO' WHERE codigo = %s",
                    (codigo,)
                )
    finally:
        close_connection(conn)


# --- Programas Academicos ---

def listar_programas(facultad=None, modo=None):
    """Retorna lista de programas academicos, con filtros opcionales."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM programa_academico WHERE 1=1 "
            params = []
            if facultad:
                query += "AND facultad ILIKE %s "
                params.append(f"{facultad}%")
            if modo:
                query += "AND modo = %s "
                params.append(modo)
            query += "ORDER BY nombre"
            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def obtener_programa(nombre):
    """Retorna un programa academico por su nombre (PK)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM programa_academico WHERE nombre = %s", (nombre,))
            return cur.fetchone()
    finally:
        close_connection(conn)


def crear_programa(nombre, facultad, modo, duracion):
    """Crea un programa academico nuevo."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO programa_academico (nombre, facultad, modo, duracion) VALUES (%s, %s, %s, %s)",
                    (nombre, facultad, modo, duracion)
                )
    finally:
        close_connection(conn)


def actualizar_programa(nombre, facultad, modo, duracion):
    """Actualiza los datos de un programa academico."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE programa_academico SET facultad = %s, modo = %s, duracion = %s WHERE nombre = %s",
                    (facultad, modo, duracion, nombre)
                )
    finally:
        close_connection(conn)


def desactivar_programa(nombre):
    """No existe estado para programa segun esquema, solo podemos verificar eliminacion, pero la guia dice no desactivar si tiene matriculas. Ojo: el esquema NO tiene columna 'estado' en programa_academico. Se asume que no se puede eliminar si esta en uso, y no se elimina."""
    raise NotImplementedError("El esquema no soporta desactivar un programa_academico")


# --- Asignaturas ---

def listar_asignaturas(codigo=None, nombre=None, tipo=None, limit=20, offset=0):
    """Retorna lista de asignaturas, con filtros opcionales y paginacion."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM asignatura WHERE 1=1 "
            params = []

            if codigo:
                query += "AND codigo ILIKE %s "
                params.append(f"{codigo}%")
            if nombre:
                query += "AND nombre ILIKE %s "
                params.append(f"{nombre}%")
            if tipo:
                query += "AND tipo = %s "
                params.append(tipo)

            query += "ORDER BY codigo LIMIT %s OFFSET %s"
            params.append(limit)
            params.append(offset)

            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def obtener_asignatura(codigo):
    """Retorna una asignatura por su codigo."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM asignatura WHERE codigo = %s", (codigo,))
            return cur.fetchone()
    finally:
        close_connection(conn)


def crear_asignatura(codigo, nombre, creditos, descripcion, tipo, prog_academico, semestre):
    """Crea asignatura y la asigna al plan de estudio del programa indicado."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO asignatura (codigo, nombre, creditos, descripcion, tipo) VALUES (%s, %s, %s, %s, %s)",
                    (codigo, nombre, creditos, descripcion, tipo)
                )
                cur.execute(
                    "INSERT INTO plan_estudio (nombre_programa, cod_asignatura, semestre) VALUES (%s, %s, %s)",
                    (prog_academico, codigo, semestre)
                )
    finally:
        close_connection(conn)


def actualizar_asignatura(codigo, nombre, creditos, descripcion, tipo):
    """Actualiza los datos de una asignatura."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE asignatura SET nombre = %s, creditos = %s, descripcion = %s, tipo = %s WHERE codigo = %s",
                    (nombre, creditos, descripcion, tipo, codigo)
                )
    finally:
        close_connection(conn)


def eliminar_asignatura(codigo):
    """Elimina la asignatura y la remueve de todos los planes de estudio."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM plan_estudio WHERE cod_asignatura = %s", (codigo,))
                cur.execute("DELETE FROM asignatura WHERE codigo = %s", (codigo,))
    finally:
        close_connection(conn)


# --- Plan de Estudio ---

def listar_plan_estudio(prog_academico):
    """Retorna el plan de estudio de un programa: asignaturas agrupadas por semestre."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pe.semestre, a.codigo, a.nombre, a.creditos, a.tipo "
                "FROM plan_estudio pe "
                "JOIN asignatura a ON pe.cod_asignatura = a.codigo "
                "WHERE pe.nombre_programa = %s "
                "ORDER BY pe.semestre, a.nombre",
                (prog_academico,)
            )
            return cur.fetchall()
    finally:
        close_connection(conn)


def asignar_asignatura_plan(prog_academico, cod_asignatura, semestre):
    """Asigna una asignatura a un programa con el semestre indicado."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO plan_estudio (nombre_programa, cod_asignatura, semestre) VALUES (%s, %s, %s)",
                    (prog_academico, cod_asignatura, semestre)
                )
    finally:
        close_connection(conn)


def actualizar_asignatura_en_plan(prog_academico, cod_asignatura, semestre, creditos, tipo):
    """Actualiza semestre en plan_estudio y créditos/tipo en asignatura (transacción)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE plan_estudio SET semestre = %s WHERE nombre_programa = %s AND cod_asignatura = %s",
                    (semestre, prog_academico, cod_asignatura)
                )
                cur.execute(
                    "UPDATE asignatura SET creditos = %s, tipo = %s WHERE codigo = %s",
                    (creditos, tipo, cod_asignatura)
                )
    finally:
        close_connection(conn)


def eliminar_asignatura_plan(prog_academico, cod_asignatura):
    """Remueve una asignatura de un plan de estudio especifico."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM plan_estudio WHERE nombre_programa = %s AND cod_asignatura = %s",
                    (prog_academico, cod_asignatura)
                )
    finally:
        close_connection(conn)
