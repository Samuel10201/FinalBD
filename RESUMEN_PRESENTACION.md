# Resumen del Proyecto — Presentación Bases de Datos

---

## 2. Problema que se abarca

Sistema de **Cuenta Corriente Universitaria**: gestión integral del flujo financiero y académico de una universidad. El sistema resuelve:

- **Gestión de matrícula**: registrar la inscripción de estudiantes a periodos académicos (individual o masiva por programa), calculando automáticamente el cobro según modalidad (global o por créditos).
- **Cuenta corriente estudiantil**: registrar cobros (deudas) y pagos (abonos) por estudiante, manteniendo un saldo actualizado con trazabilidad completa de cada movimiento.
- **Configuración académica**: administrar programas académicos, asignaturas, planes de estudio y estudiantes.
- **Configuración operativa**: administrar periodos académicos (semestral/intersemestral), servicios de cobro/pago, y costos por programa/periodo.
- **Reportes financieros**: ingreso esperado vs. real, estudiantes pendientes de pago, cartera.

El sistema maneja 4 roles (Administrador, Supervisor, Asistente, Estudiante) con permisos diferenciados.

---

## 3. Arquitectura Técnica

### RDBMS
**PostgreSQL** — hospedado en **Supabase** (PostgreSQL gestionado en la nube).

### Herramienta de desarrollo de la aplicación
**Python + Flask** (microframework web). Arquitectura MVC en 3 capas:
- **Presentación**: Templates HTML con Jinja2 + CSS puro (sin frameworks JS)
- **Controladores**: 7 Blueprints de Flask (`auth`, `config_academica`, `config_operativa`, `matricula`, `pagos`, `cuenta_corriente`, `reportes`)
- **Servicios**: Capa de lógica de negocio con SQL directo (sin ORM)
- **Datos**: Pool de conexiones a PostgreSQL

### Driver de conexión
**psycopg2-binary** — driver nativo de PostgreSQL para Python
- `SimpleConnectionPool(1, 5)` — pool de 1 a 5 conexiones
- `RealDictCursor` — retorna filas como diccionarios Python
- Queries parametrizadas con `%s` (prevención de SQL injection)
- Transacciones con context manager (`with conn:` → autocommit/rollback)

### Dependencias completas
| Librería | Uso |
|---|---|
| Flask | Framework web |
| psycopg2-binary | Driver PostgreSQL |
| bcrypt | Hash de contraseñas |
| python-dotenv | Variables de entorno |
| Vercel | Despliegue serverless |

### Despliegue
**Vercel** (serverless Python) — la app se despliega como función serverless conectándose a Supabase.

---

## 4. Motor de Base de Datos — PostgreSQL

### Modelo de datos: 11 tablas

```
┌──────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│ periodo  │────<│      matricula      │>────│ programa_academico   │
│ (CHAR 6) │     │ (SERIAL PK)         │     │ (VARCHAR 30 PK)      │
│          │     │ modalidad, semestre  │     │ facultad, modo,      │
│          │     │ cod_estudiante (FK)  │     │ duracion             │
│          │     │ cod_periodo (FK)     │     └──────────┬───────────┘
│          │     │ prog_acad (FK)       │                │
│          │     │ UNIQUE(est,per,prog) │     ┌──────────┴───────────┐
└────┬─────┘     └──────────────────────┘     │     plan_estudio     │
     │                                        │ (PK compuesta)       │
     │           ┌──────────────────────┐     │ nombre_programa (FK) │
     ├──────────<│       costo          │>────│ cod_asignatura (FK)  │
     │           │ (PK compuesta)       │     │ semestre             │
     │           │ costo_credito        │     └──────────┬───────────┘
     │           │ costo_global         │                │
     │           └──────────────────────┘     ┌──────────┴───────────┐
     │                                        │    asignatura        │
     │                                        │ (CHAR 6 PK)         │
     │                                        │ nombre, creditos,    │
     │                                        │ tipo, descripcion    │
     │                                        └──────────────────────┘
     │
     │           ┌──────────────────────┐     ┌──────────────────────┐
     ├──────────<│  cuenta_corriente    │>────│     servicio         │
     │           │ (SERIAL PK)          │     │ (VARCHAR 4 PK)       │
     │           │ descripcion_mov      │     │ grupo: COBRO|PAGO    │
     │           │ valor (>0)           │     │ estado, descripcion  │
     │           │ cod_estudiante (FK)  │     └──────────────────────┘
     │           │ id_usuario (FK)      │
     │           │ codigo_servicio (FK) │     ┌──────────────────────┐
     │           │ codigo_periodo (FK)  │     │       pago           │
     │           │ id_pago (FK, NULL)  │────>│ (SERIAL PK)          │
     │           └──────────┬──────────┘     │ estado: PENDIENTE|   │
     │                      │                │  COMPLETADO|ANULADO  │
     │                      │                │ metodo, monto (>0)   │
     │           ┌──────────┴──────────┐     └──────────────────────┘
     │           │                     │
┌────┴───────┐  ┌┴─────────────────────┐
│  usuario   │──│     estudiante       │
│ (id PK)    │  │ (codigo PK)          │
│ tipo_id,   │  │ nombre, estado,      │
│ nombre,    │  │ fecha_nacimiento,    │
│ correo     │  │ direccion            │
│ (UNIQUE),  │  │ id (FK → usuario)    │
│ contrasena,│  └──────────────────────┘
│ rol, estado│
└────────────┘
```

