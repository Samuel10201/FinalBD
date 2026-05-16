CREATE TABLE periodo(
    codigo CHAR(6) PRIMARY KEY CHECK(codigo ~ '^[0-9]{4}(00|10|20|30|40)$'),
    descripcion VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado VARCHAR(15) NOT NULL CHECK(estado IN ('ACTIVO', 'INACTIVO'))
);

CREATE TABLE programa_academico(
    nombre VARCHAR(30) PRIMARY KEY,
    facultad VARCHAR(40) NOT NULL,
    modo VARCHAR(10) NOT NULL CHECK (modo IN ('PRESENCIAL', 'REMOTO')),
    duracion INT NOT NULL CHECK(duracion BETWEEN 1 AND 12)
);

CREATE TABLE asignatura(
    codigo CHAR(6) PRIMARY KEY CHECK(codigo ~ '^[A-Z]{3}[0-9]{3}$'),
    nombre VARCHAR(30) NOT NULL,
    creditos INT NOT NULL CHECK(creditos BETWEEN 0 AND 10),
    descripcion VARCHAR(100) NOT NULL,
    tipo VARCHAR(11) NOT NULL CHECK(tipo IN ('OBLIGATORIA', 'ELECTIVA'))
);

CREATE TABLE servicio(
    codigo VARCHAR(4) PRIMARY KEY CHECK(codigo ~ '^[A-Z]{3,4}$'),
    grupo VARCHAR(5) NOT NULL CHECK(grupo IN('COBRO', 'PAGO')),
    estado VARCHAR(10) NOT NULL CHECK(estado IN('ACTIVO', 'INACTIVO')),
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE usuario(
    tipo_id CHAR(2) NOT NULL CHECK(tipo_id IN('CC', 'TI', 'CE', 'PP', 'RC', 'NI', 'PE')),
    id VARCHAR(15),
    nombre VARCHAR(50) NOT NULL,
    correo VARCHAR(50) NOT NULL UNIQUE CHECK(correo ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    contrasena VARCHAR(250) NOT NULL,
    rol VARCHAR(15) NOT NULL CHECK(rol IN ('ADMINISTRADOR', 'ESTUDIANTE', 'SUPERVISOR', 'ASISTENTE')),
    estado VARCHAR(10) NOT NULL CHECK(estado IN ('ACTIVO', 'INACTIVO')),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY(id)
);

CREATE TABLE estudiante(
    codigo VARCHAR(8) PRIMARY KEY CHECK(codigo ~ '^[0-9]{2,8}$'),
    nombre VARCHAR(50) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO' CHECK(estado IN ('ACTIVO', 'INACTIVO')),
    fecha_nacimiento DATE NOT NULL,
    direccion VARCHAR(60) NOT NULL,
    id VARCHAR(15) NOT NULL REFERENCES usuario(id)
);

CREATE TABLE matricula (
    id SERIAL PRIMARY KEY,
    modalidad VARCHAR(10) NOT NULL CHECK(modalidad IN ('GLOBAL', 'CREDITO')),
    semestre INT NOT NULL CHECK(semestre BETWEEN 1 AND 12),
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
    cod_estudiante VARCHAR(8) NOT NULL REFERENCES estudiante(codigo),
    cod_periodo CHAR(6) NOT NULL REFERENCES periodo(codigo),
    prog_acad VARCHAR(30) NOT NULL REFERENCES programa_academico(nombre),
    UNIQUE (cod_estudiante, cod_periodo, prog_acad)
);

CREATE TABLE pago(
    id SERIAL PRIMARY KEY,
    estado VARCHAR(10) NOT NULL CHECK(estado IN ('PENDIENTE', 'COMPLETADO', 'ANULADO')),
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    metodo VARCHAR(10) NOT NULL CHECK(metodo IN ('EN LINEA', 'CAJA')),
    monto NUMERIC(12,2) NOT NULL CHECK(monto > 0)
);

CREATE TABLE cuenta_corriente(
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT NOW(),
    descripcion_mov VARCHAR(100) NOT NULL,
    valor NUMERIC(12,2) NOT NULL CHECK(valor > 0),
    cod_estudiante VARCHAR(8) NOT NULL REFERENCES estudiante(codigo),
    id_usuario VARCHAR(15) NOT NULL REFERENCES usuario(id),
    codigo_servicio VARCHAR(4) NOT NULL REFERENCES servicio(codigo),
    codigo_periodo CHAR(6) NOT NULL REFERENCES periodo(codigo),
    id_pago INT REFERENCES pago(id)
);

CREATE TABLE costo(
    prog_academico VARCHAR(30) REFERENCES programa_academico(nombre),
    cod_periodo CHAR(6) REFERENCES periodo(codigo),
    costo_credito NUMERIC(12,2) NOT NULL CHECK(costo_credito > 0),
    costo_global NUMERIC(12,2) NOT NULL CHECK(costo_global > 0),
    PRIMARY KEY(prog_academico, cod_periodo)
);

CREATE TABLE plan_estudio(
    nombre_programa VARCHAR(30) REFERENCES programa_academico(nombre),
    cod_asignatura CHAR(6) REFERENCES asignatura(codigo),
    semestre INT NOT NULL CHECK(semestre BETWEEN 1 AND 12),
    PRIMARY KEY(nombre_programa, cod_asignatura)
);

-- Indices
CREATE INDEX idx_cuenta_cod_estudiante ON cuenta_corriente(cod_estudiante);
CREATE INDEX idx_matricula_cod_periodo ON matricula(cod_periodo);
CREATE INDEX idx_matricula_prog_acad ON matricula(prog_acad);
