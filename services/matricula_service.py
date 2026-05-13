from models.db import get_connection, close_connection
from decimal import Decimal


# ===================== EXCEPCIONES PERSONALIZADAS =====================

class MatriculaException(Exception):
    """Excepción base para errores de matrícula"""
    pass


class EstudianteNoExisteException(MatriculaException):
    """El estudiante no existe o no está activo"""
    pass


class ProgramaNoExisteException(MatriculaException):
    """El programa académico no existe"""
    pass


class PeriodoNoExisteException(MatriculaException):
    """El período no existe o no está activo"""
    pass


class MatriculaDuplicadaException(MatriculaException):
    """El estudiante ya está matriculado en ese programa/período"""
    pass


class CostoNoDefinidoException(MatriculaException):
    """No existe costo definido para programa+período"""
    pass


class ServicioNoExisteException(MatriculaException):
    """Código de servicio (PMAT, PCRE) no existe"""
    pass


# ===================== FUNCIONES DE CONSULTA PARA FORMULARIOS =====================

def obtener_estudiantes_activos():
    """Retorna lista de estudiantes ACTIVOS para autocompletado.
    
    Retorna:
        list: Lista de diccionarios {'codigo': '...', 'nombre': '...'}
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT codigo, nombre 
                FROM estudiante 
                WHERE estado = 'ACTIVO'
                ORDER BY nombre ASC
            """)
            resultado = [dict(row) for row in cur.fetchall()]
        return resultado
    finally:
        close_connection(conn)


def obtener_programas_activos():
    """Retorna lista de programas ACTIVOS para autocompletado.
    
    Retorna:
        list: Lista de diccionarios {'nombre': '...', 'duracion': ...}
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nombre, duracion 
                FROM programa_academico 
                ORDER BY nombre ASC
            """)
            resultado = [dict(row) for row in cur.fetchall()]
        return resultado
    finally:
        close_connection(conn)


def obtener_periodos_activos():
    """Retorna lista de períodos ACTIVOS para autocompletado.
    
    Retorna:
        list: Lista de diccionarios {'codigo': '...', 'descripcion': '...'}
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT codigo, descripcion 
                FROM periodo 
                WHERE estado = 'ACTIVO'
                ORDER BY codigo DESC
            """)
            resultado = [dict(row) for row in cur.fetchall()]
        return resultado
    finally:
        close_connection(conn)


def obtener_datos_formulario_individual():
    """Retorna todas las listas necesarias para el formulario de matrícula individual.
    
    Retorna:
        dict: {'estudiantes': [...], 'programas': [...], 'periodos': [...]}
    """
    return {
        'estudiantes': obtener_estudiantes_activos(),
        'programas': obtener_programas_activos(),
        'periodos': obtener_periodos_activos()
    }


# ===================== FUNCIÓN PRINCIPAL: CREAR MATRÍCULA INDIVIDUAL =====================

