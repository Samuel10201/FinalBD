from flask import Blueprint, render_template, request, flash, session, redirect
from services.cuenta_service import listar_movimientos, calcular_saldo, obtener_cuenta, obtener_todos_los_periodos, obtener_codigo_estudiante
from services.config_academica_service import listar_estudiantes

cuenta_corriente_bp = Blueprint('cuenta_corriente', __name__)

@cuenta_corriente_bp.route('/cuenta-corriente/consulta', methods=['GET', 'POST'])
def consulta():
    """Buscar estudiante (datalist) y mostrar movimientos con saldo por periodo."""
    estudiantes = listar_estudiantes()
    periodos = obtener_todos_los_periodos()
    
    movimientos = []
    saldo = 0
    estudiante_seleccionado = None
    periodo_seleccionado = None
    
    if request.method == 'POST':
        cod_estudiante = request.form.get('cod_estudiante', '').strip()
        cod_periodo = request.form.get('cod_periodo')

        if not cod_periodo:
            cod_periodo = None

        import re
        if not cod_estudiante:
            pass
        elif not re.match(r'^[0-9]{2,8}$', cod_estudiante):
            flash('Ingrese el código del estudiante', 'error')
        else:
            estudiante_seleccionado = obtener_cuenta(cod_estudiante)
            if estudiante_seleccionado:
                movimientos = listar_movimientos(cod_estudiante, cod_periodo)
                saldo = calcular_saldo(cod_estudiante, cod_periodo)
                periodo_seleccionado = cod_periodo
            else:
                flash('Ingrese el código del estudiante', 'error')
                
    return render_template(
        'cuenta_corriente/consulta.html', 
        estudiantes=estudiantes, 
        periodos=periodos,
        movimientos=movimientos,
        saldo=saldo,
        estudiante=estudiante_seleccionado,
        periodo_actual=periodo_seleccionado
    )

@cuenta_corriente_bp.route('/estudiante/cuenta')
def cuenta_propia():
    """Mostrar los movimientos y saldo exclusivamente del estudiante en sesión."""
    if 'usuario' not in session:
        flash('Debe iniciar sesión', 'error')
        return redirect('/login')

    usuario = session['usuario']
    es_admin_vista = usuario['rol'] == 'ADMINISTRADOR' and session.get('vista_rol') == 'ESTUDIANTE'

    if usuario['rol'] != 'ESTUDIANTE' and not es_admin_vista:
        flash('Acceso denegado', 'error')
        return redirect('/')

    estudiantes_lista = []
    if es_admin_vista:
        codigo_param = request.args.get('codigo', '').strip()
        if codigo_param:
            session['estudiante_vista'] = codigo_param
        cod_estudiante = session.get('estudiante_vista')
        estudiantes_lista = listar_estudiantes(limit=500)
    else:
        cod_estudiante = obtener_codigo_estudiante(usuario['id'])

    if not cod_estudiante:
        if es_admin_vista:
            return render_template('estudiante/cuenta.html', estudiante=None, movimientos=[], saldo=0,
                                   es_admin_vista=True, estudiantes=estudiantes_lista, codigo_estudiante=None)
        flash('Estudiante no encontrado en el sistema', 'error')
        return redirect('/')

    estudiante = obtener_cuenta(cod_estudiante)
    if not estudiante and es_admin_vista:
        session.pop('estudiante_vista', None)
        flash('Estudiante no encontrado', 'error')
        return render_template('estudiante/cuenta.html', estudiante=None, movimientos=[], saldo=0,
                               es_admin_vista=True, estudiantes=estudiantes_lista, codigo_estudiante=None)

    movimientos = listar_movimientos(cod_estudiante)
    saldo = calcular_saldo(cod_estudiante)

    return render_template(
        'estudiante/cuenta.html',
        estudiante=estudiante,
        movimientos=movimientos,
        saldo=saldo,
        es_admin_vista=es_admin_vista,
        estudiantes=estudiantes_lista,
        codigo_estudiante=cod_estudiante
    )
