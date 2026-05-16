from flask import Blueprint, render_template, request, redirect, flash
from services import config_operativa_service

config_operativa_bp = Blueprint('config_operativa', __name__)


# --- Periodos ---

@config_operativa_bp.route('/configuracion/periodos')
def listar_periodos():
    """Muestra lista de periodos academicos."""

    periodos = config_operativa_service.listar_periodos()

    return render_template(
        'configuracion/periodos.html',
        periodos=periodos
    )


@config_operativa_bp.route('/configuracion/periodos/crear', methods=['POST'])
def crear_periodo():
    """Crea un periodo."""

    try:
        codigo = request.form.get('codigo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        if not all([codigo, descripcion, fecha_inicio, fecha_fin]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/periodos')

        config_operativa_service.crear_periodo(
            codigo,
            descripcion,
            fecha_inicio,
            fecha_fin
        )

        flash('Periodo creado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/periodos')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/editar', methods=['GET', 'POST'])
def editar_periodo(codigo):

    if request.method == 'GET':

        periodo = config_operativa_service.obtener_periodo(codigo)
        periodos = config_operativa_service.listar_periodos()

        return render_template(
            'configuracion/periodos.html',
            periodo_edit=periodo,
            periodos=periodos
        )

    elif request.method == 'POST':

        try:
            descripcion = request.form.get('descripcion', '').strip()
            fecha_inicio = request.form.get('fecha_inicio', '').strip()
            fecha_fin = request.form.get('fecha_fin', '').strip()
            estado = request.form.get('estado', '').strip()

            config_operativa_service.actualizar_periodo(
                codigo,
                descripcion,
                fecha_inicio,
                fecha_fin,
                estado
            )

            flash('Periodo actualizado exitosamente.', 'success')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        return redirect('/configuracion/periodos')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/desactivar', methods=['POST'])
def desactivar_periodo(codigo):

    try:
        config_operativa_service.desactivar_periodo(codigo)

        flash('Periodo desactivado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/periodos')

# --- Servicios (codigos de detalle) ---

@config_operativa_bp.route('/configuracion/servicios')
def listar_servicios():
    """Muestra lista de servicios."""
    
    servicios = config_operativa_service.listar_servicios()

    return render_template(
        'configuracion/servicios.html',
        servicios=servicios
    )


@config_operativa_bp.route('/configuracion/servicios/crear', methods=['POST'])
def crear_servicio():
    """Crea un servicio."""

    try:
        codigo = request.form.get('codigo', '').strip().upper()
        grupo = request.form.get('grupo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not all([codigo, grupo, descripcion]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/servicios')

        config_operativa_service.crear_servicio(
            codigo,
            grupo,
            descripcion
        )

        flash('Servicio creado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/servicios')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/editar', methods=['GET', 'POST'])
def editar_servicio(codigo):

    if request.method == 'GET':

        servicio = config_operativa_service.obtener_servicio(codigo)
        servicios = config_operativa_service.listar_servicios()

        return render_template(
            'configuracion/servicios.html',
            servicio_edit=servicio,
            servicios=servicios
        )

    elif request.method == 'POST':

        try:
            grupo = request.form.get('grupo', '').strip()
            descripcion = request.form.get('descripcion', '').strip()
            estado = request.form.get('estado', '').strip()

            config_operativa_service.actualizar_servicio(
                codigo,
                grupo,
                descripcion,
                estado
            )

            flash('Servicio actualizado exitosamente.', 'success')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        return redirect('/configuracion/servicios')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/desactivar', methods=['POST'])
def desactivar_servicio(codigo):

    try:
        config_operativa_service.desactivar_servicio(codigo)

        flash('Servicio desactivado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/servicios')


# --- Costos (reglas de cobro) ---

@config_operativa_bp.route('/configuracion/costos')
def listar_costos():
    """Muestra lista de costos."""

    costos = config_operativa_service.listar_costos()

    return render_template(
        'configuracion/costos.html',
        costos=costos
    )


@config_operativa_bp.route('/configuracion/costos/crear', methods=['POST'])
def crear_o_actualizar_costo():
    """Crea o actualiza un costo."""

    try:
        prog_academico = request.form.get('prog_academico', '').strip()
        cod_periodo = request.form.get('cod_periodo', '').strip()
        costo_credito = request.form.get('costo_credito', '').strip()
        costo_global = request.form.get('costo_global', '').strip()

        if not all([
            prog_academico,
            cod_periodo,
            costo_credito,
            costo_global
        ]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/costos')

        config_operativa_service.crear_o_actualizar_costo(
            prog_academico,
            cod_periodo,
            costo_credito,
            costo_global
        )

        flash('Costo guardado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/costos')


@config_operativa_bp.route('/configuracion/costos/<prog_academico>/<cod_periodo>/eliminar', methods=['POST'])
def eliminar_costo(prog_academico, cod_periodo):

    try:
        config_operativa_service.eliminar_costo(
            prog_academico,
            cod_periodo
        )

        flash('Costo eliminado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/costos')
