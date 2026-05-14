from flask import Blueprint, render_template, request, redirect, session, flash
from services import matricula_service

matricula_bp = Blueprint('matricula', __name__)


# ===================== MIDDLEWARE DE AUTORIZACIÓN =====================

def verificar_acceso_asistente():
    """Verifica que el usuario tiene rol ASISTENTE o ADMINISTRADOR."""
    if 'usuario' not in session:
        return redirect('/login')

    rol = session['usuario']['rol']
    if rol == 'ADMINISTRADOR':
        return None

    if rol != 'ASISTENTE':
        flash('Acceso denegado. Solo ASISTENTE puede acceder a matricula.', 'error')
        return redirect('/')

    return None


# ===================== MATRÍCULA INDIVIDUAL =====================

@matricula_bp.route('/matricula/individual', methods=['GET', 'POST'])
def individual():
    """GET: formulario con datalist de estudiantes, programas, periodos.
    POST: crea matricula y genera cobros en cuenta corriente."""
    
    # Verificar acceso
    acceso = verificar_acceso_asistente()
    if acceso:
        return acceso
    
    if request.method == 'GET':
        # Obtener listas para los dropdowns/datalist
        datos = matricula_service.obtener_datos_formulario_individual()
        return render_template('matricula/individual.html', **datos)
    
    elif request.method == 'POST':
        try:
            # Extraer datos del formulario
            cod_estudiante = request.form.get('cod_estudiante', '').strip()
            prog_acad = request.form.get('prog_acad', '').strip()
            cod_periodo = request.form.get('cod_periodo', '').strip()
            modalidad = request.form.get('modalidad', '').strip()
            semestre_str = request.form.get('semestre', '').strip()
            
            # Validaciones básicas
            if not all([cod_estudiante, prog_acad, cod_periodo, modalidad, semestre_str]):
                flash('Todos los campos son obligatorios.', 'error')
                datos = matricula_service.obtener_datos_formulario_individual()
                return render_template('matricula/individual.html', **datos), 400
            
            try:
                semestre = int(semestre_str)
            except ValueError:
                flash('Semestre debe ser un número.', 'error')
                datos = matricula_service.obtener_datos_formulario_individual()
                return render_template('matricula/individual.html', **datos), 400
            
            # Crear matrícula
            resultado = matricula_service.crear_matricula_individual(
                cod_estudiante=cod_estudiante,
                prog_acad=prog_acad,
                cod_periodo=cod_periodo,
                modalidad=modalidad,
                semestre=semestre,
                tipo_id_usuario=session['usuario']['tipo_id'],
                id_usuario=session['usuario']['id']
            )
            
            # Éxito
            flash(
                f"✓ Matrícula creada exitosamente (ID: {resultado['matricula_id']}). "
                f"Cobro de ${resultado['monto_cobrado']} registrado.",
                'success'
            )
            
            return render_template(
                'matricula/individual.html',
                resultado_exitoso=resultado,
                **matricula_service.obtener_datos_formulario_individual()
            )
        
        except matricula_service.EstudianteNoExisteException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.ProgramaNoExisteException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.PeriodoNoExisteException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.MatriculaDuplicadaException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.CostoNoDefinidoException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.ServicioNoExisteException as e:
            flash(f"Error: {str(e)}", 'error')
        except matricula_service.MatriculaException as e:
            flash(f"Error: {str(e)}", 'error')
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", 'error')
        
        # Mostrar formulario nuevamente con el error
        datos = matricula_service.obtener_datos_formulario_individual()
        return render_template('matricula/individual.html', **datos), 400


# ===================== MATRÍCULA MASIVA =====================

@matricula_bp.route('/matricula/masiva', methods=['GET', 'POST'])
def masiva():
    """GET: formulario para seleccionar programa y mostrar vista previa.
    POST: genera matriculas para periodo siguiente (semestre+1) para todos los estudiantes activos."""
    
    # Verificar acceso
    acceso = verificar_acceso_asistente()
    if acceso:
        return acceso
    
    if request.method == 'GET':
        # Mostrar formulario con listas
        programas = matricula_service.obtener_programas_activos()
        periodos = matricula_service.obtener_periodos_activos()
        return render_template('matricula/masiva.html', programas=programas, periodos=periodos)
    
    elif request.method == 'POST':
        try:
            prog_acad = request.form.get('prog_acad', '').strip()
            cod_periodo_destino = request.form.get('cod_periodo_destino', '').strip()
            action = request.form.get('action', '').strip()
            
            if not all([prog_acad, cod_periodo_destino]):
                flash('Programa y período destino son obligatorios.', 'error')
                programas = matricula_service.obtener_programas_activos()
                periodos = matricula_service.obtener_periodos_activos()
                return render_template('matricula/masiva.html', programas=programas, periodos=periodos), 400
            
            if action == 'preview':
                # Mostrar vista previa (sin crear nada)
                preview = matricula_service.obtener_estudiantes_para_masiva(
                    prog_acad=prog_acad,
                    cod_periodo_destino=cod_periodo_destino
                )
                
                if preview.get('mensaje'):
                    flash(f"Aviso: {preview['mensaje']}", 'warning')
                
                programas = matricula_service.obtener_programas_activos()
                periodos = matricula_service.obtener_periodos_activos()
                
                return render_template(
                    'matricula/masiva.html',
                    programas=programas,
                    periodos=periodos,
                    preview_data=preview,
                    prog_acad_seleccionado=prog_acad,
                    cod_periodo_destino_seleccionado=cod_periodo_destino
                )
            
            elif action == 'crear':
                # Crear realmente las matrículas masivas
                resultado = matricula_service.crear_matriculas_masivas(
                    prog_acad=prog_acad,
                    cod_periodo_destino=cod_periodo_destino,
                    tipo_id_usuario=session['usuario']['tipo_id'],
                    id_usuario=session['usuario']['id']
                )
                
                if resultado.get('mensaje_error'):
                    flash(f"Error: {resultado['mensaje_error']}", 'error')
                else:
                    flash(
                        f"✓ Matrículas creadas: {resultado['total_creadas']}. "
                        f"Excluidas (último semestre): {resultado['total_excluidas']}. "
                        f"Monto total cobrado: ${resultado['monto_total_cobrado']}",
                        'success'
                    )
                    
                    if resultado['errores']:
                        msg_errores = ", ".join([e['cod_estudiante'] for e in resultado['errores']])
                        flash(f"⚠ Errores en: {msg_errores}", 'warning')
                
                # Volver al formulario inicial
                programas = matricula_service.obtener_programas_activos()
                periodos = matricula_service.obtener_periodos_activos()
                return render_template('matricula/masiva.html', programas=programas, periodos=periodos)
            
            else:
                flash('Acción no reconocida.', 'error')
                programas = matricula_service.obtener_programas_activos()
                periodos = matricula_service.obtener_periodos_activos()
                return render_template('matricula/masiva.html', programas=programas, periodos=periodos), 400
        
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", 'error')
            programas = matricula_service.obtener_programas_activos()
            periodos = matricula_service.obtener_periodos_activos()
            return render_template('matricula/masiva.html', programas=programas, periodos=periodos), 400
