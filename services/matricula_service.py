from models.db import get_connection, close_connection


def crear_individual(cod_estudiante, prog_academico, cod_periodo, modalidad, semestre):
    """Crea una matricula individual y genera cobros en cuenta corriente.
    Valida: estudiante existe, costo definido, matricula no duplicada."""
    pass


def crear_masiva(prog_academico):
    """Genera matriculas para el periodo siguiente (semestre+1) para todos
    los estudiantes activos del programa. Conserva modalidad anterior.
    Excluye estudiantes en ultimo semestre."""
    pass


def obtener_matricula(id):
    """Retorna una matricula por su id."""
    pass


def listar_por_estudiante(cod_estudiante):
    """Retorna todas las matriculas de un estudiante."""
    pass


def listar_por_programa_periodo(prog_academico, cod_periodo):
    """Retorna todas las matriculas de un programa en un periodo."""
    pass
