CREATE TABLE periodo(
    codigo CHAR(6) PRIMARY KEY CHECK(codigo ~ '^[0-9]{4}(00|10|20|30|40)$'),
    descripcion VARCHAR(60) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO' CONSTRAINT estado_periodo_valido CHECK(estado IN ('ACTIVO', 'INACTIVO'))
);

CREATE TABLE telefono(
    id SERIAL PRIMARY KEY,
    numero VARCHAR(10) NOT NULL CHECK(numero ~ '^3[0-9]{9}$')
);

CREATE TABLE documento(
    id SERIAL PRIMARY KEY,
    tipo CHAR(2) NOT NULL CHECK(tipo IN ('CC', 'TI', 'CE', 'PP')),
    numero VARCHAR(15) NOT NULL CHECK (numero ~ '^[0-9]{6,15}$')
);
