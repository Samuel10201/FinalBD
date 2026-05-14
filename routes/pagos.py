from flask import Blueprint, render_template, request, redirect

pagos_bp = Blueprint('pagos', __name__)


@pagos_bp.route('/pagos/registro', methods=['GET', 'POST'])
def registro():
    """GET: formulario de pago en caja (asistente). Datalist de estudiantes.
    POST: registra pago + movimiento en cuenta corriente (transaccion)."""
    return render_template('en_construccion.html')


@pagos_bp.route('/pagos/en-linea', methods=['GET', 'POST'])
def en_linea():
    """GET: formulario de pago en linea (estudiante, ve solo su cuenta).
    POST: registra pago + movimiento en cuenta corriente (transaccion)."""
    return render_template('en_construccion.html')


@pagos_bp.route('/pagos/<int:id_pago>/anular', methods=['POST'])
def anular_pago(id_pago):
    """Cambia estado del pago a ANULADO. No se elimina el registro."""
    return render_template('en_construccion.html')
