from flask import Blueprint, render_template, request, redirect

config_operativa_bp = Blueprint('config_operativa', __name__)


# --- Periodos ---

@config_operativa_bp.route('/configuracion/periodos')
def listar_periodos():
    """Muestra lista de periodos academicos."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/periodos/crear', methods=['GET', 'POST'])
def crear_periodo():
    """GET: formulario. POST: crea periodo (valida formato YYYYXX y solapamiento de fechas)."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/editar', methods=['GET', 'POST'])
def editar_periodo(codigo):
    """GET: formulario con datos actuales. POST: actualiza el periodo."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/periodos/<codigo>/desactivar', methods=['POST'])
def desactivar_periodo(codigo):
    """Desactiva el periodo (estado = INACTIVO). No permite si tiene matriculas."""
    return render_template('en_construccion.html')


# --- Servicios (codigos de detalle) ---

@config_operativa_bp.route('/configuracion/servicios')
def listar_servicios():
    """Muestra lista de servicios (codigos de detalle)."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/servicios/crear', methods=['GET', 'POST'])
def crear_servicio():
    """GET: formulario. POST: crea servicio con grupo COBRO o PAGO."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/editar', methods=['GET', 'POST'])
def editar_servicio(codigo):
    """GET: formulario con datos actuales. POST: actualiza el servicio."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/servicios/<codigo>/desactivar', methods=['POST'])
def desactivar_servicio(codigo):
    """Desactiva el servicio (estado = INACTIVO). No permite si esta en cuentas corrientes."""
    return render_template('en_construccion.html')


# --- Costos (reglas de cobro) ---

@config_operativa_bp.route('/configuracion/costos')
def listar_costos():
    """Muestra lista de costos por programa + periodo."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/costos/crear', methods=['GET', 'POST'])
def crear_o_actualizar_costo():
    """GET: formulario con datalist de programas y periodos. POST: upsert del costo."""
    return render_template('en_construccion.html')


@config_operativa_bp.route('/configuracion/costos/<prog_academico>/<cod_periodo>/eliminar', methods=['POST'])
def eliminar_costo(prog_academico, cod_periodo):
    """Elimina el costo. Solo si no hay matriculas que lo hayan usado."""
    return render_template('en_construccion.html')
