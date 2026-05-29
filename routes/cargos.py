from flask import Blueprint, render_template, request, redirect, flash, session
from services.cargo_service import registrar_cargo, obtener_servicios_cobro
from services.config_academica_service import listar_estudiantes
from services.cuenta_service import obtener_todos_los_periodos

cargos_bp = Blueprint('cargos', __name__)

@cargos_bp.route('/cargos/registro', methods=['GET', 'POST'])
def registro():
    """GET: formulario para cargar un servicio (carnet, laboratorio, etc.) a un estudiante.
    POST: registra el cobro como movimiento en cuenta corriente (transaccion)."""

    if 'usuario' not in session or session['usuario']['rol'] not in ['ASISTENTE', 'ADMINISTRADOR']:
        flash('No tiene permisos para registrar cargos.', 'error')
        return redirect('/')

    if request.method == 'POST':
        cod_estudiante = request.form.get('cod_estudiante', '').strip()
        monto = request.form.get('monto')
        codigo_servicio = request.form.get('codigo_servicio')
        cod_periodo = request.form.get('cod_periodo')

        import re
        if not re.match(r'^[0-9]{2,8}$', cod_estudiante):
            flash('Ingrese el código del estudiante', 'error')
        else:
            try:
                registrar_cargo(
                    cod_estudiante=cod_estudiante,
                    monto=float(monto),
                    codigo_servicio=codigo_servicio,
                    cod_periodo=cod_periodo,
                    id_usuario=session['usuario']['id']
                )
                flash('Cargo registrado exitosamente en la cuenta del estudiante.', 'success')
                return redirect('/cargos/registro')
            except Exception as e:
                flash(f'Error al registrar el cargo: {str(e)}', 'error')

    estudiantes = listar_estudiantes()
    periodos = obtener_todos_los_periodos()
    servicios = obtener_servicios_cobro()

    return render_template(
        'cargos/registro.html',
        estudiantes=estudiantes,
        periodos=periodos,
        servicios=servicios
    )
