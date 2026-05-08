from models.db import get_connection, close_connection


def obtener_cuenta(cod_estudiante):
    """Retorna los datos de la cuenta corriente de un estudiante."""
    pass


def listar_movimientos(cod_estudiante, cod_periodo=None):
    """Retorna los movimientos de un estudiante. Opcionalmente filtra por periodo."""
    pass


def calcular_saldo(cod_estudiante, cod_periodo=None):
    """Calcula el saldo: suma COBROS - suma PAGOS. Excluye pagos ANULADOS."""
    pass


def registrar_cobro_matricula(cod_estudiante, cod_periodo, valor, descripcion, codigo_servicio, id_usuario, tipo_id_usuario):
    """Inserta un movimiento de cobro por matricula en cuenta corriente."""
    pass


def registrar_cobro_servicio(cod_estudiante, cod_periodo, valor, descripcion, codigo_servicio, id_usuario, tipo_id_usuario):
    """Inserta un movimiento de cobro por servicio (examen medico, carnet, etc.) en cuenta corriente."""
    pass
