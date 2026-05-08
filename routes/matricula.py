from flask import Blueprint, render_template, request, redirect

matricula_bp = Blueprint('matricula', __name__)


@matricula_bp.route('/matricula/individual', methods=['GET', 'POST'])
def individual():
    """GET: formulario con datalist de estudiantes, programas, periodos.
    POST: crea matricula y genera cobros en cuenta corriente."""
    pass


@matricula_bp.route('/matricula/masiva', methods=['GET', 'POST'])
def masiva():
    """GET: formulario para seleccionar programa.
    POST: genera matriculas para periodo siguiente (semestre+1) para todos los estudiantes activos."""
    pass
