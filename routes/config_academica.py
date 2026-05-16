from flask import Blueprint, render_template, request, redirect, flash, url_for
from routes import login_required, rol_requerido
import services.config_academica_service as srv

config_academica_bp = Blueprint('config_academica', __name__)


# --- Estudiantes ---

@config_academica_bp.route('/configuracion/estudiantes')
@rol_requerido('SUPERVISOR')
def listar_estudiantes():
    """Muestra lista de estudiantes con opciones de CRUD y busqueda."""
    correo = request.args.get('correo')
    tipo_id = request.args.get('tipo_id')
    id_num = request.args.get('id')
    estado = request.args.get('estado')
    tab = request.args.get('tab', 'buscar')
    pagina = int(request.args.get('pagina', 1))

    codigo_cargar = request.args.get('codigo_cargar')
    estudiante_edit = None
    if codigo_cargar and tab == 'actualizar':
        estudiante_edit = srv.obtener_estudiante(codigo_cargar)
        if not estudiante_edit:
            flash(f'Estudiante con código {codigo_cargar} no encontrado.', 'error')

    # Desactivar: cargar estudiante para confirmar
    codigo_desactivar = request.args.get('codigo_desactivar')
    estudiante_desactivar = None
    if codigo_desactivar and tab == 'desactivar':
        estudiante_desactivar = srv.obtener_estudiante(codigo_desactivar)
        if not estudiante_desactivar:
            flash(f'Estudiante con código {codigo_desactivar} no encontrado.', 'error')

    estudiantes = srv.listar_estudiantes(correo, tipo_id, id_num, estado, limit=20, offset=(pagina - 1) * 20)
    return render_template('configuracion/estudiantes.html',
                           estudiantes=estudiantes,
                           tab=tab,
                           pagina=pagina,
                           estudiante_edit=estudiante_edit,
                           estudiante_desactivar=estudiante_desactivar,
                           correo=correo, tipo_id=tipo_id, id_num=id_num, estado=estado)


