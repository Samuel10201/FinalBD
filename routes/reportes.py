from flask import Blueprint, render_template, request, session, redirect, flash
from services.reporte_service import (
    get_estudiante_perfil,
    get_filtros_disponibles,
    get_reporte_estudiantes_programa,
    get_reporte_ingreso_esperado,
    get_reporte_pendientes_pago,
    get_reporte_ingreso_real,
    get_reporte_cartera
)
from models.db import get_connection, close_connection
from routes import login_required, rol_requerido

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/estudiante/perfil')
@login_required
def perfil():
    usuario = session['usuario']

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo FROM estudiante WHERE tipo_id = %s AND id = %s",
                        (usuario['tipo_id'], usuario['id']))
            res = cur.fetchone()
            codigo_estudiante = res['codigo'] if res else None
    finally:
        close_connection(conn)

    if not codigo_estudiante:
        flash('No se encontró información del estudiante vinculada a tu cuenta', 'error')
        return redirect('/')

    datos = get_estudiante_perfil(codigo_estudiante)
    
    if not datos or not datos['estudiante']:
        flash('No se encontró el perfil', 'error')
        return redirect('/')
        
    return render_template('estudiante/perfil.html', datos=datos)


@reportes_bp.route('/reportes/estudiantes-programa')
@rol_requerido('SUPERVISOR')
def reporte_estudiantes():

    periodos, programas = get_filtros_disponibles()
    periodo_sel = request.args.get('periodo')
    programa_sel = request.args.get('programa')
    
    resultados = []
    if periodo_sel and programa_sel:
        resultados = get_reporte_estudiantes_programa(periodo_sel, programa_sel)
        
    return render_template('reportes/estudiantes_programa.html', 
                           periodos=periodos, programas=programas,
                           periodo_sel=periodo_sel, programa_sel=programa_sel,
                           resultados=resultados)


@reportes_bp.route('/reportes/ingreso-esperado')
@rol_requerido('SUPERVISOR')
def reporte_esperado():

    periodos, programas = get_filtros_disponibles()
    periodo_sel = request.args.get('periodo')
    programa_sel = request.args.get('programa')
    
    total = 0
    resultados = []
    if periodo_sel and programa_sel:
        total, resultados = get_reporte_ingreso_esperado(periodo_sel, programa_sel)
        
    return render_template('reportes/ingreso_esperado.html',
                           periodos=periodos, programas=programas,
                           periodo_sel=periodo_sel, programa_sel=programa_sel,
                           total=total, resultados=resultados)


@reportes_bp.route('/reportes/pendientes-pago')
@rol_requerido('SUPERVISOR')
def reporte_pendientes():

    periodos, programas = get_filtros_disponibles()
    periodo_sel = request.args.get('periodo')
    programa_sel = request.args.get('programa')
    
    resultados = []
    if periodo_sel and programa_sel:
        resultados = get_reporte_pendientes_pago(periodo_sel, programa_sel)
        
    return render_template('reportes/pendientes_pago.html',
                           periodos=periodos, programas=programas,
                           periodo_sel=periodo_sel, programa_sel=programa_sel,
                           resultados=resultados)


@reportes_bp.route('/reportes/ingreso-real')
@rol_requerido('SUPERVISOR')
def reporte_real():

    periodos, programas = get_filtros_disponibles()
    periodo_sel = request.args.get('periodo')
    programa_sel = request.args.get('programa')
    
    total = 0
    if periodo_sel and programa_sel:
        total = get_reporte_ingreso_real(periodo_sel, programa_sel)
        
    return render_template('reportes/ingreso_real.html',
                           periodos=periodos, programas=programas,
                           periodo_sel=periodo_sel, programa_sel=programa_sel,
                           total=total)


@reportes_bp.route('/reportes/cartera')
@rol_requerido('SUPERVISOR')
def reporte_cartera():

    periodos, programas = get_filtros_disponibles()
    periodo_sel = request.args.get('periodo')
    programa_sel = request.args.get('programa')
    
    total = 0
    resultados = []
    if periodo_sel and programa_sel:
        total, resultados = get_reporte_cartera(periodo_sel, programa_sel)
        
    return render_template('reportes/cartera.html',
                           periodos=periodos, programas=programas,
                           periodo_sel=periodo_sel, programa_sel=programa_sel,
                           total=total, resultados=resultados)
