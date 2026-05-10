# Conceptos para scripts SQL en PostgreSQL

## 1. CREATE TABLE y tipos de dato

CREATE TABLE define una tabla con columnas y sus tipos. Sintaxis:

    CREATE TABLE nombre (
        columna TIPO,
        columna TIPO
    );

Tipos principales:
- VARCHAR(n): texto variable, máximo n caracteres.
- CHAR(n): texto fijo de exactamente n caracteres.
- INTEGER / INT: número entero.
- NUMERIC(p, s): número con decimales exactos. p = dígitos totales, s = decimales.
- DATE: solo fecha.
- TIMESTAMP: fecha + hora.
- SERIAL: entero autoincremental (atajo para INTEGER + secuencia + DEFAULT).

SERIAL no es un tipo real. Internamente crea una secuencia separada.
Los IDs generados por SERIAL no se reciclan ni son necesariamente consecutivos.
Alternativa moderna: GENERATED ALWAYS AS IDENTITY (rechaza asignación manual).

---

## 2. Restricciones de columna

Reglas que PostgreSQL hace cumplir automáticamente en cada INSERT/UPDATE.

- NOT NULL: la columna no puede estar vacía. NULL y cadena vacía ('') no son lo mismo.
- DEFAULT valor: valor automático cuando la columna se omite en el INSERT. No aplica si se pasa NULL explícitamente.
- UNIQUE: no permite valores repetidos. Permite múltiples NULLs (NULL ≠ NULL).
- CHECK (condición): valida una condición booleana. Si evalúa a NULL, lo deja pasar (solo rechaza FALSE).

PRIMARY KEY = NOT NULL + UNIQUE. Solo una por tabla.

Combinar NOT NULL + DEFAULT protege ambos flancos: DEFAULT cubre la omisión, NOT NULL impide el NULL explícito.

Se pueden nombrar restricciones para mensajes de error más claros:

    CONSTRAINT nombre_restriccion CHECK (condicion)

El orden de las restricciones en la columna no importa funcionalmente (solo convención).

---

## 3. Llaves foráneas y orden de creación

FK: columna que apunta a la PK de otra tabla. Garantiza integridad referencial.

Sintaxis en línea (FK de 1 columna):

    cod_editorial CHAR(6) NOT NULL REFERENCES editorial(codigo)

Sintaxis al final (obligatoria para FK compuesta):

    FOREIGN KEY (col1, col2) REFERENCES otra_tabla(col1, col2)

ON DELETE:
- RESTRICT (default): rechaza borrar si hay filas dependientes.
- CASCADE: borra en cascada (peligroso).
- SET NULL: pone NULL en la FK.

FK permite NULL por defecto (relación opcional). Agregar NOT NULL la hace obligatoria.

Orden de creación: las tablas referenciadas deben crearse primero.
Orden de eliminación: inverso (DROP primero las que referencian).

DROP TABLE IF EXISTS evita errores si la tabla no existe.

PostgreSQL NO crea índices automáticos en columnas FK (a diferencia de MySQL).

---

## 4. PK compuestas y FK compuestas

PK compuesta: cuando ninguna columna sola identifica la fila. Se declara al final:

    PRIMARY KEY (columna1, columna2)

Cada columna puede repetirse individualmente; la combinación debe ser única.
Las columnas de PK compuesta son automáticamente NOT NULL.

FK a PK compuesta: debe incluir todas las columnas, declarada al final:

    FOREIGN KEY (col_local1, col_local2) REFERENCES tabla(col_pk1, col_pk2)

Los tipos deben coincidir par a par. Los nombres no necesitan ser iguales.

Una columna puede ser parte de la PK compuesta y ser FK al mismo tiempo.

---

## 5. CHECK avanzados con patrones (regex)

Operador ~ evalúa expresiones regulares:

    CHECK (codigo ~ '^[0-9]{4}(00|10|20|30|40)$')

Bloques de regex:
- ^ y $: inicio y fin del texto. Siempre usarlos en CHECK.
- [0-9]: un dígito. [a-zA-Z]: una letra.
- {n}: exactamente n veces. {min,max}: entre min y max veces.
- (a|b|c): alternativas.

~ es case sensitive. ~* es case insensitive.

SIMILAR TO existe pero es menos usado. Quedarse con ~.

Cuantificador de rango usa coma, no guión: {6,15} no {6-15}.

---

## 6. Índices

Estructura de datos separada que acelera búsquedas. Tipo default: B-tree.

    CREATE INDEX idx_nombre ON tabla(columna);

Índices automáticos: PRIMARY KEY y UNIQUE ya tienen índice.
Índices compuestos: CREATE INDEX idx ON tabla(col1, col2). El orden importa:
un índice (A, B) sirve para filtrar por A solo o por A+B, pero NO por B solo.

Costo: ocupan espacio y hacen INSERT/UPDATE/DELETE más lentos.

Cuándo crear: columnas frecuentes en WHERE/JOIN/ORDER BY que no son PK ni UNIQUE.
Cuándo NO crear: columnas con pocos valores distintos (baja selectividad, ej: estado ACTIVO/INACTIVO), tablas pequeñas.

Convención de nombres: idx_tabla_columna.

---

## 7. Vistas

Consulta guardada con nombre. No almacena datos; se ejecuta en cada consulta.

    CREATE VIEW nombre AS
    SELECT ...;

CREATE OR REPLACE VIEW: crea o reemplaza sin hacer DROP.

Siempre reflejan datos actualizados (se ejecutan en tiempo real).
Si se modifica la estructura de una tabla base (renombrar/eliminar columna), la vista se rompe.
No son actualizables por defecto si tienen JOINs, GROUP BY o funciones agregadas.

JOINs en vistas:
- INNER JOIN: solo filas con coincidencia en ambas tablas.
- LEFT JOIN: todas las filas de la izquierda, NULL si no hay coincidencia.
- ON con FK compuesta: ON t1.col1 = t2.col1 AND t1.col2 = t2.col2.

Funciones de agregación: SUM, COUNT, AVG, MIN, MAX.
GROUP BY: toda columna en SELECT que no esté en función agregada debe estar en GROUP BY.

CASE dentro de vistas: transforma valores condicionalmente:

    SUM(CASE WHEN tipo = 'COBRO' THEN -valor WHEN tipo = 'PAGO' THEN valor END)
