from models.db import get_connection, close_connection


# --- Periodos ---

def listar_periodos():
    """Retorna lista de todos los periodos academicos."""
    pass


def obtener_periodo(codigo):
    """Retorna un periodo por su codigo."""
    pass


def crear_periodo(codigo, descripcion, fecha_inicio, fecha_fin):
    """Crea un periodo. Valida formato YYYYXX (XX: 00,10,20,30,40) y que no se solape con otros."""
    pass


def actualizar_periodo(codigo, descripcion, fecha_inicio, fecha_fin, estado):
    """Actualiza los datos de un periodo."""
    pass


def desactivar_periodo(codigo):
    """Desactiva un periodo. No permite si tiene matriculas asociadas."""
    pass


def validar_codigo_periodo(codigo):
    """Valida que el codigo tenga 6 digitos y termine en 00, 10, 20, 30 o 40."""
    pass


def validar_fechas_periodo(fecha_inicio, fecha_fin):
    """Valida que las fechas no se solapen con periodos existentes."""
    pass


# --- Servicios (codigos de detalle) ---

def listar_servicios():
    """Retorna lista de todos los servicios."""
    pass


def obtener_servicio(codigo):
    """Retorna un servicio por su codigo."""
    pass


def crear_servicio(codigo, grupo, descripcion):
    """Crea un servicio. Grupo debe ser COBRO o PAGO."""
    pass


def actualizar_servicio(codigo, grupo, descripcion, estado):
    """Actualiza los datos de un servicio."""
    pass


def desactivar_servicio(codigo):
    """Desactiva un servicio. No permite si aparece en cuentas corrientes."""
    pass


# --- Costos (reglas de cobro) ---

def listar_costos():
    """Retorna lista de todos los costos (programa + periodo)."""
    pass


def obtener_costo(prog_academico, cod_periodo):
    """Retorna un costo por su llave compuesta."""
    pass


def crear_o_actualizar_costo(prog_academico, cod_periodo, costo_credito, costo_global):
    """Upsert: si la combinacion existe, actualiza. Si no, inserta."""
    pass


def eliminar_costo(prog_academico, cod_periodo):
    """Elimina un costo. Solo si no hay matriculas que lo hayan usado."""
    pass
