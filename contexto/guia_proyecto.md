# Guia del Proyecto — Sistema de Cuenta Corriente del Estudiante

## 1. Descripcion del proyecto

Sistema web que gestiona los cobros y pagos de matriculas estudiantiles para una universidad.
Proyecto final de la materia Bases de Datos.

### Flujo de negocio
1. Un SUPERVISOR configura el sistema: programas academicos, planes de estudio, periodos, servicios, reglas de cobro y estudiantes.
2. Un ASISTENTE ingresa la informacion del estudiante (semestre, modalidad de cobro) y genera cobros individuales o masivos. Estos generan movimientos de COBRO en la cuenta corriente.
3. El estudiante o asistente registra pagos (por caja o en linea), lo cual genera movimientos de PAGO en la cuenta corriente.
4. Balance: los codigos de detalle asociados a COBRO se restan y los asociados a PAGO se suman. Cuando el balance da cero, el estudiante esta al dia.

### Roles del sistema
- ADMINISTRADOR: acceso a todas las funcionalidades. Tiene una barra superior con un selector para ver el sistema como cualquier otro rol, mas acceso directo a gestion de usuarios.
- SUPERVISOR: configuracion del sistema (programas, periodos, reglas de cobro, servicios, estudiantes).
- ASISTENTE: ingreso de datos del estudiante, semestre y modalidad de cobro. Generacion de cobro individual y masivo. Registro de pagos.
- ESTUDIANTE: consulta su cuenta corriente, pago en linea.

---

## 2. Modelo de datos

### Entidades (9)
| Entidad | PK | Campos principales |
|---------|----|--------------------|
| Periodo | codigo CHAR(6) | descripcion VARCHAR(100), fecha_inicio DATE, fecha_fin DATE, estado VARCHAR(15) |
| Programa Academico | nombre VARCHAR(30) | facultad VARCHAR(40), modo VARCHAR(10), duracion INT |
| Asignatura | codigo CHAR(6) | nombre VARCHAR(30), creditos INT, descripcion VARCHAR(100), tipo VARCHAR(10) |
| Servicio | codigo VARCHAR(4) | grupo VARCHAR(5), estado VARCHAR(10), descripcion VARCHAR(100) |
| Usuario | tipo_id CHAR(2) + id VARCHAR(15) (compuesta) | nombre VARCHAR(50), correo VARCHAR(50) UNIQUE, contrasena VARCHAR(250), rol VARCHAR(15), estado VARCHAR(10), fecha_creacion TIMESTAMP |
| Estudiante | codigo VARCHAR(8) | nombre VARCHAR(50), estado VARCHAR(10), fecha_nacimiento DATE, direccion VARCHAR(60), tipo_id CHAR(2) + id VARCHAR(15) (FK a Usuario) |
| Matricula | id SERIAL | modalidad VARCHAR(10), semestre INT, fecha_creacion TIMESTAMP, cod_estudiante VARCHAR(8) FK, cod_periodo CHAR(6) FK, prog_acad VARCHAR(30) FK |
| Cuenta Corriente | id SERIAL | fecha TIMESTAMP, descripcion_mov VARCHAR(100), valor NUMERIC(12,2), cod_estudiante VARCHAR(8) FK, tipo_id_usuario CHAR(2) + id_usuario VARCHAR(15) FK, codigo_servicio VARCHAR(4) FK, codigo_periodo CHAR(6) FK, id_pago INT FK nullable |
| Pago | id SERIAL | estado VARCHAR(10), fecha TIMESTAMP, metodo VARCHAR(10), monto NUMERIC(12,2) |

### Tablas intermedias (2)
| Tabla | PK | Campos |
|-------|-----|--------|
| Costo | prog_academico VARCHAR(30) + cod_periodo CHAR(6) (compuesta, ambas FK) | costo_credito NUMERIC(12,2), costo_global NUMERIC(12,2) |
| Plan Estudio | nombre_programa VARCHAR(30) + cod_asignatura CHAR(6) (compuesta, ambas FK) | semestre INT |

