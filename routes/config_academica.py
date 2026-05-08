from flask import Blueprint, render_template, request, redirect

config_academica_bp = Blueprint('config_academica', __name__)


# --- Estudiantes ---

@config_academica_bp.route('/configuracion/estudiantes')
def listar_estudiantes():
    """Muestra lista de estudiantes con opciones de CRUD."""
    pass


@config_academica_bp.route('/configuracion/estudiantes/crear', methods=['GET', 'POST'])
def crear_estudiante():
    """GET: formulario. POST: crea usuario + estudiante + cuenta corriente (transaccion)."""
    pass


@config_academica_bp.route('/configuracion/estudiantes/<codigo>/editar', methods=['GET', 'POST'])
def editar_estudiante(codigo):
    """GET: formulario con datos actuales. POST: actualiza el estudiante."""
    pass


@config_academica_bp.route('/configuracion/estudiantes/<codigo>/desactivar', methods=['POST'])
def desactivar_estudiante(codigo):
    """Desactiva estudiante y su usuario (estado = INACTIVO)."""
    pass


# --- Programas Academicos ---

@config_academica_bp.route('/configuracion/programas')
def listar_programas():
    """Muestra lista de programas academicos."""
    pass


@config_academica_bp.route('/configuracion/programas/crear', methods=['GET', 'POST'])
def crear_programa():
    """GET: formulario. POST: crea el programa academico."""
    pass


@config_academica_bp.route('/configuracion/programas/<nombre>/editar', methods=['GET', 'POST'])
def editar_programa(nombre):
    """GET: formulario con datos actuales. POST: actualiza el programa."""
    pass


@config_academica_bp.route('/configuracion/programas/<nombre>/desactivar', methods=['POST'])
def desactivar_programa(nombre):
    """Desactiva el programa academico (estado = INACTIVO)."""
    pass


# --- Asignaturas ---

@config_academica_bp.route('/configuracion/asignaturas')
def listar_asignaturas():
    """Muestra lista de asignaturas."""
    pass


@config_academica_bp.route('/configuracion/asignaturas/crear', methods=['GET', 'POST'])
def crear_asignatura():
    """GET: formulario con datalist de programas. POST: crea asignatura y la asigna a plan de estudio."""
    pass


@config_academica_bp.route('/configuracion/asignaturas/<codigo>/editar', methods=['GET', 'POST'])
def editar_asignatura(codigo):
    """GET: formulario con datos actuales. POST: actualiza la asignatura."""
    pass


@config_academica_bp.route('/configuracion/asignaturas/<codigo>/eliminar', methods=['POST'])
def eliminar_asignatura(codigo):
    """Elimina la asignatura y la remueve de todos los planes de estudio."""
    pass


# --- Plan de Estudio ---

@config_academica_bp.route('/configuracion/plan-estudio')
def listar_plan_estudio():
    """Muestra plan de estudio: programa > semestre > asignaturas con creditos."""
    pass


@config_academica_bp.route('/configuracion/plan-estudio/asignar', methods=['POST'])
def asignar_asignatura_plan():
    """Asigna una asignatura existente a un programa con su semestre."""
    pass


@config_academica_bp.route('/configuracion/plan-estudio/eliminar', methods=['POST'])
def eliminar_asignatura_plan():
    """Remueve una asignatura de un plan de estudio especifico."""
    pass
