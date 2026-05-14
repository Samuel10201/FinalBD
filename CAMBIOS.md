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

---

## Merge: branch-academica -> main

Fecha: 2026-05-13

Sin cambios necesarios sobre el codigo de la branch. Se integro directamente.

---

## Merge: isabella -> main

Fecha: 2026-05-13

### routes/reportes.py

#### `perfil()`
- Cambiado `res[0]` a `res['codigo']`. Con `RealDictCursor` los resultados son diccionarios, no tuplas.

#### Todas las rutas de reportes
- URLs corregidas de guion bajo a guion medio para consistencia con el navbar:
  - `/reportes/estudiantes_programa` -> `/reportes/estudiantes-programa`
  - `/reportes/ingreso_esperado` -> `/reportes/ingreso-esperado`
  - `/reportes/pendientes_pago` -> `/reportes/pendientes-pago`
  - `/reportes/ingreso_real` -> `/reportes/ingreso-real`

### services/matricula_service.py

#### `crear_matricula_individual()`
- Todos los accesos por indice numerico corregidos a nombres de columna:
  - `est[0]` -> `est['nombre']`
  - `prog[0]` -> `prog['duracion']`
  - `costo[0]`, `costo[1]` -> `costo['costo_global']`, `costo['costo_credito']`
  - `total_creditos_row[0]` -> `total_creditos_row['sum']`
  - `cur.fetchone()[0]` -> `cur.fetchone()['id']`

#### `obtener_estudiantes_para_masiva()`
- Todos los accesos por indice numerico corregidos:
  - `prog[0]` -> `prog['duracion']`
  - `periodo_anterior[0]` -> `periodo_anterior['cod_periodo']`
  - `row[0]..row[3]` -> `row['cod_estudiante']`, `row['nombre']`, `row['semestre']`, `row['modalidad']`

### routes/matricula.py

#### `individual()` y `masiva()`
- Corregidas las referencias de sesion: `session['tipo_id']` -> `session['usuario']['tipo_id']` y `session['id']` -> `session['usuario']['id']`.

### templates/matricula/individual.html
- Bloque cambiado de `{% block content %}` a `{% block contenido %}` y `{% block title %}` a `{% block titulo %}` para coincidir con base.html.

### templates/matricula/masiva.html
- Mismo cambio de bloques: `content` -> `contenido`, `title` -> `titulo`.

### templates/reportes/estudiantes_programa.html
- Corregida URL del formulario de guion bajo a guion medio.
- Agregado cuadro resumen con total de estudiantes matriculados y monto total esperado.

### templates/reportes/pendientes_pago.html
- Corregida URL del formulario de guion bajo a guion medio.
- Agregado cuadro resumen con cantidad de estudiantes pendientes y total adeudado.

### templates/reportes/ingreso_esperado.html
- Corregida URL del formulario de guion bajo a guion medio.

### templates/reportes/ingreso_real.html
- Corregida URL del formulario de guion bajo a guion medio.

---

## Estandarizacion de UI

Fecha: 2026-05-13

Todos los templates implementados se estandarizaron para usar exclusivamente las clases CSS del proyecto (`.card`, `.form-inline`, `.form-group`, `.form-buttons`, `.btn`, `.action-tabs`, `.table-info`, `.paginacion`, `.truncate`, `.table-container`). Se elimino Bootstrap y estilos inline innecesarios. La pagina de referencia fue `admin/usuarios.html`.

### templates/configuracion/estudiantes.html
- Eliminado bloque `<style>` de ~120 lineas con estilos inline.
- Convertido a patron de action-tabs (Buscar/Crear/Actualizar/Desactivar).
- Tab "Desactivar" ahora usa patron de dos pasos (cargar por codigo, luego confirmar) en vez de hack con JavaScript.
- Agregada paginacion con navegacion Anterior/Siguiente.
- Agregado boton "Limpiar" en tab Buscar.
- Agregado contador de resultados con `.table-info`.

### templates/configuracion/asignaturas.html
- Misma conversion que estudiantes: action-tabs, paginacion, Limpiar, dos pasos en Eliminar.
- Filtros por codigo, nombre y tipo de asignatura.

### templates/configuracion/programas.html
- Convertido de `crud_base.html` a `base.html` con action-tabs (Buscar/Crear/Actualizar).
- Agregados filtros por facultad y modo.
- Tab "Actualizar" usa patron de dos pasos (cargar por nombre, luego editar).
- Eliminados botones de accion inline en la tabla; se conservo enlace a "Ver Plan".

### templates/configuracion/plan_estudio.html
- Eliminados estilos inline de formularios, botones y tablas.
- Convertido a clases `.form-inline`, `.form-group`, `.form-buttons`.

### templates/matricula/individual.html
- Eliminadas clases de Bootstrap (`container`, `form-control`, `mb-3`, etc.).
- Convertido a clases del proyecto (`.card`, `.form-group`, `.form-inline`, `.form-buttons`).
- Resultado exitoso usa patron simple `<p><strong>Label:</strong> valor</p>`.

### templates/matricula/masiva.html
- Eliminadas clases de Bootstrap.
- Preview usa tabla plana con texto en vez de badges.
- Convertido a clases del proyecto.

### templates/reportes/*.html (5 archivos)
- Agregada navegacion con action-tabs entre los 5 reportes.
- Formularios convertidos a `.form-inline`.
- Agregado boton "Limpiar" en todos los reportes.
- Eliminados estilos inline de tablas.

### templates/estudiante/perfil.html
- Eliminados estilos inline de cards y tablas.

### routes/config_academica.py
- `listar_estudiantes()`: Agregado soporte para `tab`, `pagina`, `codigo_cargar` (actualizar) y `codigo_desactivar`.
- `listar_asignaturas()`: Agregado soporte para `tab`, `pagina`, `codigo_cargar` y `codigo_eliminar`.
- `listar_programas()`: Agregado soporte para `tab`, `nombre_cargar`, filtros de `facultad` y `modo`.
- `editar_estudiante()`, `editar_asignatura()`, `editar_programa()`: GET ahora redirige a la ruta principal con tab=actualizar en vez de renderizar el template directamente.

### services/config_academica_service.py
- `listar_estudiantes()`: Agregados parametros `limit` y `offset` para paginacion.
- `listar_asignaturas()`: Agregados parametros `limit` y `offset` para paginacion, filtros por `codigo`, `nombre` y `tipo`.
- `listar_programas()`: Agregados parametros opcionales `facultad` y `modo` para filtros.

### .gitignore
- Agregado `.vs/` (carpeta de Visual Studio que se incluyo accidentalmente en branch-academica).
- Carpeta `.vs` removida del tracking de git.