### Decisiones de diseno
- La modalidad es UNA por matricula (global O creditos, no ambas).
- El saldo es calculado (suma de movimientos), no almacenado en un campo.
- Todo estudiante tiene un usuario con rol ESTUDIANTE.
- La FK de Estudiante a Usuario es por tipo_id + id (documento de identidad).
- Cuenta Corriente es una entidad propia, no una relacion.
- Pago es una entidad separada de Cuenta Corriente (datos operativos vs contables).
- Al crear un estudiante, se crea automaticamente su cuenta corriente (permite cobros previos a matricula como examenes de admision).

### Restricciones y formatos implementados en la BD

#### Formatos de codigo (validados con CHECK regex)
- **Periodo:** `YYYYXX` donde XX es 00, 10, 20, 30 o 40. Regex: `'^[0-9]{4}(00|10|20|30|40)$'`
- **Asignatura:** 3 letras mayusculas + 3 digitos (ej: MAT101, PRG201). Regex: `'^[A-Z]{3}[0-9]{3}$'`
- **Servicio:** 3 o 4 letras mayusculas (ej: PMAT, ANT). Regex: `'^[A-Z]{3,4}$'`
- **Estudiante:** entre 2 y 8 digitos. Regex: `'^[0-9]{2,8}$'`
- **Correo:** formato email estandar.

#### Valores permitidos (CHECK IN)
- **tipo_id (usuario):** CC, TI, CE, PP, RC, NI, PE
- **rol (usuario):** ADMINISTRADOR, ESTUDIANTE, SUPERVISOR, ASISTENTE
- **estado (usuario, estudiante, servicio, periodo):** ACTIVO, INACTIVO
- **estado (pago):** PENDIENTE, COMPLETADO, ANULADO
- **grupo (servicio):** COBRO, PAGO
- **modalidad (matricula):** GLOBAL, CREDITO
- **modo (programa):** PRESENCIAL, REMOTO
- **tipo (asignatura):** OBLIGATORIA, ELECTIVA
- **metodo (pago):** EN LINEA, CAJA

#### Campos autogenerados (no enviar en INSERT)
- **matricula.id:** SERIAL. Usar `RETURNING id` para obtener el valor.
- **pago.id:** SERIAL. Usar `RETURNING id` para obtener el valor.
- **cuenta_corriente.id:** SERIAL.
- **fecha_creacion (usuario, matricula):** DEFAULT NOW().
- **fecha (pago, cuenta_corriente):** DEFAULT NOW().
- **estado (estudiante):** DEFAULT 'ACTIVO'.

#### Rangos numericos
- **duracion (programa):** entre 1 y 12 semestres.
- **creditos (asignatura):** entre 0 y 10.
- **semestre (matricula, plan_estudio):** entre 1 y 12.
- **valor (cuenta_corriente):** mayor a 0.
- **monto (pago):** mayor a 0.
- **costo_credito, costo_global (costo):** mayor a 0.

#### Constraint UNIQUE
- **correo (usuario):** no se repite.
- **matricula:** combinacion (cod_estudiante, cod_periodo, prog_acad) unica.

### Reglas de negocio (creacion y eliminacion)

#### Transacciones atomicas (BEGIN/COMMIT)
Operaciones que deben ejecutarse como un bloque (todas o ninguna):
- **Crear estudiante:** INSERT usuario (rol ESTUDIANTE) + INSERT estudiante + INSERT cuenta corriente.
- **Registrar pago:** INSERT pago + INSERT movimiento en cuenta corriente.

#### Creacion con dependencias
Cuando el usuario referencia una entidad que no existe, el sistema ofrece crearla en ese momento:
- **Asignatura:** requiere programa academico + plan de estudio.
- **Matricula:** requiere estudiante, programa, periodo, y costo definido (programa+periodo).
- **Costo:** requiere programa y periodo. Si la combinacion ya existe, se actualiza (upsert).

#### Interfaz: campos con referencia a otras entidades
Usar `<datalist>` de HTML para campos que referencian otra entidad. Permite autocompletado con opciones existentes y libertad de escribir un valor nuevo.

#### Dos tipos de cobro
- **Cobro por matricula:** se genera al crear la matricula. Usa la tabla Costo (programa+periodo) para calcular el monto segun modalidad (global o creditos).
- **Cobro por servicio:** se genera directamente asociando un servicio de grupo COBRO a la cuenta corriente del estudiante. Ejemplos: examen medico, carnet, derechos de grado.

