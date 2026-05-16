from models.db import get_connection, close_connection
from psycopg2.extras import DictCursor


def get_estudiante_perfil(codigo_estudiante):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT codigo, nombre, estado, fecha_nacimiento, direccion
                FROM estudiante
                WHERE codigo = %s
            """, (codigo_estudiante,))
            estudiante = cur.fetchone()

            if not estudiante:
                return None

            cur.execute("""
                SELECT m.prog_acad, m.semestre, m.modalidad, m.cod_periodo, p.descripcion as desc_periodo
                FROM matricula m
                JOIN periodo p ON m.cod_periodo = p.codigo
                WHERE m.cod_estudiante = %s
                ORDER BY m.fecha_creacion DESC
                LIMIT 1
            """, (codigo_estudiante,))
            matricula = cur.fetchone()

            plan_estudio = []
            if matricula:
                cur.execute("""
                    SELECT pe.semestre, a.codigo, a.nombre, a.creditos, a.tipo
                    FROM plan_estudio pe
                    JOIN asignatura a ON pe.cod_asignatura = a.codigo
                    WHERE pe.nombre_programa = %s
                    ORDER BY pe.semestre ASC, a.nombre ASC
                """, (matricula['prog_acad'],))

                materias = cur.fetchall()

                semestres = {}
                for mat in materias:
                    s = mat['semestre']
                    if s not in semestres:
                        semestres[s] = []
                    semestres[s].append(mat)

                plan_estudio = [{'semestre': k, 'materias': v} for k, v in semestres.items()]

            return {
                'estudiante': estudiante,
                'matricula': matricula,
                'plan_estudio': plan_estudio
            }
    finally:
        close_connection(conn)


def get_reporte_estudiantes_programa(periodo, programa):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT e.codigo, e.nombre, m.modalidad, m.semestre,
                       CASE
                           WHEN m.modalidad = 'GLOBAL' THEN c.costo_global
                           ELSE (
                               SELECT COALESCE(SUM(a.creditos), 0) * c.costo_credito
                               FROM plan_estudio pe
                               JOIN asignatura a ON pe.cod_asignatura = a.codigo
                               WHERE pe.nombre_programa = m.prog_acad AND pe.semestre = m.semestre
                           )
                       END as monto
                FROM matricula m
                JOIN estudiante e ON m.cod_estudiante = e.codigo
                JOIN costo c ON c.prog_academico = m.prog_acad AND c.cod_periodo = m.cod_periodo
                WHERE m.cod_periodo = %s AND m.prog_acad = %s
                ORDER BY e.nombre
            """, (periodo, programa))
            return cur.fetchall()
    finally:
        close_connection(conn)


def get_reporte_ingreso_esperado(periodo, programa):
    estudiantes = get_reporte_estudiantes_programa(periodo, programa)
    total = sum([float(e['monto']) for e in estudiantes if e['monto']])
    return total, estudiantes


def get_reporte_pendientes_pago(periodo, programa):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT e.codigo, e.nombre,
                       ABS(SUM(
                           CASE
                               WHEN s.grupo = 'COBRO' THEN -cc.valor
                               WHEN s.grupo = 'PAGO' THEN cc.valor
                               ELSE 0
                           END
                       )) AS saldo_pendiente
                FROM cuenta_corriente cc
                JOIN estudiante e ON cc.cod_estudiante = e.codigo
                JOIN servicio s ON cc.codigo_servicio = s.codigo
                JOIN matricula m ON m.cod_estudiante = e.codigo AND m.cod_periodo = cc.codigo_periodo
                LEFT JOIN pago p ON cc.id_pago = p.id
                WHERE cc.codigo_periodo = %s
                  AND m.prog_acad = %s
                  AND (cc.id_pago IS NULL OR p.estado <> 'ANULADO')
                GROUP BY e.codigo, e.nombre
                HAVING SUM(
                    CASE
                        WHEN s.grupo = 'COBRO' THEN -cc.valor
                        WHEN s.grupo = 'PAGO' THEN cc.valor
                        ELSE 0
                    END
                ) < 0
                ORDER BY e.nombre
            """, (periodo, programa))
            return cur.fetchall()
    finally:
        close_connection(conn)


def get_reporte_ingreso_real(periodo, programa):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT COALESCE(SUM(cc.valor), 0) AS total_ingreso
                FROM cuenta_corriente cc
                JOIN servicio s ON cc.codigo_servicio = s.codigo
                JOIN matricula m ON m.cod_estudiante = cc.cod_estudiante AND m.cod_periodo = cc.codigo_periodo
                LEFT JOIN pago p ON cc.id_pago = p.id
                WHERE cc.codigo_periodo = %s
                  AND m.prog_acad = %s
                  AND s.grupo = 'PAGO'
                  AND (cc.id_pago IS NULL OR p.estado <> 'ANULADO')
            """, (periodo, programa))
            res = cur.fetchone()
            return float(res['total_ingreso']) if res and res['total_ingreso'] else 0.0
    finally:
        close_connection(conn)


def get_reporte_cartera(periodo, programa):
    pendientes = get_reporte_pendientes_pago(periodo, programa)
    total_cartera = sum([float(p['saldo_pendiente']) for p in pendientes])
    return total_cartera, pendientes


def get_filtros_disponibles():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT codigo, descripcion FROM periodo ORDER BY codigo DESC")
            periodos = cur.fetchall()
            cur.execute("SELECT nombre FROM programa_academico ORDER BY nombre")
            programas = cur.fetchall()
            return periodos, programas
    finally:
        close_connection(conn)
