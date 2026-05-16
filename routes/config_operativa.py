import re
from flask import Blueprint, render_template, request, redirect, flash
from services import config_operativa_service
from services.config_academica_service import listar_programas, obtener_programa
from routes import rol_requerido

config_operativa_bp = Blueprint('config_operativa', __name__)

_PERIODO_DESC = {
    '00': 'Periodo Libre',
    '10': 'Primer Semestre',
    '20': 'Intersemestral',
    '30': 'Segundo Semestre',
    '40': 'Vacacional Final',
}

def _descripcion_periodo(codigo):
    if len(codigo) == 6 and re.match(r'^[0-9]{4}(00|10|20|30|40)$', codigo):
        return f'{_PERIODO_DESC[codigo[4:]]} {codigo[:4]}'
    return None


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
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()

        descripcion = _descripcion_periodo(codigo)
        if not descripcion:
            flash('Código de periodo inválido. Debe ser 4 dígitos del año + 00, 10, 20, 30 o 40.', 'error')
            return redirect('/configuracion/periodos?tab=crear')

        if not all([fecha_inicio, fecha_fin]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect('/configuracion/periodos?tab=crear')

        anio = codigo[:4]
        if not fecha_inicio.startswith(anio):
            flash(f'La fecha de inicio debe corresponder al año {anio}.', 'error')
            return redirect('/configuracion/periodos?tab=crear')
        if not fecha_fin.startswith(anio):
            flash(f'La fecha de fin debe corresponder al año {anio}.', 'error')
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
        fecha_inicio = request.form.get('fecha_inicio', '').strip()
        fecha_fin = request.form.get('fecha_fin', '').strip()
        estado = request.form.get('estado', '').strip()

        descripcion = _descripcion_periodo(codigo)
        if not descripcion:
            flash('Código de periodo inválido.', 'error')
            return redirect('/configuracion/periodos?tab=actualizar')

        anio = codigo[:4]
        if not fecha_inicio.startswith(anio):
            flash(f'La fecha de inicio debe corresponder al año {anio}.', 'error')
            return redirect(f'/configuracion/periodos?tab=actualizar&codigo_cargar={codigo}')
        if not fecha_fin.startswith(anio):
            flash(f'La fecha de fin debe corresponder al año {anio}.', 'error')
            return redirect(f'/configuracion/periodos?tab=actualizar&codigo_cargar={codigo}')

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

        if not all([grupo, descripcion, estado]):
            flash('Todos los campos son obligatorios.', 'error')
            return redirect(f'/configuracion/servicios?tab=actualizar&codigo_cargar={codigo}')

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

        if not obtener_programa(prog_academico):
            flash('El programa académico no existe. Seleccione uno de la lista.', 'error')
            return redirect('/configuracion/costos')

        if not config_operativa_service.obtener_periodo(cod_periodo):
            flash('El periodo no existe. Seleccione uno de la lista.', 'error')
            return redirect('/configuracion/costos')

        try:
            credito_val = float(costo_credito)
            global_val = float(costo_global)
        except ValueError:
            flash('Los valores de costo deben ser numéricos.', 'error')
            return redirect('/configuracion/costos')

        if credito_val <= 0 or global_val <= 0:
            flash('Los costos deben ser mayores a 0.', 'error')
            return redirect('/configuracion/costos')

        if credito_val >= 10000000000 or global_val >= 10000000000:
            flash('El valor del costo no puede superar $9,999,999,999.99', 'error')
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