#### Eliminacion y proteccion de datos
| Entidad | Eliminar | Regla |
|---------|----------|-------|
| Estudiante | No. Desactivar (INACTIVO) | Si tiene movimientos en cuenta corriente |
| Usuario | No. Desactivar (INACTIVO) | Si es FK de un estudiante, se desactivan ambos |
| Programa | No. Desactivar | Si tiene matriculas o asignaturas en plan de estudio |
| Periodo | No. Desactivar | Si tiene matriculas asociadas |
| Servicio | No. Desactivar | Si aparece en alguna cuenta corriente |
| Asignatura | Si (DELETE) | Se elimina tambien de planes de estudio. Costo global no cambia |
| Pago | No. Anular (estado = ANULADO) | Nunca se borran. Pago anulado no cuenta en saldo |
| Movimiento cuenta corriente | No | Nunca se eliminan movimientos |
| Costo | Si (DELETE) | Solo si no hay matriculas que lo hayan usado |

#### Validaciones
- **Periodo:** codigo de 6 digitos (YYYYXX). XX solo puede ser: 00 (libre), 10 (1er semestre), 20 (vacacional 1), 30 (2do semestre), 40 (vacacional 2).
- **Fechas de periodo:** no se pueden solapar (fecha_inicio posterior a fecha_fin del periodo anterior).
- **Matricula:** unica por estudiante + programa + periodo (UNIQUE constraint).
- **Cobro por matricula:** no se genera si no existe un costo definido para programa + periodo.

#### Estados de Pago
- `PENDIENTE`: pago registrado, pendiente de confirmacion.
- `COMPLETADO`: pago confirmado y aplicado.
- `ANULADO`: pago rechazado o anulado. No cuenta en el calculo del saldo.

---

## 3. Stack tecnologico

| Componente | Tecnologia | Proposito |
|------------|-----------|-----------|
| Backend | Python + Flask | Framework web, maneja rutas y logica |
| Frontend | HTML + CSS + Jinja2 | Templates renderizados por Flask, sin JavaScript |
| Base de datos | PostgreSQL en Supabase (plan gratuito) | Almacenamiento de datos |
| Conexion BD | psycopg2 (SQL directo) | No se usa ORM. Las consultas son SQL puro |
| Hosting | Vercel (plan gratuito, serverless) | Despliega la app como funciones serverless |

---

## 4. Arquitectura del proyecto

### Estructura de archivos

```
proyecto/
├── api/
│   └── index.py                  ← Punto de entrada (Vercel). Crea la app Flask y registra blueprints.
├── routes/                       ← Rutas (URLs) agrupadas por modulo (blueprints de Flask).
│   ├── __init__.py
│   ├── auth.py
│   ├── config_academica.py
│   ├── config_operativa.py
│   ├── matricula.py
│   ├── cuenta_corriente.py
│   ├── pagos.py
│   └── reportes.py
├── services/                     ← Logica de negocio y consultas SQL.
│   ├── __init__.py
│   ├── auth_service.py
│   ├── config_academica_service.py
│   ├── config_operativa_service.py
│   ├── matricula_service.py
│   ├── cuenta_service.py
│   ├── pago_service.py
│   └── reporte_service.py
├── models/                       ← Conexion a la base de datos.
│   ├── __init__.py
│   └── db.py
├── templates/                    ← Archivos HTML con Jinja2.
│   ├── base.html
│   ├── auth/
│   │   └── login.html
│   ├── admin/
│   │   └── usuarios.html
│   ├── configuracion/
│   │   ├── estudiantes.html
│   │   ├── programas.html
│   │   ├── asignaturas.html
│   │   ├── plan_estudio.html
│   │   ├── periodos.html
│   │   ├── servicios.html
│   │   └── costos.html
│   ├── matricula/
│   │   ├── individual.html
│   │   └── masiva.html
│   ├── pagos/
│   │   ├── registro.html
│   │   └── en_linea.html
│   ├── cuenta_corriente/
│   │   └── consulta.html
│   ├── estudiante/
│   │   ├── perfil.html
│   │   └── cuenta.html
│   └── reportes/
│       ├── estudiantes_programa.html
│       ├── ingreso_esperado.html
│       ├── pendientes_pago.html
│       ├── ingreso_real.html
│       └── cartera.html
├── static/
│   ├── css/
│   └── img/
├── sql/
│   ├── schema.sql                ← CREATE TABLE, CREATE INDEX, CREATE VIEW.
│   └── seed.sql                  ← Datos de prueba.
├── .env.example
├── .gitignore
├── requirements.txt
└── vercel.json
```

