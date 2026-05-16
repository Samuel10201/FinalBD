from flask import Blueprint, render_template, request, redirect, flash
from services import config_operativa_service
from services.config_academica_service import listar_programas
from routes import rol_requerido

config_operativa_bp = Blueprint('config_operativa', __name__)


# --- Periodos ---

@config_operativa_bp.route('/configuracion/periodos')
@rol_requerido('SUPERVISOR')
def listar_periodos():
    tab = request.args.get('tab', 'buscar')
    codigo_filtro = request.args.get('codigo')
    estado_filtro = request.args.get('estado')

    periodo_edit = None
    codigo_cargar = request.args.get('codigo_cargar')
    if codigo_cargar and tab == 'actualizar':
        periodo_edit = config_operativa_service.obtener_periodo(codigo_cargar)
        if not periodo_edit:
            flash(f'Periodo con codigo {codigo_cargar} no encontrado.', 'error')

    periodo_desactivar = None
    codigo_desactivar = request.args.get('codigo_desactivar')
    if codigo_desactivar and tab == 'desactivar':
        periodo_desactivar = config_operativa_service.obtener_periodo(codigo_desactivar)
        if not periodo_desactivar:
            flash(f'Periodo con codigo {codigo_desactivar} no encontrado.', 'error')

    periodos = config_operativa_service.listar_periodos(codigo=codigo_filtro, estado=estado_filtro)

    return render_template(
        'configuracion/periodos.html',
        periodos=periodos,
        tab=tab,
        periodo_edit=periodo_edit,
        periodo_desactivar=periodo_desactivar,
        codigo_filtro=codigo_filtro,
        estado_filtro=estado_filtro
    )


@config_operativa_bp.route('/configuracion/periodos/crear', methods=['POST'])
@rol_requerido('SUPERVISOR')
def crear_periodo():
    try:
        codigo = request.form.get('codigo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        if not all([codigo, descripcion, fecha_inicio, fecha_fin]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/periodos?tab=crear')

        if fecha_fin < fecha_inicio:
            flash('La fecha de fin no puede ser anterior a la fecha de inicio.', 'error')
            return redirect('/configuracion/periodos?tab=crear')

        config_operativa_service.crear_periodo(codigo, descripcion, fecha_inicio, fecha_fin)
        flash('Periodo creado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/periodos')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/editar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def editar_periodo(codigo):
    try:
        descripcion = request.form.get('descripcion', '').strip()
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()
        estado = request.form.get('estado', '').strip()

        if fecha_fin < fecha_inicio:
            flash('La fecha de fin no puede ser anterior a la fecha de inicio.', 'error')
            return redirect(f'/configuracion/periodos?tab=actualizar&codigo_cargar={codigo}')

        config_operativa_service.actualizar_periodo(codigo, descripcion, fecha_inicio, fecha_fin, estado)
        flash('Periodo actualizado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/periodos')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/desactivar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def desactivar_periodo(codigo):
    try:
        config_operativa_service.desactivar_periodo(codigo)
        flash('Periodo desactivado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect('/configuracion/periodos')


# --- Servicios (codigos de detalle) ---

@config_operativa_bp.route('/configuracion/servicios')
@rol_requerido('SUPERVISOR')
def listar_servicios():
    tab = request.args.get('tab', 'buscar')
    codigo_filtro = request.args.get('codigo')
    grupo_filtro = request.args.get('grupo')
    estado_filtro = request.args.get('estado')

    servicio_edit = None
    codigo_cargar = request.args.get('codigo_cargar')
    if codigo_cargar and tab == 'actualizar':
        servicio_edit = config_operativa_service.obtener_servicio(codigo_cargar)
        if not servicio_edit:
            flash(f'Servicio con codigo {codigo_cargar} no encontrado.', 'error')

    servicio_desactivar = None
    codigo_desactivar = request.args.get('codigo_desactivar')
    if codigo_desactivar and tab == 'desactivar':
        servicio_desactivar = config_operativa_service.obtener_servicio(codigo_desactivar)
        if not servicio_desactivar:
            flash(f'Servicio con codigo {codigo_desactivar} no encontrado.', 'error')

    servicios = config_operativa_service.listar_servicios(codigo=codigo_filtro, grupo=grupo_filtro, estado=estado_filtro)

    return render_template(
        'configuracion/servicios.html',
        servicios=servicios,
        tab=tab,
        servicio_edit=servicio_edit,
        servicio_desactivar=servicio_desactivar,
        codigo_filtro=codigo_filtro,
        grupo_filtro=grupo_filtro,
        estado_filtro=estado_filtro
    )


@config_operativa_bp.route('/configuracion/servicios/crear', methods=['POST'])
@rol_requerido('SUPERVISOR')
def crear_servicio():
    try:
        codigo = request.form.get('codigo', '').strip().upper()
        grupo = request.form.get('grupo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()

        if not all([codigo, grupo, descripcion]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/servicios?tab=crear')

        config_operativa_service.crear_servicio(codigo, grupo, descripcion)
        flash('Servicio creado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/servicios')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/editar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def editar_servicio(codigo):
    try:
        grupo = request.form.get('grupo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        estado = request.form.get('estado', '').strip()

        config_operativa_service.actualizar_servicio(codigo, grupo, descripcion, estado)
        flash('Servicio actualizado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/servicios')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/desactivar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def desactivar_servicio(codigo):
    try:
        config_operativa_service.desactivar_servicio(codigo)
        flash('Servicio desactivado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect('/configuracion/servicios')


# --- Costos (reglas de cobro) ---

@config_operativa_bp.route('/configuracion/costos')
@rol_requerido('SUPERVISOR')
def listar_costos():
    costos = config_operativa_service.listar_costos()
    programas = listar_programas()
    periodos = config_operativa_service.listar_periodos()

    return render_template(
        'configuracion/costos.html',
        costos=costos,
        programas=programas,
        periodos=periodos
    )


@config_operativa_bp.route('/configuracion/costos/crear', methods=['POST'])
@rol_requerido('SUPERVISOR')
def crear_o_actualizar_costo():
    try:
        prog_academico = request.form.get('prog_academico', '').strip()
        cod_periodo = request.form.get('cod_periodo', '').strip()
        costo_credito = request.form.get('costo_credito', '').strip()
        costo_global = request.form.get('costo_global', '').strip()

        if not all([prog_academico, cod_periodo, costo_credito, costo_global]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/costos')

        config_operativa_service.crear_o_actualizar_costo(
            prog_academico, cod_periodo, costo_credito, costo_global
        )
        flash('Costo guardado exitosamente.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect('/configuracion/costos')


@config_operativa_bp.route('/configuracion/costos/<prog_academico>/<cod_periodo>/eliminar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def eliminar_costo(prog_academico, cod_periodo):
    try:
        config_operativa_service.eliminar_costo(prog_academico, cod_periodo)
        flash('Costo eliminado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect('/configuracion/costos')