def crear_matricula_individual(cod_estudiante, prog_acad, cod_periodo, modalidad, semestre, tipo_id_usuario, id_usuario):
    """Crea una matrícula individual y genera el cobro en cuenta_corriente.
    
    Garantiza atomicidad: si algo falla, todo se revierte (ROLLBACK).
    
    Args:
        cod_estudiante (str): Código del estudiante (ej: '00123456')
        prog_acad (str): Nombre del programa académico (ej: 'Ingenieria de Sistemas')
        cod_periodo (str): Código del período (ej: '202210')
        modalidad (str): 'GLOBAL' o 'CREDITO'
        semestre (int): Semestre a cursar (1-12)
        tipo_id_usuario (str): Tipo ID del usuario autenticado (ej: 'CC')
        id_usuario (str): ID del usuario autenticado (ej: '1234567890')
    
    Retorna:
        dict: {
            'matricula_id': int,
            'estudiante': str,
            'programa': str,
            'periodo': str,
            'modalidad': str,
            'semestre': int,
            'monto_cobrado': Decimal
        }
    
    Raises:
        Excepciones personalizadas (MatriculaDuplicadaException, CostoNoDefinidoException, etc.)
    """
    conn = get_connection()
    try:
        with conn:  # Context manager para transacción automática
            with conn.cursor() as cur:
                # 1. Verificar que estudiante existe y está ACTIVO
                cur.execute(
                    "SELECT nombre FROM estudiante WHERE codigo = %s AND estado = 'ACTIVO'",
                    (cod_estudiante,)
                )
                est = cur.fetchone()
                if not est:
                    raise EstudianteNoExisteException(f"Estudiante {cod_estudiante} no existe o está inactivo")
                nombre_est = est[0]
                
                # 2. Verificar que programa existe
                cur.execute(
                    "SELECT duracion FROM programa_academico WHERE nombre = %s",
                    (prog_acad,)
                )
                prog = cur.fetchone()
                if not prog:
                    raise ProgramaNoExisteException(f"Programa '{prog_acad}' no existe")
                duracion = prog[0]
                
                # 3. Verificar que período existe y está ACTIVO
                cur.execute(
                    "SELECT codigo FROM periodo WHERE codigo = %s AND estado = 'ACTIVO'",
                    (cod_periodo,)
                )
                if not cur.fetchone():
                    raise PeriodoNoExisteException(f"Período {cod_periodo} no existe o está inactivo")
                
                # 4. Validar semestre dentro de rango válido
                if semestre < 1 or semestre > duracion:
                    raise MatriculaException(f"Semestre {semestre} inválido. Programa tiene {duracion} semestres")
                
                # 5. Verificar UNIQUE(cod_estudiante, cod_periodo, prog_acad)
                cur.execute(
                    """SELECT id FROM matricula 
                       WHERE cod_estudiante = %s AND cod_periodo = %s AND prog_acad = %s""",
                    (cod_estudiante, cod_periodo, prog_acad)
                )
                if cur.fetchone():
                    raise MatriculaDuplicadaException(
                        f"Estudiante {cod_estudiante} ya está matriculado en {prog_acad} para el período {cod_periodo}"
                    )
                
                # 6. Obtener costo definido para (programa, período)
                cur.execute(
                    """SELECT costo_global, costo_credito FROM costo 
                       WHERE prog_academico = %s AND cod_periodo = %s""",
                    (prog_acad, cod_periodo)
                )
                costo = cur.fetchone()
                if not costo:
                    raise CostoNoDefinidoException(
                        f"No hay costo definido para {prog_acad} en período {cod_periodo}"
                    )
                costo_global, costo_credito = Decimal(costo[0]), Decimal(costo[1])
                
                # 7. Calcular monto a cobrar
                if modalidad == 'GLOBAL':
                    monto_cobro = costo_global
                    codigo_servicio = 'PMAT'
                elif modalidad == 'CREDITO':
                    # Obtener suma de créditos para asignaturas del semestre
                    cur.execute(
                        """SELECT SUM(a.creditos) FROM plan_estudio ps
                           JOIN asignatura a ON ps.cod_asignatura = a.codigo
                           WHERE ps.nombre_programa = %s AND ps.semestre = %s""",
                        (prog_acad, semestre)
                    )
                    total_creditos_row = cur.fetchone()
                    total_creditos = total_creditos_row[0] if total_creditos_row[0] else 0
                    monto_cobro = Decimal(total_creditos) * costo_credito
                    codigo_servicio = 'PCRE'
                else:
                    raise MatriculaException(f"Modalidad '{modalidad}' no válida")
                
                # 8. Verificar que código de servicio existe
                cur.execute(
                    """SELECT codigo FROM servicio 
                       WHERE codigo = %s AND grupo = 'COBRO' AND estado = 'ACTIVO'""",
                    (codigo_servicio,)
                )
                if not cur.fetchone():
                    raise ServicioNoExisteException(
                        f"Código de servicio '{codigo_servicio}' no existe o está inactivo"
                    )
                
                # 9. INSERT en matricula
                cur.execute(
                    """INSERT INTO matricula (modalidad, semestre, cod_estudiante, cod_periodo, prog_acad)
                       VALUES (%s, %s, %s, %s, %s)
                       RETURNING id""",
                    (modalidad, semestre, cod_estudiante, cod_periodo, prog_acad)
                )
                matricula_id = cur.fetchone()[0]
                
                # 10. INSERT en cuenta_corriente (cobro)
                descripcion = f"Matrícula {prog_acad} - Período {cod_periodo} - {modalidad}"
                cur.execute(
                    """INSERT INTO cuenta_corriente 
                       (descripcion_mov, valor, cod_estudiante, tipo_id_usuario, id_usuario, 
                        codigo_servicio, codigo_periodo, id_pago)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)""",
                    (descripcion, monto_cobro, cod_estudiante, tipo_id_usuario, id_usuario,
                     codigo_servicio, cod_periodo)
                )
                
        # Transacción completada exitosamente (COMMIT automático)
        return {
            'matricula_id': matricula_id,
            'estudiante': nombre_est,
            'programa': prog_acad,
            'periodo': cod_periodo,
            'modalidad': modalidad,
            'semestre': semestre,
            'monto_cobrado': monto_cobro
        }
        
    except MatriculaException:
        raise
    except Exception as e:
        raise MatriculaException(f"Error inesperado al crear matrícula: {str(e)}")
    finally:
        close_connection(conn)


# ===================== MATRÍCULA MASIVA =====================