### Como funciona la arquitectura

Cada modulo tiene 3 capas:

1. **Ruta (routes/)**: recibe la peticion HTTP del navegador, llama al servicio, y renderiza el HTML con el resultado. No tiene logica de negocio ni SQL.
2. **Servicio (services/)**: contiene la logica de negocio y ejecuta las consultas SQL con psycopg2. Devuelve datos a la ruta.
3. **Template (templates/)**: archivo HTML con Jinja2 que muestra los datos al usuario.

Ejemplo de flujo: el asistente crea una matricula.
- El navegador envia el formulario a la URL `/matricula/nueva`.
- `routes/matricula.py` recibe la peticion y llama a `services/matricula_service.py`.
- `matricula_service.py` ejecuta los INSERTs en la BD y devuelve el resultado.
- `routes/matricula.py` renderiza `templates/matricula/individual.html` con el resultado.

### Blueprints

Flask usa blueprints para agrupar rutas por modulo. Cada archivo en routes/ crea un Blueprint:

```python
from flask import Blueprint
matricula_bp = Blueprint('matricula', __name__)

@matricula_bp.route('/matricula/nueva')
def nueva():
    ...
```

Luego `api/index.py` los registra:

```python
from flask import Flask
from routes.matricula import matricula_bp
app = Flask(__name__)
app.register_blueprint(matricula_bp)
```

### Templates HTML: como usarlos

Hay dos templates base. Cada pagina del proyecto debe heredar de uno de ellos.

#### Opcion 1: `base.html` (paginas libres)

Para paginas que NO son CRUD (matricula, pagos, cuenta corriente, reportes, perfil estudiante, login). Hereda la navbar y el layout general, y te da un bloque vacio para poner lo que quieras.

```html
{% extends "base.html" %}
{% block titulo %}Nombre de la pagina{% endblock %}
{% block contenido %}
    <!-- Tu contenido aqui -->
{% endblock %}
```

#### Opcion 2: `crud_base.html` (paginas de configuracion)

Para paginas de CRUD (estudiantes, programas, asignaturas, periodos, servicios, costos, usuarios). Ya trae la estructura de formulario arriba + tabla abajo. Solo hay que llenar los bloques.

```html
{% extends "crud_base.html" %}

{% block titulo_formulario %}Crear Programa{% endblock %}
{% block form_action %}/configuracion/programas{% endblock %}

{% block campos %}
<div class="form-group">
    <label for="nombre">Nombre</label>
    <input type="text" id="nombre" name="nombre">
</div>
<div class="form-group">
    <label for="facultad">Facultad</label>
    <input type="text" id="facultad" name="facultad">
</div>
{% endblock %}

{% block columnas %}
<th>Nombre</th><th>Facultad</th><th>Acciones</th>
{% endblock %}

{% block filas %}
{% for p in programas %}
<tr>
    <td>{{ p.nombre }}</td>
    <td>{{ p.facultad }}</td>
    <td><a href="#">Editar</a> | <a href="#">Desactivar</a></td>
</tr>
{% endfor %}
{% endblock %}
```

Bloques disponibles en `crud_base.html`:
- `titulo_formulario`: titulo del card del formulario.
- `form_action`: URL a la que se envia el formulario (POST).
- `campos`: los inputs del formulario, cada uno dentro de un `<div class="form-group">`.
- `botones`: (opcional) botones del formulario. Por defecto trae un boton "Guardar".
- `titulo_tabla`: titulo del card de la tabla. Por defecto dice "Registros".
- `columnas`: los `<th>` de la tabla.
- `filas`: las filas `<tr>` de la tabla, normalmente dentro de un `{% for ... %}`.

#### Clases CSS disponibles

