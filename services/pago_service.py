from models.db import get_connection, close_connection


def registrar_pago(cod_estudiante, monto, metodo, codigo_servicio, cod_periodo, id_usuario, tipo_id_usuario):
    """Crea pago + movimiento en cuenta corriente en una transaccion BEGIN/COMMIT.
    Estado inicial del pago: PENDIENTE."""
    pass


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
