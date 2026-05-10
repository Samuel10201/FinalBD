CREATE TABLE editorial(
    codigo CHAR(6) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL
);

CREATE TABLE libro(
    id  SERIAL PRIMARY KEY,
    titulo VARCHAR(40) NOT NULL,
    precio NUMERIC(8,2) NOT NULL CHECK(precio > 0),
    cod_editorial CHAR(6) NOT NULL REFERENCES editorial(codigo)
);

CREATE TABLE cliente(
    documento CHAR(8) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE venta(
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    doc_cliente CHAR(8) NOT NULL REFERENCES cliente(documento)
);

CREATE TABLE detalle_venta(
    id SERIAL PRIMARY KEY,
    cantidad INT NOT NULL CHECK(cantidad > 0),
    precio_unitario NUMERIC(8,2) NOT NULL CHECK(precio_unitario > 0),
    id_venta INT NOT NULL REFERENCES venta(id),
    id_libro INT NOT NULL REFERENCES libro(id)
);
