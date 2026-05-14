# Registro de cambios post-merge

Cambios realizados sobre el codigo de cada branch al integrarse a main.
Cada seccion indica el archivo modificado y las funciones o secciones afectadas.

---

## Merge: branch-matricula -> main

Fecha: 2026-05-13

### models/db.py

#### `get_connection()`
- Se restauro `cursor_factory=RealDictCursor` en `psycopg2.connect()`. La version de branch-matricula lo omitia, causando que las consultas retornaran tuplas en vez de diccionarios. Esto rompia todos los templates que acceden a columnas por nombre (ej: `u.tipo_id`).

#### Nivel de modulo
- Se restauro la llamada a `load_dotenv()` despues del import. Sin ella, `os.getenv('DATABASE_URL')` no encontraba la variable de entorno y la conexion fallaba.

### routes/auth.py

#### `login()`
- Mensaje de bienvenida cambiado de `'Bienvenido, {nombre}'` a `'Hola, {nombre}'` para que sea neutro en genero.

### routes/matricula.py

#### `verificar_acceso_asistente()`
- Corregidas las claves de sesion. La version original usaba `session.get('vista_actual')` y `session.get('rol')`, que no existen en la app. Se cambio a `session['usuario']['rol']`.
- Se agrego retorno directo de `None` cuando el rol es `ADMINISTRADOR`, para que el admin nunca sea denegado.

### routes/config_academica.py

#### Todas las funciones (15 rutas)
- Reemplazado `pass` (retornaba `None`, causando `TypeError`) por `return render_template('en_construccion.html')`.

### routes/config_operativa.py

#### Todas las funciones (11 rutas)
- Mismo cambio que config_academica: `pass` -> `return render_template('en_construccion.html')`.

### routes/cuenta_corriente.py

#### `consulta()`
- Mismo cambio: `pass` -> `return render_template('en_construccion.html')`.

### routes/pagos.py

#### Todas las funciones (3 rutas)
- Mismo cambio: `pass` -> `return render_template('en_construccion.html')`.

### routes/reportes.py

#### Todas las funciones (5 rutas)
- Mismo cambio: `pass` -> `return render_template('en_construccion.html')`.

### templates/base.html

#### Navbar brand
- Titulo cambiado de "Cuenta Corriente" a "Sistema Academico".

#### Admin bar
- Eliminado el enlace `<a href="/admin/usuarios">Usuarios</a>` que estaba junto a "Ver como:".

#### Navbar menu
- "Usuarios" agregado como opcion del menu visible solo en vista de Administrador.
- El menu sigue filtrandose segun la vista seleccionada (variable `rol`).

#### Alertas
- El bloque de alertas flash se envolvio en `{% block alertas %}` para permitir que templates hijos lo sobreescriban.

### templates/auth/login.html

#### Alertas de error
- Las alertas flash se movieron dentro de `.login-container`, debajo del card de login, para que tengan el mismo ancho que el formulario.
- Se sobreescribe `{% block alertas %}` vacio para evitar duplicacion de alertas.

### templates/admin/usuarios.html

#### Boton "Limpiar"
- Clase cambiada de `btn-secondary` (gris, parecia deshabilitado) a `btn-danger` (rojo).

### templates/en_construccion.html (NUEVO)
- Template placeholder para rutas no implementadas. Muestra mensaje "Pagina en construccion".

### credenciales_prueba.txt
- Agregada columna de correo electronico a todas las entradas.
- Formato actualizado: `nombre | correo | tipo_id | id | rol | contrasena`.
