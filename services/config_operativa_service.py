from models.db import get_connection, close_connection


# --- Periodos ---

def listar_periodos(codigo=None, estado=None):
    """Retorna lista de periodos academicos con filtros opcionales."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM periodo WHERE 1=1 "
            params = []
            if codigo:
                query += "AND codigo ILIKE %s "
                params.append(f"{codigo}%")
            if estado:
                query += "AND estado = %s "
                params.append(estado)
            query += "ORDER BY codigo DESC"
            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def obtener_periodo(codigo):
    """Retorna un periodo por su codigo."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM periodo
                WHERE codigo = %s
                """,
                (codigo,)
            )

            return cur.fetchone()

    finally:
        close_connection(conn)


def crear_periodo(codigo, descripcion, fecha_inicio, fecha_fin):
    """Crea un periodo."""

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO periodo (
                        codigo,
                        descripcion,
                        fecha_inicio,
                        fecha_fin,
                        estado
                    )
                    VALUES (%s, %s, %s, %s, 'ACTIVO')
                    """,
                    (
                        codigo,
                        descripcion,
                        fecha_inicio,
                        fecha_fin
                    )
                )

    finally:
        close_connection(conn)


def actualizar_periodo(codigo, descripcion, fecha_inicio, fecha_fin, estado):
    """Actualiza un periodo."""

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE periodo
                    SET descripcion = %s,
                        fecha_inicio = %s,
                        fecha_fin = %s,
                        estado = %s
                    WHERE codigo = %s
                    """,
                    (
                        descripcion,
                        fecha_inicio,
                        fecha_fin,
                        estado,
                        codigo
                    )
                )

    finally:
        close_connection(conn)


def desactivar_periodo(codigo):
    """Desactiva un periodo."""

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    UPDATE periodo
                    SET estado = 'INACTIVO'
                    WHERE codigo = %s
                    """,
                    (codigo,)
                )

    finally:
        close_connection(conn)


def validar_codigo_periodo(codigo):
    """Valida que el codigo tenga 6 digitos y termine en 00, 10, 20, 30 o 40."""
    pass


def validar_fechas_periodo(fecha_inicio, fecha_fin):
    """Valida que las fechas no se solapen con periodos existentes."""
    pass

# --- Servicios (codigos de detalle) ---

def listar_servicios(codigo=None, grupo=None, estado=None):
    """Retorna lista de servicios con filtros opcionales."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM servicio WHERE 1=1 "
            params = []
            if codigo:
                query += "AND codigo ILIKE %s "
                params.append(f"{codigo}%")
            if grupo:
                query += "AND grupo = %s "
                params.append(grupo)
            if estado:
                query += "AND estado = %s "
                params.append(estado)
            query += "ORDER BY codigo"
            cur.execute(query, tuple(params))
            return cur.fetchall()
    finally:
        close_connection(conn)


def obtener_servicio(codigo):
    """Retorna un servicio por su codigo."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM servicio WHERE codigo = %s",
                (codigo,)
            )
            return cur.fetchone()
    finally:
        close_connection(conn)


def crear_servicio(codigo, grupo, descripcion):
    """Crea un servicio."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO servicio (
                        codigo,
                        grupo,
                        estado,
                        descripcion
                    )
                    VALUES (%s, %s, 'ACTIVO', %s)
                    """,
                    (codigo, grupo, descripcion)
                )
    finally:
        close_connection(conn)


def actualizar_servicio(codigo, grupo, descripcion, estado):
    """Actualiza un servicio."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE servicio
                    SET grupo = %s,
                        descripcion = %s,
                        estado = %s
                    WHERE codigo = %s
                    """,
                    (grupo, descripcion, estado, codigo)
                )
    finally:
        close_connection(conn)


def desactivar_servicio(codigo):
    """Desactiva un servicio."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE servicio
                    SET estado = 'INACTIVO'
                    WHERE codigo = %s
                    """,
                    (codigo,)
                )
    finally:
        close_connection(conn)
        

# --- Costos (reglas de cobro) ---

def listar_costos():
    """Retorna lista de todos los costos."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM costo
                ORDER BY cod_periodo DESC
                """
            )

            return cur.fetchall()

    finally:
        close_connection(conn)


def obtener_costo(prog_academico, cod_periodo):
    """Retorna un costo."""

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM costo
                WHERE prog_academico = %s
                AND cod_periodo = %s
                """,
                (prog_academico, cod_periodo)
            )

            return cur.fetchone()

    finally:
        close_connection(conn)


def crear_o_actualizar_costo(
    prog_academico,
    cod_periodo,
    costo_credito,
    costo_global
):
    """Inserta o actualiza un costo."""

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO costo (
                        prog_academico,
                        cod_periodo,
                        costo_credito,
                        costo_global
                    )
                    VALUES (%s, %s, %s, %s)

                    ON CONFLICT (
                        prog_academico,
                        cod_periodo
                    )

                    DO UPDATE SET
                        costo_credito = EXCLUDED.costo_credito,
                        costo_global = EXCLUDED.costo_global
                    """,
                    (
                        prog_academico,
                        cod_periodo,
                        costo_credito,
                        costo_global
                    )
                )

    finally:
        close_connection(conn)


def eliminar_costo(prog_academico, cod_periodo):
    """Elimina un costo."""

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    DELETE FROM costo
                    WHERE prog_academico = %s
                    AND cod_periodo = %s
                    """,
                    (
                        prog_academico,
                        cod_periodo
                    )
                )

    finally:
        close_connection(conn)