| Clase | Uso |
|-------|-----|
| `card` | Contenedor con fondo blanco, bordes redondeados y sombra. Para envolver secciones. |
| `form-group` | Contenedor de un campo de formulario (label + input). |
| `btn btn-primary` | Boton azul (accion principal). |
| `btn btn-danger` | Boton rojo (eliminar, desactivar). |
| `btn btn-success` | Boton verde (confirmar). |
| `alert alert-success` | Mensaje de exito (verde). |
| `alert alert-error` | Mensaje de error (rojo). |
| `alert alert-warning` | Mensaje de advertencia (amarillo). |
| `login-container` | Contenedor centrado para la pagina de login. |

#### Mensajes flash

Para mostrar mensajes de exito o error despues de una operacion, usar `flash()` de Flask en la ruta:

```python
from flask import flash, redirect

flash('Programa creado exitosamente', 'success')   # verde
flash('Error: el programa ya existe', 'error')     # rojo
flash('El periodo esta proximo a vencer', 'warning')  # amarillo
return redirect('/configuracion/programas')
```

Los mensajes se muestran automaticamente en `base.html` (no hay que agregar nada en el template).

---

## 5. Pantallas del sistema (22)

### Auth
| # | Pantalla | Descripcion |
|---|----------|-------------|
| 1 | Login | Correo + contrasena. Redirige al dashboard del rol. |

### Administrador
| # | Pantalla | Descripcion |
|---|----------|-------------|
| 2 | Barra de admin | Barra superior permanente. Dropdown para cambiar vista (SUPERVISOR/ASISTENTE/ESTUDIANTE) + acceso a gestion de usuarios. |
| 3 | Gestion de usuarios | CRUD: tipo_id, id, nombre, correo, contrasena, rol, estado. |

### Supervisor — Configuracion
| # | Pantalla | Descripcion |
|---|----------|-------------|
| 4 | Estudiantes | CRUD completo. Al crear un estudiante se crea su cuenta corriente automaticamente. |
| 5 | Programas academicos | CRUD: nombre, facultad, modo, duracion. Muestra plan de estudio completo. |
| 6 | Asignaturas | CRUD: codigo, nombre, creditos, descripcion, tipo. |
| 7 | Plan de estudio | Asignar asignaturas a un programa con semestre. Vista: programa > semestre > asignaturas con creditos. |
| 8 | Periodos | CRUD: codigo, descripcion, fecha inicio, fecha fin, estado. |
| 9 | Servicios (codigos de detalle) | CRUD: codigo, grupo (COBRO/PAGO), estado, descripcion. |
| 10 | Costos (reglas de cobro) | Seleccionar programa + periodo, definir costo por credito y costo global. |

### Asistente — Gestion de cobro y pagos
| # | Pantalla | Descripcion |
|---|----------|-------------|
| 11 | Matricula individual | Formulario: estudiante, programa, periodo, modalidad (global/creditos), semestre. Genera COBROs. |
| 12 | Matricula masiva | Seleccionar programa. Genera matriculas para el periodo siguiente con semestre+1 para todos los estudiantes activos. Conserva modalidad anterior. Excluye ultimo semestre. |
| 13 | Registro de pago (caja) | Formulario: estudiante, monto, metodo, referencia. Genera PAGOs. |
| 14 | Consulta cuenta corriente | Buscar estudiante, ver cobros/pagos con codigo de detalle y descripcion, saldo por periodo. |

### Estudiante
| # | Pantalla | Descripcion |
|---|----------|-------------|
| 15 | Mi perfil y plan de estudio | Una sola pantalla: datos personales + matricula actual (programa, semestre, modalidad, periodo) + asignaturas por semestre con creditos. |
| 16 | Mi cuenta corriente | Cobros y pagos con codigo de detalle y descripcion. Balance por periodo. |
| 17 | Pago en linea | Simulacion de pago. Genera movimiento de PAGO. |

### Reportes (acceso: SUPERVISOR y ADMIN)
| # | Reporte | Filtros | Descripcion |
|---|---------|---------|-------------|
| 18 | Estudiantes por programa | Periodo, programa | Listado con estudiante, programa, modalidad, monto. |
| 19 | Ingreso esperado | Periodo, programa | Total que se deberia recaudar, totalizado. |
| 20 | Estudiantes pendientes de pago | Periodo, programa | Estudiantes con saldo pendiente. |
| 21 | Ingreso real | Periodo, programa | Total de pagos recibidos. |
| 22 | Cartera | Periodo, programa | Estudiantes que deben, valor individual, total cuentas por cobrar. |