def obtener_estudiantes_para_masiva(prog_acad, cod_periodo_destino):
    """Retorna vista previa de estudiantes que serán inscritos en matrícula masiva.
    
    Args:
        prog_acad (str): Programa académico
        cod_periodo_destino (str): Período destino (siguiente)
    
    Retorna:
        dict: {
            'vista_previa': [
                {'cod_estudiante': '...', 'nombre': '...', 'semestre_actual': int, 
                 'nuevo_semestre': int, 'modalidad': '...', 'puede_inscribir': bool}
            ],
            'total_a_inscribir': int,
            'total_excluidos': int,
            'mensaje': str (si hay error)
        }
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Obtener duracion del programa
            cur.execute(
                "SELECT duracion FROM programa_academico WHERE nombre = %s",
                (prog_acad,)
            )
            prog = cur.fetchone()
            if not prog:
                return {'vista_previa': [], 'total_a_inscribir': 0, 'total_excluidos': 0,
                        'mensaje': f"Programa '{prog_acad}' no existe"}
            duracion = prog[0]
            
            # Encontrar el período anterior (más reciente)
            # Esto es complejo porque necesitamos deducir el período anterior
            # Estrategia: buscar el período más reciente (antes del destino) con matrículas en el programa
            cur.execute(
                """SELECT DISTINCT cod_periodo FROM matricula 
                   WHERE prog_acad = %s AND cod_periodo < %s
                   ORDER BY cod_periodo DESC
                   LIMIT 1""",
                (prog_acad, cod_periodo_destino)
            )
            periodo_anterior = cur.fetchone()
            if not periodo_anterior:
                return {'vista_previa': [], 'total_a_inscribir': 0, 'total_excluidos': 0,
                        'mensaje': f"No hay estudiantes del programa {prog_acad} en períodos anteriores"}
            periodo_anterior = periodo_anterior[0]
            
            # Obtener estudiantes activos con matrícula en programa y periodo anterior
            cur.execute(
                """SELECT DISTINCT m.cod_estudiante, e.nombre, m.semestre, m.modalidad
                   FROM matricula m
                   JOIN estudiante e ON m.cod_estudiante = e.codigo
                   WHERE m.prog_acad = %s AND m.cod_periodo = %s AND e.estado = 'ACTIVO'
                   ORDER BY e.nombre ASC""",
                (prog_acad, periodo_anterior)
            )
            estudiantes = [
                {
                    'cod_estudiante': row[0],
                    'nombre': row[1],
                    'semestre_actual': row[2],
                    'nuevo_semestre': row[2] + 1,
                    'modalidad': row[3],
                    'puede_inscribir': row[2] < duracion  # Excluir si está en último semestre
                }
                for row in cur.fetchall()
            ]
            
        total_a_inscribir = sum(1 for e in estudiantes if e['puede_inscribir'])
        total_excluidos = sum(1 for e in estudiantes if not e['puede_inscribir'])
        
        return {
            'vista_previa': estudiantes,
            'total_a_inscribir': total_a_inscribir,
            'total_excluidos': total_excluidos,
            'periodo_anterior': periodo_anterior,
            'periodo_destino': cod_periodo_destino
        }
        
    except Exception as e:
        return {'vista_previa': [], 'total_a_inscribir': 0, 'total_excluidos': 0,
                'mensaje': f"Error: {str(e)}"}
    finally:
        close_connection(conn)


def crear_matriculas_masivas(prog_acad, cod_periodo_destino, tipo_id_usuario, id_usuario):
    """Crea matrículas masivas para todos los estudiantes activos del programa.
    
    Args:
        prog_acad (str): Programa académico
        cod_periodo_destino (str): Período destino
        tipo_id_usuario (str): Usuario autenticado
        id_usuario (str): Usuario autenticado
    
    Retorna:
        dict: {
            'total_creadas': int,
            'total_excluidas': int,
            'errores': [{'cod_estudiante': '...', 'error': '...'}],
            'monto_total_cobrado': Decimal
        }
    """
    resultado = {
        'total_creadas': 0,
        'total_excluidas': 0,
        'errores': [],
        'monto_total_cobrado': Decimal('0')
    }
    
    # Obtener vista previa
    preview = obtener_estudiantes_para_masiva(prog_acad, cod_periodo_destino)
    
    if preview.get('mensaje'):
        return {**resultado, 'mensaje_error': preview['mensaje']}
    
    # Para cada estudiante, intentar crear matrícula
    for est in preview['vista_previa']:
        if not est['puede_inscribir']:
            resultado['total_excluidas'] += 1
            continue
        
        try:
            matricula = crear_matricula_individual(
                cod_estudiante=est['cod_estudiante'],
                prog_acad=prog_acad,
                cod_periodo=cod_periodo_destino,
                modalidad=est['modalidad'],
                semestre=est['nuevo_semestre'],
                tipo_id_usuario=tipo_id_usuario,
                id_usuario=id_usuario
            )
            resultado['total_creadas'] += 1
            resultado['monto_total_cobrado'] += matricula['monto_cobrado']
        except MatriculaException as e:
            resultado['errores'].append({
                'cod_estudiante': est['cod_estudiante'],
                'error': str(e)
            })
    
    return resultado