### Características destacadas de la BD

**CHECK constraints extensivos (16 en total):**
- Validación con regex: `periodo.codigo ~ '^[0-9]{4}(00|10|20|30|40)$'`, `asignatura.codigo ~ '^[A-Z]{3}[0-9]{3}$'`, `servicio.codigo ~ '^[A-Z]{3,4}$'`, `usuario.correo` con regex de email, `estudiante.codigo ~ '^[0-9]{2,8}$'`
- Dominios enumerados via CHECK: estados (`ACTIVO/INACTIVO`), roles (`ADMINISTRADOR/ESTUDIANTE/SUPERVISOR/ASISTENTE`), modalidades (`GLOBAL/CREDITO`), estados de pago (`PENDIENTE/COMPLETADO/ANULADO`), métodos de pago (`EN LINEA/CAJA`), tipos de documento (`CC/TI/CE/PP/RC/NI/PE`), grupos de servicio (`COBRO/PAGO`), tipo asignatura (`OBLIGATORIA/ELECTIVA`), modo programa (`PRESENCIAL/REMOTO`)
- Rangos numéricos: `creditos BETWEEN 0 AND 10`, `duracion BETWEEN 1 AND 12`, `valor > 0`, `monto > 0`, `costo_credito > 0`, `costo_global > 0`

**Índices explícitos (3, además de los automáticos de PKs y UNIQUEs):**
- `idx_cuenta_cod_estudiante` en `cuenta_corriente(cod_estudiante)` — acelera consultas de estado de cuenta
- `idx_matricula_cod_periodo` en `matricula(cod_periodo)` — acelera reportes por periodo
- `idx_matricula_prog_acad` en `matricula(prog_acad)` — acelera reportes por programa

**Claves:**
- 9 PKs simples (5 naturales: periodo, programa, asignatura, servicio, usuario; 3 surrogadas SERIAL: matricula, pago, cuenta_corriente; 1 código de negocio: estudiante)
- 2 PKs compuestas: `costo(prog_academico, cod_periodo)`, `plan_estudio(nombre_programa, cod_asignatura)`
- 10 FKs, de las cuales solo 1 es nullable (`cuenta_corriente.id_pago` — los cobros no tienen pago asociado)
- 1 UNIQUE adicional: `usuario(correo)` y `matricula(cod_estudiante, cod_periodo, prog_acad)`

**Decisiones de diseño notables:**
- Sin ON DELETE CASCADE — toda eliminación requiere lógica explícita en la aplicación
- Sin triggers, vistas ni procedimientos almacenados — toda lógica de negocio en la capa de servicios Python
- Soft delete (desactivación lógica) en lugar de borrado físico para usuarios y estudiantes
- La tabla `pago` es indirecta — se conecta al estudiante solo a través de `cuenta_corriente.id_pago`
- `cuenta_corriente.valor` siempre positivo; la semántica cobro/pago la define `servicio.grupo`

### Datos semilla (seed.sql)

~8,670 líneas, ~1.7 MB. Generado por un script Python (`generar_seed.py`).

| Tabla | Registros | Descripción |
|---|---|---|
| periodo | 15 | 5 años (2022-2026) × 3 tipos (10=1er sem, 20=intersemestral, 30=2do sem) |
| programa_academico | 14 | 6 facultades (Ingeniería, Salud, Jurídicas, Humanidades, Económicas, Básicas) |
| asignatura | 140 | 10 por programa (8 obligatorias + 2 electivas) |
| servicio | 9 | 5 de cobro + 4 de pago |
| usuario | 530 | 30 staff + 500 estudiantes (contraseñas bcrypt) |
| estudiante | 500 | Códigos 200001-200500, vinculados a usuarios |
| plan_estudio | 140 | 10 asignaturas × 14 programas |
| costo | 140 | Incremento semestral progresivo por programa |
| matrícula | 1,853 | Múltiples semestres por estudiante |
| pago | 1,723 | Mayoría COMPLETADO |
| cuenta_corriente | 3,576 | ~2 movimientos por matrícula (1 cobro + 1 pago) |

