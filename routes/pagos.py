from flask import Blueprint, render_template, request, redirect, flash, session
from services.pago_service import registrar_pago, obtener_servicios_pago
from services.config_academica_service import listar_estudiantes
from services.cuenta_service import obtener_todos_los_periodos, obtener_codigo_estudiante, obtener_cuenta

pagos_bp = Blueprint('pagos', __name__)

@pagos_bp.route('/pagos/registro', methods=['GET', 'POST'])
def registro():
    """GET: formulario de pago en caja (asistente). Datalist de estudiantes.
    POST: registra pago + movimiento en cuenta corriente (transaccion)."""
    
    if 'usuario' not in session or session['usuario']['rol'] not in ['ASISTENTE', 'ADMINISTRADOR']:
        flash('No tiene permisos para registrar pagos en caja.', 'error')
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
            usuario_actual = session['usuario']
            try:
                registrar_pago(
                    cod_estudiante=cod_estudiante,
                    monto=float(monto),
                    metodo='CAJA',
                    codigo_servicio=codigo_servicio,
                    cod_periodo=cod_periodo,
                    id_usuario=usuario_actual['id']
                )
                flash('Pago por caja registrado exitosamente en estado PENDIENTE.', 'success')
                return redirect('/pagos/registro')
            except Exception as e:
                flash('Ingrese el código del estudiante', 'error')

    estudiantes = listar_estudiantes()
    periodos = obtener_todos_los_periodos()
    servicios = obtener_servicios_pago()
    
    return render_template(
        'pagos/registro.html', 
        estudiantes=estudiantes, 
        periodos=periodos, 
        servicios=servicios
    )

@pagos_bp.route('/pagos/en-linea', methods=['GET', 'POST'])
def en_linea():
    """GET: formulario de pago en linea (estudiante).
    POST: registra pago + movimiento en cuenta corriente (transaccion)."""

    if 'usuario' not in session:
        flash('Debe iniciar sesión', 'error')
        return redirect('/login')

    usuario_actual = session['usuario']
    es_admin_vista = usuario_actual['rol'] == 'ADMINISTRADOR' and session.get('vista_rol') == 'ESTUDIANTE'

    if usuario_actual['rol'] != 'ESTUDIANTE' and not es_admin_vista:
        flash('Acceso denegado. Esta sección es exclusiva para estudiantes.', 'error')
        return redirect('/')

    estudiantes_lista = []
    if es_admin_vista:
        codigo_param = request.args.get('codigo', '').strip()
        if codigo_param:
            session['estudiante_vista'] = codigo_param
        cod_estudiante = session.get('estudiante_vista')
        estudiantes_lista = listar_estudiantes(limit=500)
    else:
        cod_estudiante = obtener_codigo_estudiante(usuario_actual['id'])

    if not cod_estudiante:
        if es_admin_vista:
            periodos = obtener_todos_los_periodos()
            servicios = obtener_servicios_pago()
            return render_template('pagos/en_linea.html', periodos=periodos, servicios=servicios,
                                   es_admin_vista=True, estudiantes=estudiantes_lista,
                                   codigo_estudiante=None, nombre_estudiante=None)
        flash('No se encontró su código de estudiante en el sistema.', 'error')
        return redirect('/')

    nombre_estudiante = None
    if es_admin_vista:
        est = obtener_cuenta(cod_estudiante)
        if not est:
            session.pop('estudiante_vista', None)
            flash('Estudiante no encontrado', 'error')
            periodos = obtener_todos_los_periodos()
            servicios = obtener_servicios_pago()
            return render_template('pagos/en_linea.html', periodos=periodos, servicios=servicios,
                                   es_admin_vista=True, estudiantes=estudiantes_lista,
                                   codigo_estudiante=None, nombre_estudiante=None)
        nombre_estudiante = est['nombre']

    if request.method == 'POST':
        monto = request.form.get('monto')
        codigo_servicio = request.form.get('codigo_servicio')
        cod_periodo = request.form.get('cod_periodo')

        try:
            registrar_pago(
                cod_estudiante=cod_estudiante,
                monto=float(monto),
                metodo='EN LINEA',
                codigo_servicio=codigo_servicio,
                cod_periodo=cod_periodo,
                id_usuario=usuario_actual['id']
            )
            flash('Pago en línea exitoso. Está pendiente de validación bancaria.', 'success')
            return redirect('/estudiante/cuenta')
        except Exception as e:
            flash(f'Error en la transacción en línea: {str(e)}', 'error')

    periodos = obtener_todos_los_periodos()
    servicios = obtener_servicios_pago()

    return render_template(
        'pagos/en_linea.html',
        periodos=periodos,
        servicios=servicios,
        es_admin_vista=es_admin_vista,
        estudiantes=estudiantes_lista,
        codigo_estudiante=cod_estudiante,
        nombre_estudiante=nombre_estudiante
    )

@pagos_bp.route('/pagos/<int:id_pago>/anular', methods=['POST'])
def anular_pago(id_pago):
    """Cambia estado del pago a ANULADO. No se elimina el registro."""
    return render_template('en_construccion.html')
