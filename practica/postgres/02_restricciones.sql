CREATE TABLE editorial(
    codigo  CHAR(5) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE libro(
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(30) NOT NULL,
    numero_pagina INTEGER CHECK(numero_pagina > 0),
    precio  NUMERIC(8,2) NOT NULL CHECK(precio > 0),
    fecha_publicacion DATE NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT('DISPONIBLE') CONSTRAINT estado_libro_valido CHECK(estado IN ('DISPONIBLE', 'AGOTADO'))
);

CREATE TABLE cliente(
    id CHAR(8) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
    estado VARCHAR(10) NOT NULL CONSTRAINT estado_cliente_valido CHECK (estado IN('INACTIVO', 'ACTIVO')) DEFAULT 'ACTIVO'
);