---

### Inventario completo de consultas SQL por servicio

#### Estadísticas globales
| Tipo de operación | Cantidad |
|---|---|
| SELECT | ~40 sentencias |
| INSERT | ~12 sentencias |
| UPDATE | ~14 sentencias |
| DELETE | 4 sentencias |
| UPSERT (ON CONFLICT) | 1 sentencia |
| **Total** | **~71 sentencias SQL** |

#### Patrones SQL avanzados utilizados

| Patrón | Cantidad | Dónde se usa |
|---|---|---|
| JOIN / LEFT JOIN | 15+ consultas | Reportes, cuenta corriente, matrícula, listados |
| Subqueries (en WHERE y SELECT) | 3 | Actualizar/desactivar estudiante, reporte por modalidad |
| Subquery correlacionada | 1 | Cálculo de monto por créditos en reporte |
| SUM() | 5 consultas | Saldo, ingresos, créditos por semestre |
| CASE WHEN | 3 consultas | Saldo (COBRO → negativo, PAGO → positivo), monto por modalidad |
| GROUP BY + HAVING | 1 | Reporte de pendientes de pago (filtra saldo < 0) |
| ON CONFLICT DO UPDATE (UPSERT) | 1 | Crear o actualizar costo |
| RETURNING | 4 | Obtener ID/datos del registro recién creado |
| ILIKE | 6+ consultas | Búsqueda case-insensitive |
| DISTINCT | 1 | Matrícula masiva |
| CURRENT_DATE | 2 | Filtro de periodos futuros |
| NOT LIKE | 1 | Excluir periodos intersemestrales |
| ABS() | 1 | Valor absoluto de saldo pendiente |
| COALESCE() | 1 | Manejo de NULL en suma de créditos |
| Query dinámica (WHERE 1=1) | 5 funciones | Filtros opcionales en búsquedas |
| LIMIT / OFFSET | 4 funciones | Paginación |

#### Detalle por servicio

**auth_service.py** — 8 consultas (usuario, estudiante)
- Login: `SELECT ... FROM usuario WHERE correo = %s` + verificación bcrypt en Python
- CRUD usuarios: INSERT con `RETURNING`, UPDATE condicional (con/sin contraseña), desactivación atómica usuario+estudiante
- Listado: búsqueda con `ILIKE` en nombre/correo/id, paginación `LIMIT/OFFSET`

**cuenta_service.py** — 5 consultas (estudiante, cuenta_corriente, servicio, pago, periodo)
- Consulta de movimientos: `JOIN servicio`, `LEFT JOIN pago`, filtro opcional por periodo
- Cálculo de saldo: `SUM(CASE WHEN grupo='PAGO' THEN valor WHEN grupo='COBRO' THEN -valor END)`, excluye pagos anulados con `(id_pago IS NULL OR p.estado <> 'ANULADO')`

**pago_service.py** — 3 consultas implementadas (pago, cuenta_corriente, servicio)
- Registro de pago: **transacción atómica** con 2 INSERTs encadenados (pago → cuenta_corriente), usando `RETURNING id` para enlazar ambos
- 4 funciones stub pendientes (confirmar, anular, obtener, listar)

**reporte_service.py** — 6 consultas (las más complejas del proyecto)
- **Estudiantes por programa**: `CASE WHEN modalidad='GLOBAL' THEN costo_global ELSE (subquery correlacionada con SUM de créditos × costo_credito)` — 3 JOINs
- **Pendientes de pago** (consulta más compleja): `SUM(CASE WHEN...)` + `GROUP BY` + `HAVING saldo < 0` + `ABS()` — 4 JOINs + LEFT JOIN
- **Ingreso real**: `SUM(cc.valor)` con filtro `s.grupo = 'PAGO' AND p.estado <> 'ANULADO'` — 3 JOINs + LEFT JOIN
- **Perfil estudiante**: 3 SELECTs secuenciales (datos personales → última matrícula con JOIN periodo → plan de estudio con JOIN asignatura)

