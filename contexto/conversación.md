# Conversacion de diseno del proyecto

## 1. Que es serverless?
Modelo donde el codigo solo se ejecuta cuando alguien visita la pagina. No hay servidor permanente.
Vercel toma el archivo Python, lo congela, y lo despierta solo cuando llega una peticion.
Plan gratuito de Vercel funciona asi. Desventaja: la primera visita tras inactividad es lenta (cold start, 1-3 seg).

## 2. index.py vs app.py
index.py es el equivalente a app.py. El nombre y ubicacion (api/index.py) los exige Vercel.
Su contenido: crea la app Flask y registra los blueprints. No tiene rutas directamente.

## 3. Que son los blueprints?
Un blueprint es un grupo de rutas empaquetadas en un objeto de Flask. Permite separar las rutas
de un solo archivo grande en varios archivos por modulo (auth.py, configuracion.py, etc).
Blueprint es una clase incluida en Flask, no requiere instalar nada extra.

Sin blueprints, todas las rutas irian en un solo app.py. Con blueprints, cada archivo en routes/
crea su propio Blueprint y define sus rutas con @nombre_bp.route(). Luego index.py los une
todos con app.register_blueprint().

Ejemplo:
- routes/auth.py crea auth_bp = Blueprint('auth', __name__) y define @auth_bp.route('/login')
- routes/configuracion.py crea config_bp = Blueprint('configuracion', __name__) y define sus rutas
- api/index.py importa ambos y los registra con app.register_blueprint(auth_bp), etc.

El resultado es identico a tener todo en un archivo, pero organizado para trabajo en equipo.

## 4. Que son los archivos en routes/?
Son el app.py desglosado por modulo. Cada archivo define solo las rutas de su area.
index.py los une todos mediante blueprints.

## 5. Que contiene services/?
La logica de negocio y las consultas SQL con psycopg2.
routes/ recibe la peticion HTTP y llama a services/. services/ ejecuta la logica y devuelve el resultado.
routes/ toma el resultado y renderiza el HTML. Separar esto evita archivos inmanejables y permite
que un integrante trabaje en el SQL y otro en el HTML sin estorbarse.

## 6. Como se manejan imagenes con Flask?
Flask sirve cualquier archivo dentro de static/ automaticamente.
En HTML se referencian con: <img src="{{ url_for('static', filename='img/logo.png') }}">

## 7. Como se ejecutan scripts SQL en Supabase?
Supabase tiene un SQL Editor en su panel web. Se copia el contenido de schema.sql ahi y se ejecuta.
Luego seed.sql para datos de prueba. Las tablas aparecen inmediatamente.
Tener los .sql en el repo permite que cualquier integrante vea la estructura sin entrar a Supabase.

## 8. Para que sirve .env.example?
.env guarda variables sensibles (URL de Supabase con contrasena). Nunca se sube a GitHub.
.env.example es una copia sin valores reales que si se sube. Cada companero la copia como .env
y rellena sus datos. No tiene relacion con los scripts SQL, es para la conexion de Flask a la BD.

## 9. Como se controla la vista segun el rol del usuario?
Dos niveles:
- En Flask: al hacer login se guarda el rol en sesion. Cada ruta verifica el rol antes de responder.
  Jinja2 muestra/oculta elementos del menu segun el rol.
- En PostgreSQL: las VIEWs simplifican consultas complejas (ej: calcular saldo), pero no controlan acceso.
  Se usan ambos enfoques.

## 10. Indexacion
Los indices se definen en schema.sql. PostgreSQL crea indices automaticos en PKs y UNIQUEs.
Se agregan indices adicionales en columnas consultadas frecuentemente:
cuenta_corriente.cod_estudiante, cuenta_corriente.codigo_periodo, matricula.cod_estudiante.

## 11. Carpetas obligatorias vs elegidas
- OBLIGATORIO por Vercel: api/, api/index.py, vercel.json
- OBLIGATORIO por Flask: templates/, static/
- OBLIGATORIO por Python/Git: requirements.txt, .gitignore
- ELECCION de organizacion: routes/, services/, models/, sql/

