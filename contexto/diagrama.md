# Estructura del proyecto

## Diagrama de carpetas y archivos

proyecto/
├── api/
│   └── index.py              ← Punto de entrada (Vercel). Crea la app Flask y registra blueprints.
│
├── routes/                   ← Rutas (URLs) agrupadas por modulo (blueprints de Flask).
│   ├── __init__.py
│   ├── auth.py               ← Login, logout, sesion.
│   ├── config_academica.py   ← CRUD estudiantes, programas, asignaturas, plan de estudio.
│   ├── config_operativa.py   ← CRUD periodos, servicios, costos.
│   ├── matricula.py          ← Inscripcion individual y masiva.
│   ├── cuenta_corriente.py   ← Consulta saldo, volante.
│   ├── pagos.py              ← Registro caja, simulacion en linea.
│   └── reportes.py           ← Consultas y resumenes.
│
├── services/                 ← Logica de negocio y consultas SQL (psycopg2).
│   ├── __init__.py
│   ├── auth_service.py
│   ├── config_academica_service.py
│   ├── config_operativa_service.py
│   ├── matricula_service.py
│   ├── cuenta_service.py
│   ├── pago_service.py
│   └── reporte_service.py
│
├── models/                   ← Conexion a la base de datos.
│   ├── __init__.py
│   └── db.py                 ← Funcion de conexion psycopg2 a Supabase.
│
├── templates/                ← Archivos HTML con Jinja2. Nombre obligatorio de Flask.
│   ├── base.html             ← Layout principal (navbar, estructura comun).
│   ├── auth/
│   │   └── login.html
│   ├── admin/
│   │   └── usuarios.html             ← CRUD usuarios (solo ADMIN).
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
│   │   ├── registro.html             ← Pago por caja (ASISTENTE).
│   │   └── en_linea.html             ← Pago en linea (ESTUDIANTE).
│   ├── cuenta_corriente/
│   │   └── consulta.html             ← Buscar cuenta de un estudiante (ASISTENTE).
│   ├── estudiante/
│   │   ├── perfil.html               ← Info personal + plan de estudio.
│   │   └── cuenta.html               ← Cuenta corriente del estudiante.
│   └── reportes/
│       ├── estudiantes_programa.html
│       ├── ingreso_esperado.html
│       ├── pendientes_pago.html
│       ├── ingreso_real.html
│       └── cartera.html
│
├── static/                   ← Archivos estaticos (CSS, imagenes). Nombre obligatorio de Flask.
│   ├── css/
│   └── img/
│
├── sql/                      ← Scripts de base de datos.
│   ├── schema.sql            ← DDL: CREATE TABLE, CREATE INDEX. Fuente de verdad del modelo.
│   └── seed.sql              ← Datos de prueba (INSERTs). Incluye setval para secuencias SERIAL.
│
├── .env.example              ← Plantilla de variables de entorno (sin valores reales).
├── .gitignore                ← Archivos que Git debe ignorar (.env, __pycache__, etc).
├── requirements.txt          ← Dependencias Python (flask, psycopg2, etc).
├── vercel.json               ← Configuracion de despliegue en Vercel.
└── README.md                 ← Instrucciones para el equipo.

## Flujo de una peticion

Navegador → Vercel → api/index.py → routes/*.py → services/*.py → PostgreSQL (Supabase)
                                         ↓
                                   templates/*.html + static/css/
