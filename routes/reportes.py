from flask import Blueprint, render_template, request

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/reportes/estudiantes-programa')
def estudiantes_programa():
    """Listado de estudiantes por programa. Filtros: periodo, programa."""
    pass


@reportes_bp.route('/reportes/ingreso-esperado')
def ingreso_esperado():
    """Total que se deberia recaudar. Filtros: periodo, programa."""
    pass


@reportes_bp.route('/reportes/pendientes-pago')
def pendientes_pago():
    """Estudiantes con saldo pendiente. Filtros: periodo, programa."""
    pass


@reportes_bp.route('/reportes/ingreso-real')
def ingreso_real():
    """Total de pagos recibidos. Filtros: periodo, programa."""
    pass


@reportes_bp.route('/reportes/cartera')
def cartera():
    """Estudiantes que deben, valor individual, total cuentas por cobrar. Filtros: periodo, programa."""
    pass
