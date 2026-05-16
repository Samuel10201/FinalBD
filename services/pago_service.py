from models.db import get_connection, close_connection


def registrar_pago(cod_estudiante, monto, metodo, codigo_servicio, cod_periodo, id_usuario):
    """Crea pago + movimiento en cuenta corriente en una transaccion BEGIN/COMMIT.
    Estado inicial del pago: PENDIENTE."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pago (estado, metodo, monto) VALUES ('PENDIENTE', %s, %s) RETURNING id",
                    (metodo, monto)
                )
                pago_id = cur.fetchone()['id']

                descripcion = f"Pago mediante {metodo.lower()}"
                cur.execute(
                    """
                    INSERT INTO cuenta_corriente
                    (descripcion_mov, valor, cod_estudiante, id_usuario, codigo_servicio, codigo_periodo, id_pago)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (descripcion, monto, cod_estudiante, id_usuario, codigo_servicio, cod_periodo, pago_id)
                )
                return pago_id
    finally:
        close_connection(conn)

def obtener_servicios_pago():
    """Obtiene los servicios del grupo PAGO para los selects."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT codigo, descripcion FROM servicio WHERE grupo = 'PAGO' AND estado = 'ACTIVO'")
            return cur.fetchall()
    finally:
        close_connection(conn)


def confirmar_pago(id_pago):
    """Cambia el estado del pago a COMPLETADO."""
    pass


def anular_pago(id_pago):
    """Cambia el estado del pago a ANULADO. No se elimina el registro."""
    pass


def obtener_pago(id_pago):
    """Retorna un pago por su id."""
    pass


def listar_pagos(cod_estudiante):
    """Retorna todos los pagos de un estudiante."""
    pass