## 12. Administrador - Selector de vista
El admin no tiene una pagina propia de contenido. Tiene una barra superior permanente con:
- Dropdown para cambiar vista (SUPERVISOR / ASISTENTE / ESTUDIANTE)
- Acceso directo a gestion de usuarios (exclusivo de ADMIN)
El admin ve exactamente la interfaz del rol seleccionado. En sesion se guardan dos valores:
rol_real=ADMIN y vista_actual=SUPERVISOR (por ejemplo). Las rutas usan vista_actual para mostrar
contenido, pero rol_real nunca cambia.

## 13. Cuenta corriente al crear estudiante
Al crear un estudiante (SUPERVISOR), se crea automaticamente su cuenta corriente.
Esto permite registrar cobros previos a matricula (examenes medicos, admision, etc).
Los cobros previos los registra el ASISTENTE, no el SUPERVISOR.

## 14. Matricula masiva
Flujo:
1. El asistente selecciona un programa.
2. El sistema busca todos los estudiantes activos de ese programa en el periodo actual.
3. Para cada estudiante, genera matricula para el periodo siguiente con semestre+1.
4. Se conserva la modalidad de la matricula anterior del estudiante.
5. Si el estudiante esta en el ultimo semestre (duracion del programa), no se genera matricula.
6. Se generan los cobros correspondientes para cada matricula creada.

## 15. Pantallas del sistema (22 en total)

### Auth
1. Login: correo + contrasena, redirige al dashboard del rol.

### Administrador
2. Barra de admin: elemento permanente superior. Dropdown cambiar vista + acceso a usuarios.
3. Gestion de usuarios: CRUD tipo_id, id, nombre, correo, contrasena, rol, estado.

### Supervisor - Configuracion
4. Estudiantes: CRUD completo. Al crear estudiante se crea su cuenta corriente automaticamente.
5. Programas academicos: CRUD nombre, facultad, modo, duracion. Muestra plan de estudio completo.
6. Asignaturas: CRUD codigo, nombre, creditos, descripcion, tipo.
7. Plan de estudio: asignar asignaturas a programa con semestre. Vista: programa > semestre > asignaturas con creditos.
8. Periodos: CRUD codigo, descripcion, fecha inicio, fecha fin, estado.
9. Servicios (codigos de detalle): CRUD codigo, grupo (COBRO/PAGO), estado, descripcion.
10. Costos (reglas de cobro): seleccionar programa + periodo, definir costo por credito y costo global.

### Asistente - Gestion de cobro y pagos
11. Matricula individual: formulario estudiante, programa, periodo, modalidad, semestre. Genera COBROs.
12. Matricula masiva: seleccionar programa, genera matriculas para periodo siguiente con semestre+1.
13. Registro de pago (caja): formulario estudiante, monto, metodo, referencia. Genera PAGOs.
14. Consulta cuenta corriente: buscar estudiante, ver cobros/pagos con codigo de detalle, saldo por periodo.

### Estudiante
15. Mi perfil y plan de estudio: datos personales + matricula actual + asignaturas por semestre con creditos.
16. Mi cuenta corriente: cobros y pagos con codigo de detalle y descripcion. Balance por periodo.
17. Pago en linea: simulacion de pago, genera movimiento de PAGO.

### Reportes (acceso: SUPERVISOR y ADMIN)
18. Estudiantes por programa: filtro periodo + programa. Lista estudiante, programa, modalidad, monto.
19. Ingreso esperado: filtro periodo + programa. Total que se deberia recaudar.
20. Estudiantes pendientes de pago: filtro periodo + programa. Estudiantes con saldo pendiente.
21. Ingreso real: filtro periodo + programa. Total de pagos recibidos.
22. Cartera: filtro periodo + programa. Estudiantes que deben, valor individual, total cuentas por cobrar.

## 16. Que puede ver el estudiante segun el modelo
El modelo soporta:
- Informacion personal (tabla Estudiante)
- Matricula actual: programa, periodo, semestre, modalidad (tabla Matricula)
- Plan de estudio de su programa: asignaturas por semestre con creditos (tabla Plan Estudio)
- Cuenta corriente: cobros, pagos, saldo (tabla Cuenta Corriente)
El modelo NO soporta: asignaturas aprobadas/reprobadas, notas, progreso academico.
El sistema es de cuenta corriente financiera, no de gestion academica.

## 17. Balance de cuenta corriente
En la cuenta corriente de un estudiante, los codigos de detalle asociados a COBRO se restan
y los asociados a PAGO se suman. Cuando el estudiante esta al dia, el balance da cero.
