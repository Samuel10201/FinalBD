from models.db import get_connection, close_connection

def obtener_cuenta(cod_estudiante):
    """Retorna los datos de la cuenta corriente de un estudiante."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, nombre, estado FROM estudiante WHERE codigo = %s", (cod_estudiante,))
            return cur.fetchone()
    finally:
        close_connection(conn)


def listar_movimientos(cod_estudiante, cod_periodo=None):
    """Retorna los movimientos de un estudiante. Opcionalmente filtra por periodo."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT cc.id, cc.fecha, cc.descripcion_mov, cc.valor, s.grupo, cc.codigo_periodo, p.estado as estado_pago
                FROM cuenta_corriente cc
                JOIN servicio s ON cc.codigo_servicio = s.codigo
                LEFT JOIN pago p ON cc.id_pago = p.id
                WHERE cc.cod_estudiante = %s
            """
            params = [cod_estudiante]
            
            if cod_periodo:
                query += " AND cc.codigo_periodo = %s"
                params.append(cod_periodo)
                
            query += " ORDER BY cc.fecha DESC"
            
            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def calcular_saldo(cod_estudiante, cod_periodo=None):
    """Calcula el saldo: suma PAGOS - suma COBROS. Excluye pagos ANULADOS.
    Si el resultado es positivo (o cero), el estudiante esta al dia o tiene saldo a favor.
    Si es negativo, el estudiante debe dinero.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT SUM(
                    CASE
                        WHEN s.grupo = 'PAGO' THEN cc.valor
                        WHEN s.grupo = 'COBRO' THEN -cc.valor
                    END
                ) AS saldo
                FROM cuenta_corriente cc
                JOIN servicio s ON cc.codigo_servicio = s.codigo
                LEFT JOIN pago p ON cc.id_pago = p.id
                WHERE cc.cod_estudiante = %s
                  AND (cc.id_pago IS NULL OR p.estado <> 'ANULADO')
            """
            params = [cod_estudiante]
            
            if cod_periodo:
                query += " AND cc.codigo_periodo = %s"
                params.append(cod_periodo)
                
            cur.execute(query, tuple(params))
            resultado = cur.fetchone()
            
            # Si no hay movimientos, el saldo es 0
            if resultado and resultado['saldo'] is not None:
                return float(resultado['saldo'])
            return 0.0
    finally:
        close_connection(conn)


def obtener_todos_los_periodos():
    """Funcion auxiliar para poblar los selects, por si la Persona 4 aun no lo hace."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, descripcion FROM periodo ORDER BY codigo DESC")
            return cur.fetchall()
    finally:
        close_connection(conn)

def obtener_codigo_estudiante(tipo_id, id_usuario):
    """Obtiene el codigo de estudiante a partir de las credenciales de usuario."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo FROM estudiante WHERE tipo_id = %s AND id = %s", (tipo_id, id_usuario))
            res = cur.fetchone()
            return res['codigo'] if res else None
    finally:
        close_connection(conn)
