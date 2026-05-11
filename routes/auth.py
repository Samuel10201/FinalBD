from flask import Blueprint, render_template, request, redirect, session, flash
from services.auth_service import (
    login as auth_login,
    obtener_usuario,
    obtener_usuario_por_correo,
    listar_usuarios as service_listar,
    crear_usuario as service_crear,
    actualizar_usuario as service_actualizar,
    desactivar_usuario as service_desactivar
)
from routes import login_required, rol_requerido

auth_bp = Blueprint('auth', __name__)

DESTINOS_POR_ROL = {
    'ADMINISTRADOR': '/admin/usuarios',
    'SUPERVISOR': '/configuracion/estudiantes',
    'ASISTENTE': '/matricula/individual',
    'ESTUDIANTE': '/estudiante/perfil',
}


# --- Ruta raiz ---

@auth_bp.route('/')
def index():
    if 'usuario' not in session:
        return redirect('/login')
    destino = DESTINOS_POR_ROL.get(session['usuario']['rol'], '/login')
    return redirect(destino)


# --- Login / Logout ---

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect('/')

    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        contrasena = request.form.get('contrasena', '')

        usuario = auth_login(correo, contrasena)
        if usuario:
            session['usuario'] = dict(usuario)
            flash(f'Bienvenido, {usuario["nombre"]}', 'success')
            return redirect(DESTINOS_POR_ROL.get(usuario['rol'], '/'))

        flash('Correo o contrasena incorrectos', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesion cerrada', 'success')
    return redirect('/login')


# --- Cambiar vista de admin ---

@auth_bp.route('/admin/cambiar-vista', methods=['POST'])
@login_required
def cambiar_vista():
    if session['usuario']['rol'] != 'ADMINISTRADOR':
        flash('No tiene permisos', 'error')
        return redirect('/')
    vista = request.form.get('vista_rol')
    session['vista_rol'] = vista
    return redirect(DESTINOS_POR_ROL.get(vista, '/admin/usuarios'))


# --- Gestion de usuarios (ADMIN) ---

@auth_bp.route('/admin/usuarios')
@rol_requerido('ADMINISTRADOR')
def listar_usuarios():
    buscar = request.args.get('buscar', '').strip()
    accion = request.args.get('accion', 'buscar')
    pagina = max(1, int(request.args.get('pagina', 1)))
    tipo_id_sel = request.args.get('tipo_id', '').strip()
    id_sel = request.args.get('id', '').strip()

    limite = 20
    offset = (pagina - 1) * limite
    usuarios = service_listar(buscar=buscar, limite=limite, offset=offset)

    seleccionado = None
    correo_sel = request.args.get('correo', '').strip()
    if accion in ('actualizar', 'desactivar'):
        if correo_sel:
            seleccionado = obtener_usuario_por_correo(correo_sel)
        elif tipo_id_sel and id_sel:
            seleccionado = obtener_usuario(tipo_id_sel, id_sel)
        if (correo_sel or (tipo_id_sel and id_sel)) and not seleccionado:
            flash('Usuario no encontrado', 'error')

    return render_template('admin/usuarios.html',
        usuarios=usuarios, buscar=buscar, accion=accion,
        pagina=pagina, seleccionado=seleccionado)


@auth_bp.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@rol_requerido('ADMINISTRADOR')
def crear_usuario():
    if request.method == 'GET':
        return redirect('/admin/usuarios')

    tipo_id = request.form.get('tipo_id', '').strip()
    id_usuario = request.form.get('id', '').strip()
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    contrasena = request.form.get('contrasena', '')
    rol = request.form.get('rol', '').strip()

    try:
        service_crear(tipo_id, id_usuario, nombre, correo, contrasena, rol)
        flash('Usuario creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al crear usuario: {e}', 'error')

    return redirect('/admin/usuarios')


@auth_bp.route('/admin/usuarios/<tipo_id>/<id>/editar', methods=['GET', 'POST'])
@rol_requerido('ADMINISTRADOR')
def editar_usuario(tipo_id, id):
    if request.method == 'POST':
        nuevo_tipo_id = request.form.get('tipo_id', '').strip()
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip()
        rol = request.form.get('rol', '').strip()
        estado = request.form.get('estado', '').strip()
        contrasena = request.form.get('contrasena', '').strip() or None

        try:
            service_actualizar(tipo_id, id, nombre, correo, rol, estado, contrasena, nuevo_tipo_id)
            flash('Usuario actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar usuario: {e}', 'error')

        return redirect('/admin/usuarios')

    return redirect(f'/admin/usuarios?accion=actualizar&tipo_id={tipo_id}&id={id}')


@auth_bp.route('/admin/usuarios/<tipo_id>/<id>/desactivar', methods=['POST'])
@rol_requerido('ADMINISTRADOR')
def desactivar_usuario(tipo_id, id):
    usuario_actual = session['usuario']
    if usuario_actual['tipo_id'].strip() == tipo_id and usuario_actual['id'].strip() == id:
        flash('No puede desactivar su propio usuario', 'error')
        return redirect('/admin/usuarios')

    try:
        service_desactivar(tipo_id, id)
        flash('Usuario desactivado', 'success')
    except Exception as e:
        flash(f'Error al desactivar usuario: {e}', 'error')

    return redirect('/admin/usuarios')
