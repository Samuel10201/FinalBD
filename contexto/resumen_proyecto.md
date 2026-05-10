RESUMEN DEL PROYECTO — Sistema de Cuenta Corriente del Estudiante
1. Contexto:
Proyecto final de Bases de Datos para una universidad del Caribe colombiano. El sistema gestiona cobros y pagos de matrículas estudiantiles. Grupo de 6 personas.
2. Modelo de Negocio (flujo completo):

Configuración (SUPERVISOR): Crear programas académicos, planes de estudio, periodos, códigos de detalle (servicios), reglas de cobro (precio global y por crédito por programa/periodo), y gestionar usuarios.
Matrícula y cobro (ASISTENTE): Inscribir a un estudiante en un programa para un periodo con una modalidad (global o créditos) y un semestre a cursar. Esto genera los movimientos de COBRO en la cuenta corriente. Puede ser individual o masivo.
Pagos (simulación): El estudiante o asistente registra pagos (por caja o en línea), lo cual genera movimientos de PAGO en la cuenta corriente. El pago tiene su propia estructura (id, fecha, método, monto, estado, referencia).
Balance: La cuenta corriente muestra COBROs - PAGOs = saldo. Cuando llega a cero, el estudiante está al día.

3. Roles del sistema:

ADMINISTRADOR: gestión de usuarios
SUPERVISOR: configuración del sistema (programas, periodos, reglas de cobro, servicios)
ASISTENTE: matrícula, generación de cobro, registro de pagos
ESTUDIANTE: consulta su cuenta corriente, pago en línea

4. Entidades del modelo (9) — tipos exactos en sql/schema.sql:

Periodo: codigo CHAR(6) PK, descripcion VARCHAR(100), fecha_inicio DATE, fecha_fin DATE, estado VARCHAR(15)
Programa Académico: nombre VARCHAR(30) PK, facultad VARCHAR(40), modo VARCHAR(10), duracion INT
Asignatura: codigo CHAR(6) PK, nombre VARCHAR(30), creditos INT, descripcion VARCHAR(100), tipo VARCHAR(10)
Servicio: codigo VARCHAR(4) PK, grupo VARCHAR(5), estado VARCHAR(10), descripcion VARCHAR(100)
Usuario: tipo_id CHAR(2) + id VARCHAR(15) PK compuesta, nombre VARCHAR(50), correo VARCHAR(50) UNIQUE, contrasena VARCHAR(250), rol VARCHAR(15), estado VARCHAR(10), fecha_creacion TIMESTAMP
Estudiante: codigo VARCHAR(8) PK, nombre VARCHAR(50), estado VARCHAR(10), fecha_nacimiento DATE, direccion VARCHAR(60), tipo_id CHAR(2) + id VARCHAR(15) FK a Usuario
Matrícula: id SERIAL PK, modalidad VARCHAR(10), semestre INT, fecha_creacion TIMESTAMP, cod_estudiante VARCHAR(8) FK, cod_periodo CHAR(6) FK, prog_acad VARCHAR(30) FK. UNIQUE(cod_estudiante, cod_periodo, prog_acad)
Cuenta Corriente: id SERIAL PK, fecha TIMESTAMP, descripcion_mov VARCHAR(100), valor NUMERIC(12,2), cod_estudiante VARCHAR(8) FK, tipo_id_usuario CHAR(2) + id_usuario VARCHAR(15) FK, codigo_servicio VARCHAR(4) FK, codigo_periodo CHAR(6) FK, id_pago INT FK nullable
Pago: id SERIAL PK, estado VARCHAR(10), fecha TIMESTAMP, metodo VARCHAR(10), monto NUMERIC(12,2)

5. Relaciones y tablas intermedias:

Costo: prog_academico VARCHAR(30) + cod_periodo CHAR(6) PK compuesta (ambas FK), costo_credito NUMERIC(12,2), costo_global NUMERIC(12,2)
Plan Estudio: nombre_programa VARCHAR(30) + cod_asignatura CHAR(6) PK compuesta (ambas FK), semestre INT

6. Decisiones de diseño importantes:

La modalidad es UNA por matrícula (global O créditos, no ambas)
El saldo es calculado, no almacenado
Todo estudiante tiene usuario con rol ESTUDIANTE
La FK de Estudiante a Usuario es por tipo_id + id (documento de identidad, inmutable)
Cuenta Corriente es entidad (no relación) por su complejidad
Pago es entidad separada de Cuenta Corriente (datos operativos vs contables)
IDs de matricula, pago y cuenta_corriente son SERIAL (autogenerados, no se pasan en INSERT)
Metodos de pago: EN LINEA, CAJA
Estado de pago no tiene DEFAULT, se asigna explicitamente

7. Stack tecnológico acordado:

Backend: Python + Flask
Frontend: HTML/CSS con Jinja2 (sin JavaScript)
Base de datos: PostgreSQL en Supabase (plan gratuito)
Hosting: Vercel (serverless functions)
Conexión BD: psycopg2 (SQL directo, no ORM)

8. Estructura de proyecto acordada:
proyecto/
├── api/
│   └── index.py
├── templates/
├── static/
├── models/
├── routes/
├── services/
├── requirements.txt
└── vercel.json
9. Módulos funcionales:

Autenticación (login con roles)
Gestión de configuración (CRUD programas, asignaturas, periodos, servicios, usuarios, reglas de cobro)
Matrícula (individual y masiva)
Cuenta corriente (consulta, volante)
Pagos (caja y en línea)
Reportes
