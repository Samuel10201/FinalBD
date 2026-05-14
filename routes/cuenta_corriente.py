from flask import Blueprint, render_template, request

cuenta_corriente_bp = Blueprint('cuenta_corriente', __name__)


@cuenta_corriente_bp.route('/cuenta-corriente')
def consulta():
    """Buscar estudiante (datalist) y mostrar movimientos con saldo por periodo."""
    return render_template('en_construccion.html')