---

## 6. Asignacion de trabajo

### Fases de desarrollo (por dependencias)

```
Fase 1: BD + Infraestructura + Auth (Samuel)
        ↓
Fase 2: Configuracion academica + operativa (Persona 3 y 4)
        ↓
Fase 3: Matricula + Pagos + Cuenta corriente (Persona 5 y 6)
        ↓
Fase 4: Estudiante perfil + Reportes (Persona 7)
```

### Asignacion por persona

#### Samuel — BD + Infraestructura + Auth + Admin
**Archivos:** `sql/schema.sql`, `sql/seed.sql`, `models/db.py`, `api/index.py`, `vercel.json`, `templates/base.html`, `static/css/`, `routes/auth.py`, `services/auth_service.py`, `templates/auth/login.html`, `templates/admin/usuarios.html`
**Pantallas:** 1 (Login), 2 (Barra admin), 3 (Usuarios)
**Responsabilidades:**
- Crear todas las tablas, indices y views en PostgreSQL.
- Configurar la conexion a Supabase.
- Implementar login, sesion, control de acceso por rol.
- Crear el template base (navbar, layout).
- CRUD de usuarios.
- Selector de vista del administrador.

#### Persona 3 — Configuracion academica
**Archivos:** `routes/config_academica.py`, `services/config_academica_service.py`, `templates/configuracion/estudiantes.html`, `templates/configuracion/programas.html`, `templates/configuracion/asignaturas.html`, `templates/configuracion/plan_estudio.html`
**Pantallas:** 4 (Estudiantes), 5 (Programas), 6 (Asignaturas), 7 (Plan de estudio)
**Responsabilidades:**
- CRUD de estudiantes (al crear uno, se crea su cuenta corriente).
- CRUD de programas academicos.
- CRUD de asignaturas.
- Gestion del plan de estudio (asignar asignaturas a programas con semestre).

#### Persona 4 — Configuracion operativa
**Archivos:** `routes/config_operativa.py`, `services/config_operativa_service.py`, `templates/configuracion/periodos.html`, `templates/configuracion/servicios.html`, `templates/configuracion/costos.html`
**Pantallas:** 8 (Periodos), 9 (Servicios), 10 (Costos)
**Responsabilidades:**
- CRUD de periodos academicos.
- CRUD de servicios (codigos de detalle con grupo COBRO/PAGO).
- Gestion de costos (reglas de cobro por programa y periodo).

#### Persona 5 — Matricula
**Archivos:** `routes/matricula.py`, `services/matricula_service.py`, `templates/matricula/individual.html`, `templates/matricula/masiva.html`
**Pantallas:** 11 (Matricula individual), 12 (Matricula masiva)
**Responsabilidades:**
- Formulario de matricula individual: seleccionar estudiante, programa, periodo, modalidad, semestre. Genera cobros.
- Matricula masiva: seleccionar programa, generar matriculas para periodo siguiente con semestre+1, conservar modalidad anterior, excluir estudiantes en ultimo semestre.

#### Persona 6 — Pagos + Cuenta corriente
**Archivos:** `routes/pagos.py`, `routes/cuenta_corriente.py`, `services/pago_service.py`, `services/cuenta_service.py`, `templates/pagos/registro.html`, `templates/pagos/en_linea.html`, `templates/cuenta_corriente/consulta.html`, `templates/estudiante/cuenta.html`
**Pantallas:** 13 (Registro pago caja), 14 (Consulta cuenta corriente), 16 (Mi cuenta corriente), 17 (Pago en linea)
**Responsabilidades:**
- Registro de pagos por caja (asistente).
- Simulacion de pago en linea (estudiante).
- Consulta de cuenta corriente de un estudiante (asistente).
- Vista de cuenta corriente propia (estudiante).
- Balance: codigos COBRO se restan, codigos PAGO se suman, resultado cero = al dia.

