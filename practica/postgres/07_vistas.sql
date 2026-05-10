CREATE TABLE programa(
    nombre VARCHAR(30) PRIMARY KEY,
    facultad VARCHAR(30) NOT NULL
);

CREATE TABLE periodo(
    codigo CHAR(6) PRIMARY KEY,
    descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE asignatura(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    creditos INT NOT NULL CHECK (creditos >= 0)
);

CREATE TABLE plan_estudio(
    nombre_programa VARCHAR(30) REFERENCES programa(nombre),
    cod_asignatura VARCHAR(10) REFERENCES asignatura(codigo),
    semestre INT NOT NULL CHECK(semestre > 0),
    PRIMARY KEY (nombre_programa, cod_asignatura) 
);

CREATE TABLE costo(
    nombre_programa VARCHAR(30) REFERENCES programa(nombre),
    cod_periodo CHAR(6) REFERENCES periodo(codigo),
    costo_credito NUMERIC(10,2) NOT NULL CHECK(costo_credito > 0),
    costo_global NUMERIC(10,2) NOT NULL CHECK(costo_global > 0),
    PRIMARY KEY(nombre_programa, cod_periodo)
);

CREATE TABLE usuario(
    tipo_id CHAR(2),
    id VARCHAR(15),
    nombre VARCHAR(30) NOT NULL,
    correo VARCHAR(50) NOT NULL UNIQUE,
    rol VARCHAR(15) NOT NULL CONSTRAINT rol_usuario_valido CHECK(rol IN ('ADMINISTRADOR', 'SUPERVISOR', 'ASISTENTE', 'ESTUDIANTE')),
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO' CONSTRAINT estado_usuario_valido CHECK(estado IN ('ACTIVO', 'INACTIVO')),
    PRIMARY KEY(tipo_id, id)
);

CREATE TABLE estudiante(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL,
    estado VARCHAR(10) NOT NULL DEFAULT 'ACTIVO' CONSTRAINT estado_estudiante_valido CHECK (estado IN ('ACTIVO', 'INACTIVO')),
    tipo_id CHAR(2) NOT NULL,
    id VARCHAR(15) NOT NULL,
    FOREIGN KEY(tipo_id, id) REFERENCES usuario(tipo_id, id)
);

CREATE VIEW vista_estudiante_completo AS (
                                            SELECT e.tipo_id, e.id, e.codigo, e.nombre, e.estado, u.correo, u.rol
                                            FROM estudiante e
                                            JOIN usuario u ON e.id = u.id AND e.tipo_id = u.tipo_id  
);
