# Proyecto: Sistema de Cuenta Corriente del Estudiante

## Contexto del proyecto
Proyecto final de Bases de Datos. Sistema que gestiona cobros y pagos de matriculas estudiantiles.
Grupo de 6 personas. Universidad del Caribe colombiano.

### Flujo de negocio
1. SUPERVISOR configura: programas, planes de estudio, periodos, servicios, reglas de cobro, usuarios.
2. ASISTENTE ingresa informacion del estudiante (semestre, modalidad de cobro) y genera cobros individuales o masivos -> genera COBROs en cuenta corriente.
3. Estudiante/Asistente registra PAGOs (caja o en linea) -> genera movimientos de PAGO.
4. Balance = COBROs - PAGOs. Saldo cero = al dia.

### Roles
- ADMINISTRADOR: acceso a todas las funcionalidades del sistema.
- SUPERVISOR: configuracion del sistema (programas, periodos, reglas de cobro, servicios, estudiantes).
- ASISTENTE: ingreso de datos del estudiante, semestre y modalidad de cobro. Generacion de cobro individual y masivo. Registro de pagos.
- ESTUDIANTE: consulta su cuenta corriente, pago en linea.

### Entidades (9)
Periodo, Programa Academico, Asignatura, Servicio, Usuario, Estudiante, Matricula, Cuenta Corriente, Pago.

### Tablas intermedias (2)
Costo (programa+periodo), Plan Estudio (programa+asignatura).

### Decisiones de diseno
- Modalidad es por matricula (global O creditos, no ambas).
- Saldo es calculado, no almacenado.
- Todo estudiante tiene usuario con rol ESTUDIANTE.
- FK Estudiante->Usuario por tipo_id + id (documento de identidad).
- Cuenta Corriente es entidad, no relacion.
- Pago es entidad separada de Cuenta Corriente.
- IDs de matricula, pago y cuenta_corriente son SERIAL (autogenerados). No se crean ni modifican manualmente.
- Metodos de pago: EN LINEA, CAJA.
- Modalidades de matricula: GLOBAL, CREDITO.

### Documentos de referencia
- Modelo de datos, reglas de negocio, arquitectura y asignacion de trabajo: `contexto/guia_proyecto.md`
- Esquema de la BD (fuente de verdad para tipos, restricciones y formatos): `sql/schema.sql`

### Reglas de negocio (creacion y eliminacion)

#### Transacciones (BEGIN/COMMIT)
- Crear estudiante: crea usuario (rol ESTUDIANTE) + estudiante + cuenta corriente en una sola transaccion.
- Registrar pago: crea el pago + el movimiento en cuenta corriente en una sola transaccion.

#### Creacion con dependencias
- Crear asignatura: debe asociarse a un programa academico existente y asignarse a un plan de estudio. Si el programa no existe, se ofrece crearlo.
- Crear matricula: requiere estudiante, programa, periodo, y un costo definido (programa+periodo). Si alguno no existe, se ofrece crearlo.
- Crear costo: requiere programa y periodo existentes. Si alguno no existe, se ofrece crearlo. Si la combinacion ya existe, se actualiza (upsert).
- Patron general: si el usuario referencia una entidad que no existe, se le ofrece crearla o elegir una existente.

#### Interfaz: campos con referencia a otras entidades
- Usar datalist de HTML (autocompletado con opciones existentes + libertad de escribir).

#### Cobros
- Cobro por matricula: se genera desde la matricula, usa tabla Costo para calcular monto segun modalidad.
- Cobro por servicio: se genera directamente asociando un servicio de grupo COBRO a la cuenta corriente. El valor viene del servicio.

#### Eliminacion y proteccion de datos
- Soft delete (desactivar con estado = INACTIVO): estudiante, usuario, servicio, periodo, programa academico.
- No se permite eliminar entidades con dependencias activas (RESTRICT en FK).
- No se permite eliminar pagos. Para anular: estado = ANULADO. Un pago anulado no cuenta en el saldo.
- Al desactivar un usuario-estudiante, se desactivan ambos registros (usuario y estudiante).
- Eliminar asignatura: se elimina tambien de planes de estudio. El costo global del programa no cambia automaticamente.
- Eliminar servicio: no se borra de cuentas corrientes existentes (historial se mantiene).
- No se eliminan movimientos de cuenta corriente.

#### Validaciones (implementadas como CHECK en la BD)
- Periodo: codigo CHAR(6), formato YYYYXX donde XX es 00, 10, 20, 30 o 40. Regex: `'^[0-9]{4}(00|10|20|30|40)$'`
- Asignatura: codigo CHAR(6), formato AAA999. Regex: `'^[A-Z]{3}[0-9]{3}$'`
- Servicio: codigo VARCHAR(4), formato 3-4 letras mayusculas. Regex: `'^[A-Z]{3,4}$'`
- Estudiante: codigo VARCHAR(8), 2-8 digitos. Regex: `'^[0-9]{2,8}$'`
- tipo_id de usuario: CC, TI, CE, PP, RC, NI, PE.
- Periodos no se pueden solapar en fechas (validar en servicio, no en BD).
- Matricula unica por estudiante+programa+periodo (UNIQUE constraint en BD).
- No se genera cobro por matricula si no existe un costo definido para programa+periodo (validar en servicio).

#### Estados de Pago
- PENDIENTE, COMPLETADO, ANULADO.
- No tiene DEFAULT. El estado se asigna explicitamente al crear el pago.

## Stack
- Backend: Python + Flask
- Frontend: HTML/CSS con Jinja2 (templates de Flask)
- Base de datos: PostgreSQL en Supabase (plan gratuito)
- Hosting: Vercel (plan gratuito, serverless functions)
- Conexion BD: psycopg2 (SQL directo, sin ORM)

## Perfil del usuario
- Estudiante de Ingenieria de Sistemas.
- Ha trabajado con Flask una sola vez. Nunca ha trabajado con Supabase.
- Quiere aprender estas herramientas a traves del proyecto, no solo completarlo.
- Necesita explicaciones detalladas de por que se hacen las cosas, no solo como.

## Reglas para Claude
- Idioma: espanol.
- No implementar codigo sin que el usuario lo pida. Primero discutir y luego ejecutar.
- No crear ni modificar archivos (codigo, memoria, configuracion) sin mostrar el contenido al usuario primero y recibir aprobacion.
