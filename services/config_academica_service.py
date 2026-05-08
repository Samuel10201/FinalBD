from models.db import get_connection, close_connection


# --- Estudiantes ---

def listar_estudiantes():
    """Retorna lista de todos los estudiantes."""
    pass


def obtener_estudiante(codigo):
    """Retorna un estudiante por su codigo."""
    pass


def crear_estudiante(codigo, nombre, fecha_nacimiento, direccion, tipo_id, id, correo, contrasena):
    """Crea usuario (rol ESTUDIANTE) + estudiante + cuenta corriente en una transaccion BEGIN/COMMIT."""
    pass


def actualizar_estudiante(codigo, nombre, fecha_nacimiento, direccion, estado):
    """Actualiza los datos de un estudiante existente."""
    pass


def desactivar_estudiante(codigo):
    """Desactiva estudiante y su usuario (estado = INACTIVO)."""
    pass


# --- Programas Academicos ---

def listar_programas():
    """Retorna lista de todos los programas academicos."""
    pass


def obtener_programa(nombre):
    """Retorna un programa academico por su nombre (PK)."""
    pass


def crear_programa(nombre, facultad, modo, duracion):
    """Crea un programa academico nuevo."""
    pass


def actualizar_programa(nombre, facultad, modo, duracion):
    """Actualiza los datos de un programa academico."""
    pass


def desactivar_programa(nombre):
    """Desactiva un programa. No permite si tiene matriculas activas."""
    pass


# --- Asignaturas ---

def listar_asignaturas():
    """Retorna lista de todas las asignaturas."""
    pass


def obtener_asignatura(codigo):
    """Retorna una asignatura por su codigo."""
    pass


def crear_asignatura(codigo, nombre, creditos, descripcion, tipo, prog_academico, semestre):
    """Crea asignatura y la asigna al plan de estudio del programa indicado."""
    pass


def actualizar_asignatura(codigo, nombre, creditos, descripcion, tipo):
    """Actualiza los datos de una asignatura."""
    pass


def eliminar_asignatura(codigo):
    """Elimina la asignatura y la remueve de todos los planes de estudio."""
    pass


# --- Plan de Estudio ---

def listar_plan_estudio(prog_academico):
    """Retorna el plan de estudio de un programa: asignaturas agrupadas por semestre."""
    pass


def asignar_asignatura_plan(prog_academico, cod_asignatura, semestre):
    """Asigna una asignatura a un programa con el semestre indicado."""
    pass


def eliminar_asignatura_plan(prog_academico, cod_asignatura):
    """Remueve una asignatura de un plan de estudio especifico."""
    pass