@config_academica_bp.route('/configuracion/estudiantes/crear', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def crear_estudiante():
    """GET: formulario. POST: crea usuario + estudiante + cuenta corriente (transaccion)."""
    if request.method == 'POST':
        try:
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            tipo_id = request.form['tipo_id']
            id_num = request.form['id']
            correo = request.form['correo']
            contrasena = request.form['contrasena']
            
            srv.crear_estudiante(codigo, nombre, fecha_nacimiento, direccion, tipo_id, id_num, correo, contrasena)
            flash('Estudiante creado exitosamente', 'success')
            return redirect(url_for('config_academica.listar_estudiantes'))
        except Exception as e:
            flash(f'Error al crear estudiante: {str(e)}', 'error')
            
    # GET renders the same list but with a form to create
    return redirect(url_for('config_academica.listar_estudiantes'))


@config_academica_bp.route('/configuracion/estudiantes/<codigo>/editar', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def editar_estudiante(codigo):
    """GET: formulario con datos actuales. POST: actualiza el estudiante."""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            fecha_nacimiento = request.form['fecha_nacimiento']
            direccion = request.form['direccion']
            estado = request.form['estado']
            
            srv.actualizar_estudiante(codigo, nombre, fecha_nacimiento, direccion, estado)
            flash('Estudiante actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar estudiante: {str(e)}', 'error')
            
        return redirect(url_for('config_academica.listar_estudiantes'))
        
    return redirect(url_for('config_academica.listar_estudiantes', tab='actualizar', codigo_cargar=codigo))


@config_academica_bp.route('/configuracion/estudiantes/<codigo>/desactivar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def desactivar_estudiante(codigo):
    """Desactiva estudiante y su usuario (estado = INACTIVO)."""
    try:
        srv.desactivar_estudiante(codigo)
        flash('Estudiante desactivado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al desactivar estudiante: {str(e)}', 'error')
    return redirect(url_for('config_academica.listar_estudiantes'))


# --- Programas Academicos ---

@config_academica_bp.route('/configuracion/programas')
@rol_requerido('SUPERVISOR')
def listar_programas():
    """Muestra lista de programas academicos con tabs y filtros."""
    tab = request.args.get('tab', 'buscar')
    facultad_filtro = request.args.get('facultad')
    modo_filtro = request.args.get('modo')

    nombre_cargar = request.args.get('nombre_cargar')
    programa_edit = None
    if nombre_cargar and tab == 'actualizar':
        programa_edit = srv.obtener_programa(nombre_cargar)
        if not programa_edit:
            flash(f'Programa "{nombre_cargar}" no encontrado.', 'error')

    programas = srv.listar_programas(facultad=facultad_filtro, modo=modo_filtro)
    return render_template('configuracion/programas.html',
                           programas=programas,
                           tab=tab,
                           programa_edit=programa_edit,
                           facultad_filtro=facultad_filtro,
                           modo_filtro=modo_filtro)


@config_academica_bp.route('/configuracion/programas/crear', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def crear_programa():
    """GET: formulario. POST: crea el programa academico."""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            facultad = request.form['facultad']
            modo = request.form['modo']
            duracion = request.form['duracion']
            
            srv.crear_programa(nombre, facultad, modo, duracion)
            flash('Programa creado exitosamente. Agregue asignaturas al plan de estudio.', 'success')
            return redirect(url_for('config_academica.listar_plan_estudio', programa=nombre))
        except Exception as e:
            flash(f'Error al crear programa: {str(e)}', 'error')
            
    return redirect(url_for('config_academica.listar_programas'))


@config_academica_bp.route('/configuracion/programas/<nombre>/editar', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def editar_programa(nombre):
    """GET: formulario con datos actuales. POST: actualiza el programa."""
    if request.method == 'POST':
        try:
            facultad = request.form['facultad']
            modo = request.form['modo']
            duracion = request.form['duracion']
            
            srv.actualizar_programa(nombre, facultad, modo, duracion)
            flash('Programa actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar programa: {str(e)}', 'error')
            
        return redirect(url_for('config_academica.listar_programas'))
        
    return redirect(url_for('config_academica.listar_programas', tab='actualizar', nombre_cargar=nombre))


@config_academica_bp.route('/configuracion/programas/<nombre>/desactivar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def desactivar_programa(nombre):
    """Desactiva el programa academico (estado = INACTIVO)."""
    flash('El esquema de base de datos actual no soporta desactivar o eliminar un programa.', 'warning')
    return redirect(url_for('config_academica.listar_programas'))


# --- Asignaturas ---

@config_academica_bp.route('/configuracion/asignaturas')
@rol_requerido('SUPERVISOR')
def listar_asignaturas():
    """Muestra lista de asignaturas con opciones de CRUD y busqueda."""
    codigo = request.args.get('codigo')
    nombre = request.args.get('nombre')
    tipo = request.args.get('tipo')
    tab = request.args.get('tab', 'buscar')
    pagina = int(request.args.get('pagina', 1))

    codigo_cargar = request.args.get('codigo_cargar')
    asignatura_edit = None
    if codigo_cargar and tab == 'actualizar':
        asignatura_edit = srv.obtener_asignatura(codigo_cargar)
        if not asignatura_edit:
            flash(f'Asignatura con código {codigo_cargar} no encontrada.', 'error')

    # Eliminar: cargar asignatura para confirmar
    codigo_eliminar = request.args.get('codigo_eliminar')
    asignatura_eliminar = None
    if codigo_eliminar and tab == 'eliminar':
        asignatura_eliminar = srv.obtener_asignatura(codigo_eliminar)
        if not asignatura_eliminar:
            flash(f'Asignatura con código {codigo_eliminar} no encontrada.', 'error')

    asignaturas = srv.listar_asignaturas(codigo, nombre, tipo, limit=20, offset=(pagina - 1) * 20)
    programas = srv.listar_programas()
    return render_template('configuracion/asignaturas.html',
                           asignaturas=asignaturas,
                           programas=programas,
                           tab=tab,
                           pagina=pagina,
                           asignatura_edit=asignatura_edit,
                           asignatura_eliminar=asignatura_eliminar,
                           codigo_filtro=codigo, nombre_filtro=nombre, tipo_filtro=tipo)


@config_academica_bp.route('/configuracion/asignaturas/crear', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def crear_asignatura():
    """GET: formulario con datalist de programas. POST: crea asignatura y la asigna a plan de estudio."""
    if request.method == 'POST':
        try:
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            creditos = request.form['creditos']
            descripcion = request.form['descripcion']
            tipo = request.form['tipo']
            prog_academico = request.form['prog_academico']
            semestre = request.form['semestre']
            
            srv.crear_asignatura(codigo, nombre, creditos, descripcion, tipo, prog_academico, semestre)
            flash('Asignatura creada y asignada exitosamente', 'success')
            return redirect(url_for('config_academica.listar_asignaturas'))
        except Exception as e:
            flash(f'Error al crear asignatura: {str(e)}', 'error')
            
    return redirect(url_for('config_academica.listar_asignaturas'))


@config_academica_bp.route('/configuracion/asignaturas/<codigo>/editar', methods=['GET', 'POST'])
@rol_requerido('SUPERVISOR')
def editar_asignatura(codigo):
    """GET: formulario con datos actuales. POST: actualiza la asignatura."""
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            creditos = request.form['creditos']
            descripcion = request.form['descripcion']
            tipo = request.form['tipo']
            
            srv.actualizar_asignatura(codigo, nombre, creditos, descripcion, tipo)
            flash('Asignatura actualizada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar asignatura: {str(e)}', 'error')
            
        return redirect(url_for('config_academica.listar_asignaturas'))
        
    return redirect(url_for('config_academica.listar_asignaturas', tab='actualizar', codigo_cargar=codigo))


@config_academica_bp.route('/configuracion/asignaturas/<codigo>/eliminar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def eliminar_asignatura(codigo):
    """Elimina la asignatura y la remueve de todos los planes de estudio."""
    try:
        srv.eliminar_asignatura(codigo)
        flash('Asignatura eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar asignatura: {str(e)}', 'error')
    return redirect(url_for('config_academica.listar_asignaturas'))


# --- Plan de Estudio ---

@config_academica_bp.route('/configuracion/plan-estudio')
@rol_requerido('SUPERVISOR')
def listar_plan_estudio():
    """Muestra plan de estudio: programa > semestre > asignaturas con creditos."""
    programas = srv.listar_programas()
    prog_seleccionado = request.args.get('programa')

    plan_estudio = []
    asignaturas_disp = []

    asignatura_edit = None
    cod_editar = request.args.get('editar')

    if prog_seleccionado:
        if not srv.obtener_programa(prog_seleccionado):
            flash('Programa académico no encontrado.', 'error')
            prog_seleccionado = None
        else:
            plan_estudio = srv.listar_plan_estudio(prog_seleccionado)
            asignaturas_disp = srv.listar_asignaturas(limit=500)
            if cod_editar:
                for a in plan_estudio:
                    if a['codigo'].strip() == cod_editar.strip():
                        asignatura_edit = a
                        break

    return render_template('configuracion/plan_estudio.html',
                           programas=programas,
                           prog_seleccionado=prog_seleccionado,
                           plan_estudio=plan_estudio,
                           asignaturas=asignaturas_disp,
                           asignatura_edit=asignatura_edit)


@config_academica_bp.route('/configuracion/plan-estudio/asignar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def asignar_asignatura_plan():
    """Asigna una asignatura existente a un programa con su semestre."""
    try:
        prog_academico = request.form['prog_academico']
        cod_asignatura = request.form['cod_asignatura'].strip()
        semestre = request.form['semestre']

        if not srv.obtener_asignatura(cod_asignatura):
            flash('Asignatura no existente.', 'error')
            return redirect(url_for('config_academica.listar_plan_estudio', programa=prog_academico))

        srv.asignar_asignatura_plan(prog_academico, cod_asignatura, semestre)
        flash('Asignatura agregada al plan de estudio', 'success')
    except Exception as e:
        flash(f'Error al asignar asignatura: {str(e)}', 'error')
        
    return redirect(url_for('config_academica.listar_plan_estudio', programa=request.form.get('prog_academico')))


@config_academica_bp.route('/configuracion/plan-estudio/actualizar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def actualizar_asignatura_plan():
    """Actualiza semestre, créditos y tipo de una asignatura en el plan."""
    try:
        prog_academico = request.form['prog_academico']
        cod_asignatura = request.form['cod_asignatura']
        semestre = request.form['semestre']
        creditos = request.form['creditos']
        tipo = request.form['tipo']

        srv.actualizar_asignatura_en_plan(prog_academico, cod_asignatura, semestre, creditos, tipo)
        flash('Asignatura actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar: {str(e)}', 'error')

    return redirect(url_for('config_academica.listar_plan_estudio', programa=request.form.get('prog_academico')))


@config_academica_bp.route('/configuracion/plan-estudio/eliminar', methods=['POST'])
@rol_requerido('SUPERVISOR')
def eliminar_asignatura_plan():
    """Remueve una asignatura de un plan de estudio especifico."""
    try:
        prog_academico = request.form['prog_academico']
        cod_asignatura = request.form['cod_asignatura']
        
        srv.eliminar_asignatura_plan(prog_academico, cod_asignatura)
        flash('Asignatura removida del plan de estudio', 'success')
    except Exception as e:
        flash(f'Error al remover asignatura: {str(e)}', 'error')
        
    return redirect(url_for('config_academica.listar_plan_estudio', programa=request.form.get('prog_academico')))
