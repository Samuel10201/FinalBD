# Tópicos Avanzados en SQL (SQL Server)

> **Referencia interna** — Usar estos comandos y patrones al diseñar bases de datos, escribir consultas o ayudar al usuario con SQL Server.

---

## Índice

1. [Cláusula SELECT](#1-cláusula-select)
   - TOP
   - CASE
   - OVER (funciones de ventana)
   - WINDOW
2. [Cláusula FROM](#2-cláusula-from)
   - CROSS APPLY vs INNER JOIN
   - OUTER APPLY vs OUTER JOIN
   - PIVOT & UNPIVOT
3. [Cláusula WHERE](#3-cláusula-where)
   - BETWEEN
   - EXISTS
   - IN
   - LIKE
   - LIKE...ESCAPE
   - CONTAINS
   - FREETEXT
   - IS [NOT] DISTINCT FROM
   - IS [NOT] NULL
4. [Otros Tópicos](#4-otros-tópicos)
   - ROLLUP
   - CUBE

---

## 1. Cláusula SELECT

### 1.1 TOP

**Qué hace:** Limita las filas devueltas en un conjunto de resultados a un número o porcentaje específico de filas.

**Sintaxis:**

```sql
SELECT TOP (expression) [PERCENT] [WITH TIES]
    column_list
FROM table_name
[ORDER BY column_name];
```

**Parámetros:**

| Parámetro    | Descripción |
|-------------|-------------|
| `expression` | Expresión numérica que indica el número de filas a devolver. |
| `PERCENT`    | Devuelve el primer porcentaje de filas del conjunto de resultados. |
| `WITH TIES`  | Incluye filas adicionales que empatan en el último valor del conjunto de resultados limitado. |

**Comportamiento importante:**
- Cuando se usa **con ORDER BY**, el resultado se limita al primer N número de filas **ordenadas**.
- **Sin ORDER BY**, TOP devuelve el primer N número de filas en un **orden indefinido** (no determinista).

**Ejemplo:**

```sql
-- Obtener los 10 productos más caros
SELECT TOP (10) ProductName, UnitPrice
FROM Products
ORDER BY UnitPrice DESC;

-- Obtener el 5% de los empleados con mayor salario
SELECT TOP (5) PERCENT EmployeeName, Salary
FROM Employees
ORDER BY Salary DESC;

-- Incluir empates: si el 10.° y 11.° tienen el mismo precio, ambos aparecen
SELECT TOP (10) WITH TIES ProductName, UnitPrice
FROM Products
ORDER BY UnitPrice DESC;
```

---

### 1.2 CASE

**Qué hace:** Evalúa una lista de condiciones y devuelve una de varias expresiones de resultado posibles. Funciona como un `if-else` dentro de una consulta SQL.

**Dos formatos:**

#### CASE Simple

Compara una expresión de entrada con un conjunto de valores simples.

```sql
CASE input_expression
    WHEN when_expression THEN result_expression
    [WHEN when_expression THEN result_expression ...]
    [ELSE else_result_expression]
END
```

#### CASE Buscado (Searched)

Evalúa un conjunto de expresiones booleanas independientes.

```sql
CASE
    WHEN Boolean_expression THEN result_expression
    [WHEN Boolean_expression THEN result_expression ...]
    [ELSE else_result_expression]
END
```

**Parámetros:**

| Parámetro                   | Descripción |
|----------------------------|-------------|
| `input_expression`          | Expresión evaluada en el formato CASE simple. |
| `WHEN when_expression`      | Condición con la que se compara `input_expression`. |
| `THEN result_expression`    | Expresión devuelta cuando la condición se cumple (TRUE). |
| `ELSE else_result_expression` | Expresión devuelta cuando **ninguna** comparación es verdadera. |

**Ejemplo:**

```sql
-- CASE simple
SELECT ProductName,
    CASE CategoryID
        WHEN 1 THEN 'Bebidas'
        WHEN 2 THEN 'Condimentos'
        WHEN 3 THEN 'Lácteos'
        ELSE 'Otros'
    END AS NombreCategoria
FROM Products;

-- CASE buscado
SELECT EmployeeName, Salary,
    CASE
        WHEN Salary >= 80000 THEN 'Alto'
        WHEN Salary >= 50000 THEN 'Medio'
        ELSE 'Bajo'
    END AS NivelSalario
FROM Employees;
```

---

### 1.3 OVER (Funciones de Ventana)

**Qué hace:** Determina la creación de particiones y el orden de un conjunto de filas **antes** de aplicar la función de ventana asociada. Permite realizar cálculos agregados sin colapsar las filas (a diferencia de GROUP BY).

**Sintaxis:**

```sql
function_name(...) OVER (
    [PARTITION BY value_expression, ... [n]]
    [ORDER BY order_by_expression [ASC | DESC], ... [n]]
    [ROWS | RANGE <window_frame_extent>]
)
```

**Sub-cláusulas:**

| Sub-cláusula     | Descripción |
|-----------------|-------------|
| `PARTITION BY`   | Divide el conjunto de resultados en particiones. La función se aplica independientemente a cada partición. |
| `ORDER BY`       | Define el orden lógico de las filas dentro de cada partición. |
| `ROWS` o `RANGE` | Limita las filas dentro de la partición especificando puntos inicial y final. |

**Ejemplo:**

```sql
-- Salario acumulado por departamento
SELECT
    EmployeeName,
    Department,
    Salary,
    SUM(Salary) OVER (PARTITION BY Department ORDER BY Salary) AS SalarioAcumulado,
    ROW_NUMBER() OVER (PARTITION BY Department ORDER BY Salary DESC) AS Ranking
FROM Employees;

-- Promedio móvil de ventas (últimas 3 filas)
SELECT
    OrderDate,
    TotalAmount,
    AVG(TotalAmount) OVER (
        ORDER BY OrderDate
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS PromedioMovil
FROM Orders;
```

**Funciones comunes con OVER:**
- Agregadas: `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()`
- De clasificación: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `NTILE()`
- De valor: `LAG()`, `LEAD()`, `FIRST_VALUE()`, `LAST_VALUE()`

---

### 1.4 WINDOW

**Qué hace:** Permite **nombrar** una definición de ventana para reutilizarla con múltiples funciones OVER, evitando repetir la misma especificación.

**Requisito:** Nivel de compatibilidad 160 o superior en SQL Server.

```sql
ALTER DATABASE DatabaseName
SET COMPATIBILITY_LEVEL = 160;
```

**Sintaxis:**

```sql
SELECT
    column_list,
    function1(...) OVER window_name,
    function2(...) OVER window_name
FROM table_name
WINDOW window_name AS (
    [reference_window_name]
    [PARTITION BY value_expression, ... [n]]
    [ORDER BY order_by_expression [COLLATE collation_name] [ASC | DESC], ... [n]]
    [ROWS | RANGE <window_frame_extent>]
)
[ORDER BY ...];
```

**Reglas de ubicación:**
- Se coloca **una sola vez** al final del SELECT, **después del FROM** y **antes del ORDER BY** final.

**Ejemplo:**

```sql
SELECT
    EmployeeName,
    Department,
    Salary,
    SUM(Salary)    OVER w AS TotalDept,
    AVG(Salary)    OVER w AS PromedioDept,
    ROW_NUMBER()   OVER w AS FilaNum
FROM Employees
WINDOW w AS (PARTITION BY Department ORDER BY Salary DESC)
ORDER BY Department, Salary DESC;
```

---

## 2. Cláusula FROM

### 2.1 APPLY (CROSS APPLY vs INNER JOIN)

**Qué hace APPLY:** Se utiliza para combinar una tabla principal con una tabla derivada o función de tabla. Permite aplicar una operación **fila por fila**, algo que no se puede lograr con un JOIN tradicional.

#### CROSS APPLY

Es una **unión lateral**: evalúa, para cada fila de la fuente izquierda, una expresión tabular dependiente en la derecha (puede referenciar columnas de la izquierda). Solo conserva las filas donde esa expresión produce resultados. Su semántica de filtrado equivale a un INNER JOIN.

#### Diferencia con INNER JOIN

En un `INNER JOIN`, las dos fuentes existen de manera **independiente** y luego se relacionan con una condición `ON`. La tabla o subconsulta de la derecha **no puede** necesitar valores de la izquierda para definirse. Con `CROSS APPLY`, sí puede.

**Ejemplo:**

```sql
-- CROSS APPLY: obtener las últimas 3 órdenes de cada cliente
SELECT c.CustomerName, o.OrderID, o.OrderDate
FROM Customers c
CROSS APPLY (
    SELECT TOP (3) OrderID, OrderDate
    FROM Orders
    WHERE Orders.CustomerID = c.CustomerID  -- referencia a la tabla izquierda
    ORDER BY OrderDate DESC
) o;

-- Equivalente con INNER JOIN (no es posible referencia lateral):
-- Habría que usar subconsultas correlacionadas o CTEs más complejas.
```

---

### 2.2 OUTER APPLY vs OUTER JOIN

#### OUTER APPLY

Se usa cuando la tabla derecha **depende** de la fila actual de la izquierda. Permite ejecutar una subconsulta o función para cada fila. Si la subconsulta no devuelve resultados, las columnas aparecen como `NULL` (comportamiento similar a LEFT JOIN).

#### OUTER JOIN

Combina dos tablas completas según una condición fija (`ON` o `USING`). Se ejecuta de forma **estática**, sin depender de los valores de cada fila. Si no hay coincidencia en la tabla derecha, las columnas de esa tabla se completan con `NULL`.

**Ejemplo:**

```sql
-- OUTER APPLY: último pedido de cada cliente (incluye clientes sin pedidos)
SELECT c.CustomerName, o.OrderID, o.OrderDate
FROM Customers c
OUTER APPLY (
    SELECT TOP (1) OrderID, OrderDate
    FROM Orders
    WHERE Orders.CustomerID = c.CustomerID
    ORDER BY OrderDate DESC
) o;

-- LEFT OUTER JOIN equivalente (sin referencia lateral)
SELECT c.CustomerName, o.OrderID, o.OrderDate
FROM Customers c
LEFT JOIN Orders o ON o.CustomerID = c.CustomerID;
```

**Cuándo usar APPLY en vez de JOIN:**
- Cuando necesitas referenciar columnas de la tabla izquierda en la subconsulta derecha.
- Cuando usas funciones con valor de tabla (TVF).
- Cuando necesitas obtener las "N primeras" filas por cada fila de la tabla principal.

---

### 2.3 PIVOT & UNPIVOT

#### PIVOT

**Qué hace:** Gira una expresión con valores de tabla al convertir los valores únicos de una columna en **varias columnas** en la salida. Transforma filas en columnas.

**Sintaxis:**

```sql
SELECT column_list
FROM source_table
PIVOT (
    aggregation_function(column_being_aggregated)
    FOR column_that_becomes_headers
    IN ([first_value], [second_value], ... [last_value])
) AS alias
[ORDER BY ...];
```

**Ejemplo:**

```sql
-- Convertir filas de ventas mensuales en columnas
SELECT ProductName, [Enero], [Febrero], [Marzo]
FROM (
    SELECT ProductName, MonthName, SalesAmount
    FROM MonthlySales
) AS SourceTable
PIVOT (
    SUM(SalesAmount)
    FOR MonthName IN ([Enero], [Febrero], [Marzo])
) AS PivotTable;
```

#### UNPIVOT

**Qué hace:** Operación **opuesta** a PIVOT. Convierte columnas en filas de valores.

**Sintaxis:**

```sql
SELECT column_list
FROM source_table
UNPIVOT (
    new_values_column
    FOR new_names_column
    IN ([first_column], [second_column], ... [last_column])
) AS alias
[ORDER BY ...];
```

**Ejemplo:**

```sql
-- Convertir columnas de meses de vuelta a filas
SELECT ProductName, MonthName, SalesAmount
FROM PivotedSales
UNPIVOT (
    SalesAmount
    FOR MonthName IN ([Enero], [Febrero], [Marzo])
) AS UnpivotTable;
```

---

## 3. Cláusula WHERE

### 3.1 BETWEEN

**Qué hace:** Filtra datos seleccionando filas donde un valor se encuentre dentro de un **rango inclusivo** (incluye tanto el valor inicial como el final).

**Sintaxis:**

```sql
test_expression [NOT] BETWEEN begin_expression AND end_expression
```

**Comportamiento:**
- `BETWEEN` → TRUE si el valor es **>= begin** y **<= end**.
- `NOT BETWEEN` → TRUE si el valor es **< begin** o **> end**.

**Ejemplo:**

```sql
-- Productos con precio entre 10 y 50
SELECT ProductName, UnitPrice
FROM Products
WHERE UnitPrice BETWEEN 10 AND 50;

-- Pedidos fuera del rango de fechas
SELECT OrderID, OrderDate
FROM Orders
WHERE OrderDate NOT BETWEEN '2025-01-01' AND '2025-06-30';
```

---

### 3.2 EXISTS

**Qué hace:** Operador lógico que determina si una **subconsulta devuelve filas**. Comprueba la existencia de filas que cumplan una condición.

**Sintaxis:**

```sql
WHERE EXISTS (subquery)
WHERE NOT EXISTS (subquery)
```

**Ejemplo:**

```sql
-- Clientes que tienen al menos un pedido
SELECT CustomerName
FROM Customers c
WHERE EXISTS (
    SELECT 1
    FROM Orders o
    WHERE o.CustomerID = c.CustomerID
);

-- Productos que nunca se han vendido
SELECT ProductName
FROM Products p
WHERE NOT EXISTS (
    SELECT 1
    FROM OrderDetails od
    WHERE od.ProductID = p.ProductID
);
```

**Nota:** `EXISTS` es generalmente más eficiente que `IN` con subconsultas grandes, porque deja de buscar al encontrar la primera coincidencia.

---

### 3.3 IN

**Qué hace:** Determina si un valor especificado coincide con **algún valor** de una subconsulta o una lista.

**Sintaxis:**

```sql
test_expression [NOT] IN (subquery | expression [, ...n])
```

**Ejemplo:**

```sql
-- Filtrar por lista de valores
SELECT ProductName, CategoryID
FROM Products
WHERE CategoryID IN (1, 3, 5);

-- Filtrar con subconsulta
SELECT CustomerName
FROM Customers
WHERE CustomerID IN (
    SELECT CustomerID
    FROM Orders
    WHERE OrderDate >= '2025-01-01'
);

-- Excluir valores específicos
SELECT EmployeeName
FROM Employees
WHERE DepartmentID NOT IN (10, 20);
```

---

### 3.4 LIKE

**Qué hace:** Determina si una cadena de caracteres coincide con un **patrón** especificado.

**Comodines:**

| Comodín   | Descripción |
|-----------|-------------|
| `%`       | Cualquier secuencia de cero o más caracteres. |
| `_`       | Exactamente un carácter. |
| `[...]`   | Cualquier carácter dentro del conjunto o rango especificado. |
| `[^...]`  | Cualquier carácter que **no** esté en el conjunto o rango. |

**Sintaxis:**

```sql
match_expression [NOT] LIKE pattern
```

**Ejemplo:**

```sql
-- Nombres que empiezan con 'A'
SELECT CustomerName FROM Customers
WHERE CustomerName LIKE 'A%';

-- Nombres con exactamente 5 caracteres
SELECT CustomerName FROM Customers
WHERE CustomerName LIKE '_____';

-- Nombres que empiezan con A, B o C
SELECT CustomerName FROM Customers
WHERE CustomerName LIKE '[ABC]%';

-- Nombres que NO empiezan con vocal
SELECT CustomerName FROM Customers
WHERE CustomerName LIKE '[^AEIOU]%';
```

---

### 3.5 LIKE...ESCAPE

**Qué hace:** Indica que el siguiente carácter comodín (`%` o `_`) debe tratarse como un **valor literal** en lugar de como un comodín.

**Sintaxis:**

```sql
match_expression [NOT] LIKE pattern ESCAPE escape_character
```

**Ejemplo:**

```sql
-- Buscar productos cuyo nombre contenga literalmente "10%"
SELECT ProductName
FROM Products
WHERE ProductName LIKE '%10!%%' ESCAPE '!';

-- Buscar registros que contengan un guion bajo literal
SELECT ColumnName
FROM SomeTable
WHERE ColumnName LIKE '%!_%' ESCAPE '!';
```

---

### 3.6 CONTAINS

**Qué hace:** Busca coincidencias **precisas o aproximadas** de palabras o frases, palabras que se encuentran a cierta distancia de otra, o coincidencias ponderadas. **Requiere Full-Text Index** configurado en la tabla.

**Sintaxis:**

```sql
CONTAINS (
    { column_name | (column_list) | * | PROPERTY (column_name, 'property_name') },
    '<contains_search_condition>'
    [, LANGUAGE language_term]
)
```

**Tipos de búsqueda soportados:**
- `<simple_term>` — palabra o frase exacta.
- `<prefix_term>` — palabras que comienzan con un prefijo.
- `<generation_term>` — formas conjugadas/derivadas de una palabra.
- `<generic_proximity_term>` — palabras cercanas entre sí.
- `<weighted_term>` — coincidencias con ponderación.

**Ejemplo:**

```sql
-- Buscar documentos que contengan la palabra exacta "rendimiento"
SELECT Title, Body
FROM Articles
WHERE CONTAINS(Body, 'rendimiento');

-- Buscar frase exacta
SELECT Title FROM Articles
WHERE CONTAINS(Body, '"base de datos"');

-- Buscar con prefijo
SELECT Title FROM Articles
WHERE CONTAINS(Body, '"rend*"');

-- Buscar palabras cercanas
SELECT Title FROM Articles
WHERE CONTAINS(Body, 'NEAR((rendimiento, optimización), 5)');
```

---

### 3.7 FREETEXT

**Qué hace:** Busca valores que coincidan con el **significado** y no solo con la redacción exacta de las palabras. Usa análisis lingüístico internamente (sinónimos, formas derivadas). **Requiere Full-Text Index.**

**Sintaxis:**

```sql
FREETEXT (
    { column_name | (column_list) | * },
    'freetext_string'
    [, LANGUAGE language_term]
)
```

**Diferencia con CONTAINS:** FREETEXT es más flexible y menos preciso. Descompone la frase en palabras individuales, busca sinónimos y formas conjugadas. CONTAINS busca coincidencias exactas o con patrones explícitos.

**Ejemplo:**

```sql
-- Busca filas "parecidas" a la frase (incluye sinónimos y derivaciones)
SELECT Title, Body
FROM Articles
WHERE FREETEXT(Body, 'herramientas de jardín');

-- Buscará también: "herramienta", "jardines", "jardinería", etc.
```

---

### 3.8 IS [NOT] DISTINCT FROM

**Qué hace:** Compara la igualdad de dos expresiones y **garantiza un resultado TRUE o FALSE**, incluso si uno o ambos operandos son `NULL`. A diferencia de `=`, no produce `UNKNOWN` cuando hay NULLs.

**Sintaxis:**

```sql
expression IS [NOT] DISTINCT FROM expression
```

**Se usa en:** Condiciones de búsqueda de las cláusulas `WHERE` y `HAVING`.

**Tabla de verdad (comparación con `=`):**

| A     | B     | A = B     | A IS NOT DISTINCT FROM B |
|-------|-------|-----------|--------------------------|
| 1     | 1     | TRUE      | TRUE                     |
| 1     | 2     | FALSE     | FALSE                    |
| NULL  | NULL  | UNKNOWN   | **TRUE**                 |
| 1     | NULL  | UNKNOWN   | **FALSE**                |

**Ejemplo:**

```sql
-- Encontrar filas donde ManagerID es igual (incluyendo ambos NULL)
SELECT e1.EmployeeName, e2.EmployeeName
FROM Employees e1
JOIN Employees e2 ON e1.ManagerID IS NOT DISTINCT FROM e2.ManagerID
WHERE e1.EmployeeID < e2.EmployeeID;

-- Equivalente clásico (más verboso):
-- WHERE (e1.ManagerID = e2.ManagerID OR (e1.ManagerID IS NULL AND e2.ManagerID IS NULL))
```

---

### 3.9 IS [NOT] NULL

**Qué hace:** Es la **única forma correcta** de verificar si un valor está (o no) ausente. `IS NULL` es verdadero solo cuando el valor no existe; `IS NOT NULL` es verdadero cuando sí tiene algún valor.

**Sintaxis:**

```sql
expression IS [NOT] NULL
```

**Importante:** Nunca usar `= NULL` o `!= NULL`, ya que cualquier comparación con NULL usando operadores estándar produce `UNKNOWN`, no TRUE ni FALSE.

**Ejemplo:**

```sql
-- Empleados sin gerente asignado
SELECT EmployeeName
FROM Employees
WHERE ManagerID IS NULL;

-- Productos que sí tienen descripción
SELECT ProductName
FROM Products
WHERE Description IS NOT NULL;

-- ¡INCORRECTO! Esto nunca devuelve filas:
-- SELECT * FROM Employees WHERE ManagerID = NULL;
```

---

## 4. Otros Tópicos

### 4.1 ROLLUP

**Qué hace:** Se utiliza junto con `GROUP BY` para generar **subtotales y totales acumulados** dentro de un conjunto de resultados. Crea niveles jerárquicos de agregación sin tener que escribir varias consultas con UNION.

**Qué calcula:**
1. Los totales por cada combinación de valores.
2. Los subtotales por cada nivel jerárquico (de derecha a izquierda).
3. El total general (gran total).

**Sintaxis:**

```sql
SELECT column_list, aggregation_function(column)
FROM table_name
GROUP BY ROLLUP (column1, column2, ...);

-- O también:
GROUP BY column1, column2 WITH ROLLUP;
```

**Ejemplo:**

```sql
-- Ventas por región y ciudad, con subtotales por región y total general
SELECT
    Region,
    City,
    SUM(SalesAmount) AS TotalVentas
FROM Sales
GROUP BY ROLLUP (Region, City);

-- Resultado genera filas para:
-- (Region, City)   → total por región+ciudad
-- (Region, NULL)   → subtotal por región
-- (NULL, NULL)     → gran total
```

---

### 4.2 CUBE

**Qué hace:** Produce **todos los subtotales posibles** de las columnas listadas (el conjunto potencia de los grupos), además del total general. A diferencia de ROLLUP, no hay jerarquía: devuelve cada combinación de agregación.

**Sintaxis:**

```sql
SELECT column_list, aggregation_function(column)
FROM table_name
GROUP BY CUBE (column1, column2, ...);
```

**Diferencia con ROLLUP:**
- **ROLLUP** genera subtotales jerárquicos (N+1 niveles para N columnas).
- **CUBE** genera **todas** las combinaciones posibles (2^N grupos para N columnas). Crece exponencialmente, usarlo con criterio.

**Ejemplo:**

```sql
-- Todas las combinaciones posibles de ventas por región y categoría
SELECT
    Region,
    Category,
    SUM(SalesAmount) AS TotalVentas
FROM Sales
GROUP BY CUBE (Region, Category);

-- Resultado genera filas para:
-- (Region, Category)  → total por región+categoría
-- (Region, NULL)      → subtotal por región
-- (NULL, Category)    → subtotal por categoría  ← ROLLUP no genera esto
-- (NULL, NULL)        → gran total
```

---

## Resumen Rápido de Uso

| Comando / Cláusula        | Cuándo usarlo |
|---------------------------|---------------|
| `TOP`                     | Limitar filas devueltas (top N o porcentaje). |
| `CASE`                    | Lógica condicional dentro de SELECT, WHERE, ORDER BY. |
| `OVER`                    | Funciones de ventana: agregados sin GROUP BY, rankings, acumulados. |
| `WINDOW`                  | Reutilizar definición de ventana en múltiples funciones. |
| `CROSS APPLY`             | Subconsulta lateral que depende de la fila actual (equivale a INNER JOIN lateral). |
| `OUTER APPLY`             | Igual que CROSS APPLY pero conserva filas sin coincidencia (equivale a LEFT JOIN lateral). |
| `PIVOT`                   | Transformar filas en columnas. |
| `UNPIVOT`                 | Transformar columnas en filas. |
| `BETWEEN`                 | Filtrar por rango inclusivo. |
| `EXISTS`                  | Verificar si una subconsulta devuelve filas. |
| `IN`                      | Verificar si un valor está en una lista o subconsulta. |
| `LIKE`                    | Búsqueda por patrones con comodines. |
| `LIKE...ESCAPE`           | Buscar comodines como caracteres literales. |
| `CONTAINS`                | Búsqueda full-text precisa (requiere índice). |
| `FREETEXT`                | Búsqueda full-text semántica/flexible (requiere índice). |
| `IS [NOT] DISTINCT FROM`  | Comparar igualdad manejando NULLs correctamente. |
| `IS [NOT] NULL`           | Verificar si un valor es NULL. |
| `ROLLUP`                  | Subtotales jerárquicos y total general. |
| `CUBE`                    | Todos los subtotales posibles (conjunto potencia). |

---

*Fuente: Presentación "Tópicos Avanzados en SQL" — María Isabel Gutiérrez.*
