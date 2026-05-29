from models.db import get_connection, close_connection


def registrar_cargo(cod_estudiante, monto, codigo_servicio, cod_periodo, id_usuario):
    """Crea un movimiento de COBRO en cuenta corriente (sin pago asociado).
    Permite cargar al estudiante servicios distintos a la matricula
    (carnet, laboratorio, examen supletorio, etc.)."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT descripcion FROM servicio WHERE codigo = %s AND grupo = 'COBRO' AND estado = 'ACTIVO'",
                    (codigo_servicio,)
                )
                servicio = cur.fetchone()
                if not servicio:
                    raise Exception("El concepto seleccionado no es un servicio de cobro valido.")

                descripcion = f"{servicio['descripcion']} {cod_periodo}"
                cur.execute(
                    """
                    INSERT INTO cuenta_corriente
                    (descripcion_mov, valor, cod_estudiante, id_usuario, codigo_servicio, codigo_periodo, id_pago)
                    VALUES (%s, %s, %s, %s, %s, %s, NULL)
                    RETURNING id
                    """,
                    (descripcion, monto, cod_estudiante, id_usuario, codigo_servicio, cod_periodo)
                )
                return cur.fetchone()['id']
    finally:
        close_connection(conn)


def obtener_servicios_cobro():
    """Obtiene los servicios del grupo COBRO para los selects."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, descripcion FROM servicio WHERE grupo = 'COBRO' AND estado = 'ACTIVO'")
            return cur.fetchall()
    finally:
        close_connection(conn)
