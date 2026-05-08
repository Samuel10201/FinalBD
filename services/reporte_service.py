from models.db import get_connection, close_connection


def estudiantes_por_programa(cod_periodo, prog_academico):
    """Retorna listado de estudiantes con programa, modalidad y monto."""
    pass


def ingreso_esperado(cod_periodo, prog_academico):
    """Retorna el total que se deberia recaudar (suma de cobros), totalizado."""
    pass


def pendientes_pago(cod_periodo, prog_academico):
    """Retorna estudiantes con saldo pendiente (cobros > pagos)."""
    pass


def ingreso_real(cod_periodo, prog_academico):
    """Retorna el total de pagos recibidos (solo COMPLETADOS)."""
    pass


def cartera(cod_periodo, prog_academico):
    """Retorna estudiantes que deben, valor individual y total cuentas por cobrar."""
    pass