**config_academica_service.py** — 17 consultas (estudiante, usuario, programa, asignatura, plan_estudio)
- Crear estudiante: transacción atómica con 2 INSERTs (usuario + estudiante)
- Actualizar/desactivar estudiante: transacciones atómicas con subquery `WHERE id = (SELECT id FROM estudiante WHERE codigo = %s)`
- Eliminar asignatura: transacción atómica con 2 DELETEs (plan_estudio primero, luego asignatura)
- Actualizar asignatura en plan: transacción atómica que actualiza 2 tablas (plan_estudio + asignatura)

**matricula_service.py** — 12 consultas (todas las tablas excepto usuario)
- **Crear matrícula individual** (transacción más grande del proyecto): hasta 9 operaciones atómicas en una sola transacción — 7 SELECTs de validación + INSERT matrícula con `RETURNING id` + INSERT cuenta_corriente (cobro automático). Calcula monto por modalidad: global directo de `costo`, o créditos con `SUM(a.creditos) FROM plan_estudio JOIN asignatura`
- **Periodos para matrícula**: `WHERE fecha_inicio > CURRENT_DATE` (solo futuros). Masiva excluye intersemestrales: `AND codigo NOT LIKE '%%20'`
- **Estudiantes para masiva**: `SELECT DISTINCT ... FROM matricula JOIN estudiante WHERE cod_periodo = (periodo anterior del programa)` — deduce periodo anterior con `cod_periodo < %s ORDER BY cod_periodo DESC LIMIT 1`

**config_operativa_service.py** — 14 consultas (periodo, servicio, costo)
- CRUD estándar de periodos y servicios con queries dinámicas (`WHERE 1=1` + filtros opcionales con `ILIKE`)
- **UPSERT de costo** (único del proyecto): `INSERT INTO costo ... ON CONFLICT (prog_academico, cod_periodo) DO UPDATE SET costo_credito = EXCLUDED.costo_credito, costo_global = EXCLUDED.costo_global`
- Soft delete (desactivación) para periodos y servicios

#### Transacciones atómicas críticas

| Operación | Tablas | Sentencias |
|---|---|---|
| Crear matrícula | matricula + cuenta_corriente + (7 tablas de validación) | 7 SELECT + 2 INSERT |
| Registrar pago | pago + cuenta_corriente | 2 INSERT |
| Crear estudiante | usuario + estudiante | 2 INSERT |
| Actualizar estudiante | estudiante + usuario | 2 UPDATE (con subquery) |
| Desactivar estudiante | usuario + estudiante | 2 UPDATE (con subquery) |
| Crear asignatura | asignatura + plan_estudio | 2 INSERT |
| Eliminar asignatura | plan_estudio + asignatura | 2 DELETE |
| Actualizar asignatura en plan | plan_estudio + asignatura | 2 UPDATE |

---

## 5. Retos Superados

### Retos de base de datos
- **Diseño del modelo cuenta corriente**: modelar cobros y pagos en una sola tabla (`cuenta_corriente`) donde `valor` siempre es positivo y la semántica débito/crédito la define el `servicio.grupo` (COBRO vs PAGO). El saldo se calcula dinámicamente con `SUM(CASE WHEN...)`.
- **Transacción atómica de matrícula**: la operación más compleja del sistema — 9 operaciones secuenciales que deben ser atómicas (validar estudiante, programa, periodo, duplicados, costo, créditos, servicio → insertar matrícula → generar cobro automático en cuenta corriente).
- **Cálculo de montos por modalidad**: implementar un `CASE WHEN` con subquery correlacionada que calcula `SUM(creditos) × costo_credito` cuando la modalidad es CREDITO, vs. `costo_global` cuando es GLOBAL.
- **UPSERT para costos**: usar `ON CONFLICT ... DO UPDATE SET` de PostgreSQL para simplificar la operación crear/actualizar en una sola sentencia.
- **Reporte de pendientes de pago**: la consulta más compleja del proyecto usa `SUM + CASE WHEN + GROUP BY + HAVING < 0 + ABS()` con 4 JOINs para encontrar estudiantes con saldo negativo.
- **Migración de estructura de periodos**: cambiar la codificación de periodos de 10/20 a 10/20/30 (primer semestre/intersemestral/segundo semestre), propagando el cambio a ~2,300 registros existentes en el seed.
- **Pool de conexiones en serverless**: manejar un pool de conexiones (`SimpleConnectionPool`) en un entorno Vercel serverless que no mantiene estado entre invocaciones.
- **Integridad sin CASCADE**: al no usar ON DELETE CASCADE, toda eliminación requiere lógica manual — ejemplo: eliminar asignatura requiere primero borrar plan_estudio, luego asignatura, en transacción.

