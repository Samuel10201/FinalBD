CREATE TABLE editorial(
    codigo  CHAR(5)  PRIMARY KEY,
    nombre  VARCHAR(40)
);

CREATE TABLE libro(
    id  SERIAL  PRIMARY KEY,
    titulo  VARCHAR(50),
    numero_pagina   INT,
    precio  NUMERIC(8,2),
    fecha_publicacion   DATE
);

CREATE TABLE cliente(
    id  CHAR(8) PRIMARY KEY,
    nombre  VARCHAR(30),
    email   VARCHAR(50),
    fecha_registro  TIMESTAMP
);