#### Persona 7 — Estudiante perfil + Reportes
**Archivos:** `routes/reportes.py`, `services/reporte_service.py`, `templates/estudiante/perfil.html`, `templates/reportes/estudiantes_programa.html`, `templates/reportes/ingreso_esperado.html`, `templates/reportes/pendientes_pago.html`, `templates/reportes/ingreso_real.html`, `templates/reportes/cartera.html`
**Pantallas:** 15 (Mi perfil y plan de estudio), 18-22 (Reportes)
**Responsabilidades:**
- Pantalla de perfil del estudiante (datos personales + matricula actual + plan de estudio con asignaturas y creditos por semestre).
- 5 reportes con filtros por periodo y programa.

---

## 7. Reglas para trabajar con IA

Cuando uses una IA para generar codigo de este proyecto, incluye este contexto:

- **No usar ORM.** Las consultas se hacen con SQL directo usando psycopg2.
- **No usar JavaScript.** El frontend es HTML + CSS + Jinja2 unicamente.
- **Cada modulo tiene 3 capas:** ruta (routes/), servicio (services/), template (templates/). La ruta no tiene SQL. El servicio no renderiza HTML.
- **Blueprints de Flask.** Cada archivo en routes/ es un blueprint independiente. No poner rutas en index.py.
- **La BD es PostgreSQL** alojada en Supabase. La conexion se hace desde models/db.py.
- **El saldo es calculado**, no hay un campo "saldo" en ninguna tabla. Se calcula sumando movimientos PAGO y restando movimientos COBRO de la cuenta corriente.
- **Respetar el modelo de datos** descrito en la seccion 2. No agregar tablas ni columnas que no esten en el modelo.
- **Respetar la estructura de archivos.** Solo trabajar en los archivos asignados a tu rol.
- **ID de matricula es autogenerado (SERIAL).** Solo el ASISTENTE o ADMINISTRADOR puede crear una matricula. El estudiante puede ver el ID de su matricula pero no crearlo ni modificarlo. Al insertar una matricula, usar `RETURNING id` para obtener el ID generado y mostrarlo al usuario.
- **Transacciones con psycopg2.** Para operaciones atomicas (crear estudiante, registrar pago), usar el context manager:
  ```python
  conn = get_connection()
  with conn:
      with conn.cursor() as cur:
          cur.execute("INSERT INTO ...", (...))
          cur.execute("INSERT INTO ...", (...))
  # COMMIT automatico si no hay error, ROLLBACK si hay excepcion
  ```
- **Calculo del saldo.** Para obtener el saldo de un estudiante en un periodo:
  ```sql
  SELECT SUM(
      CASE
          WHEN s.grupo = 'PAGO' THEN cc.valor
          WHEN s.grupo = 'COBRO' THEN -cc.valor
      END
  ) AS saldo
  FROM cuenta_corriente cc
  JOIN servicio s ON cc.codigo_servicio = s.codigo
  LEFT JOIN pago p ON cc.id_pago = p.id
  WHERE cc.cod_estudiante = %s
    AND cc.codigo_periodo = %s
    AND (cc.id_pago IS NULL OR p.estado <> 'ANULADO')
  ```
- **Campos que no van en formularios:** id (SERIAL), fecha_creacion, fecha. Son autogenerados por la BD.
- **Campos con datalist (autocompletado libre):** facultad de programa, y cualquier FK que referencie otra entidad (estudiante, programa, periodo, servicio, asignatura).
- **Secuencias SERIAL y datos existentes.** Las tablas con SERIAL (matricula, pago, cuenta_corriente) tienen una secuencia interna que genera IDs. Si se insertan datos con ID explicito (ej: en seed.sql), la secuencia no se actualiza automaticamente. Para evitar conflictos al insertar nuevos registros desde la app, ejecutar al final del seed:
  ```sql
  SELECT setval('matricula_id_seq', (SELECT COALESCE(MAX(id), 0) FROM matricula));
  SELECT setval('pago_id_seq', (SELECT COALESCE(MAX(id), 0) FROM pago));
  SELECT setval('cuenta_corriente_id_seq', (SELECT COALESCE(MAX(id), 0) FROM cuenta_corriente));
  ```
  Esto sincroniza la secuencia con el maximo ID existente. COALESCE maneja el caso donde la tabla esta vacia (MAX devuelve NULL).