### Retos de aplicación
- **Matrícula masiva**: deducir automáticamente el periodo anterior de un programa, encontrar sus estudiantes activos, calcular semestre+1, y generar matrícula+cobro para cada uno.
- **Seguridad multi-rol**: implementar un sistema de permisos donde el Administrador puede "ver como" otro rol sin perder su acceso real.
- **Prevención de caché post-logout**: evitar que el botón "atrás" del navegador muestre páginas protegidas con headers `Cache-Control: no-store`.
- **Validaciones en dos capas**: constraints CHECK en la BD (última línea de defensa) + validaciones en el backend Python + validaciones HTML5 en el frontend (pattern, required, min/max).

---

## 6. Uso de IA

### En el modelo de datos (schema.sql)
- Apoyo en el diseño del modelo relacional: definición de tablas, relaciones, cardinalidades
- Sugerencias de CHECK constraints con regex para validación de formatos (códigos de periodo, asignatura, servicio, correo)
- Revisión de integridad referencial y decisiones de diseño (PK naturales vs surrogadas, nullable FK para id_pago)

### En los scripts de datos (seed.sql / generar_seed.py)
- Generación del script Python que produce el seed.sql con ~8,670 líneas de datos coherentes
- Datos realistas: nombres de programas, asignaturas con códigos semánticos, progresión de costos semestrales, distribución de estudiantes por programas
- Contraseñas hasheadas con bcrypt incluidas en el seed

### En las consultas SQL (services/)
- Construcción de queries complejas: JOINs múltiples, subqueries correlacionadas, CASE WHEN, GROUP BY + HAVING
- Implementación del patrón UPSERT con ON CONFLICT
- Optimización de consultas dinámicas con el patrón WHERE 1=1
- Cálculo de saldo con SUM + CASE WHEN excluyendo pagos anulados

### En la interfaz (templates/ + routes/)
- Estructura de templates con herencia Jinja2 (base.html → páginas específicas)
- Patrón CRUD con tabs (Buscar/Crear/Actualizar/Desactivar) consistente en todas las secciones
- Integración de datalist para autocompletado en formularios
- Sistema de flash messages para feedback al usuario

### En la lógica de negocio (services/)
- Diseño de transacciones atómicas multi-tabla
- Excepciones personalizadas para errores de negocio
- Patrón de matrícula masiva con detección automática de periodo anterior

### En la seguridad
- Implementación de bcrypt para hash de contraseñas
- Decoradores de autenticación y autorización por rol
- Headers anti-caché para protección post-logout
- Manejo de errores UniqueViolation con mensajes amigables

---

## 7. Roles del Grupo

| Integrante | Módulos | Pantallas |
|---|---|---|
| Samuel | BD + Infraestructura + Auth + Admin: schema.sql, seed.sql, db.py, base.html, CSS, login, sesiones, CRUD usuarios, selector de vista admin | 1 (Login), 2 (Barra admin), 3 (Usuarios) |
| Rafael Mejía | Configuración académica: CRUD estudiantes (con creación atómica usuario+estudiante), programas, asignaturas, plan de estudio | 4 (Estudiantes), 5 (Programas), 6 (Asignaturas), 7 (Plan de estudio) |
| Frank Montaño | Configuración operativa: CRUD periodos, servicios, costos (UPSERT) | 8 (Periodos), 9 (Servicios), 10 (Costos) |
| Camilo Morales | Matrícula: individual (con generación automática de cobro) y masiva (semestre+1, excluye último semestre) | 11 (Matrícula individual), 12 (Matrícula masiva) |
| Andrés Martínez | Pagos + Cuenta corriente: registro pago caja, pago en línea, consulta de movimientos y saldo | 13 (Pago caja), 14 (Consulta CC), 16 (Mi cuenta), 17 (Pago en línea) |
| Isabella Moreno | Perfil estudiante + Reportes: perfil con plan de estudio, 5 reportes financieros con filtros | 15 (Mi perfil), 18-22 (Reportes) |

---

## Anexo: Resumen de Números

| Métrica | Valor |
|---|---|
| Tablas en la BD | 11 |
| CHECK constraints | 16 |
| Foreign Keys | 10 |
| Índices explícitos | 3 |
| Sentencias SQL en el backend | ~71 |
| JOINs en queries | 15+ |
| Transacciones atómicas | 8 operaciones críticas |
| Blueprints (módulos) | 7 |
| Templates HTML | 20+ |
| Roles de usuario | 4 |
| Registros en seed | ~8,500+ |
| Líneas de seed.sql | ~8,670 |
