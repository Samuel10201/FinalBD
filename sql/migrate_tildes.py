"""
Migración: agregar tildes y virgulillas a los datos existentes en la BD.
Ejecutar una sola vez: python sql/migrate_tildes.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.db import get_connection, close_connection

PROGRAMA_RENAMES = {
    'Ingenieria de Sistemas':  'Ingeniería de Sistemas',
    'Ingenieria Civil':        'Ingeniería Civil',
    'Ingenieria Electronica':  'Ingeniería Electrónica',
    'Ingenieria Industrial':   'Ingeniería Industrial',
    'Ingenieria Mecanica':     'Ingeniería Mecánica',
    'Psicologia':              'Psicología',
    'Administracion de Empresas': 'Administración de Empresas',
    'Contaduria Publica':      'Contaduría Pública',
    'Economia':                'Economía',
    'Comunicacion Social':     'Comunicación Social',
    'Matematicas':             'Matemáticas',
}

FACULTAD_RENAMES = {
    'Ingenieria':        'Ingeniería',
    'Ciencias Economicas': 'Ciencias Económicas',
    'Ciencias Juridicas':  'Ciencias Jurídicas',
    'Ciencias Basicas':    'Ciencias Básicas',
}

ASIGNATURA_REPLACEMENTS = [
    ('Introduccion', 'Introducción'),
    ('Programacion', 'Programación'),
    ('Logica',       'Lógica'),
    ('Ingenieria',   'Ingeniería'),
    ('Informatica',  'Informática'),
    ('Estatica',     'Estática'),
    ('Tecnico',      'Técnico'),
    ('Mecanica',     'Mecánica'),
    ('Hidraulica',   'Hidráulica'),
    ('Vias',         'Vías'),
    ('Construccion', 'Construcción'),
    ('Diseno',       'Diseño'),
    ('Electricos',   'Eléctricos'),
    ('Electronica',  'Electrónica'),
    ('Basica',       'Básica'),
    ('Senales',      'Señales'),
    ('Automatico',   'Automático'),
    ('Robotica',     'Robótica'),
    ('Investigacion','Investigación'),
    ('Gestion',      'Gestión'),
    ('Logistica',    'Logística'),
    ('Ergonomia',    'Ergonomía'),
    ('Simulacion',   'Simulación'),
    ('Termodinamica','Termodinámica'),
    ('Dinamica',     'Dinámica'),
    ('Maquinas',     'Máquinas'),
    ('Termicos',     'Térmicos'),
    ('Energia',      'Energía'),
    ('Anatomia',     'Anatomía'),
    ('Biologia',     'Biología'),
    ('Fisiologia',   'Fisiología'),
    ('Bioquimica',   'Bioquímica'),
    ('Medica',       'Médica'),
    ('Patologia',    'Patología'),
    ('Farmacologia', 'Farmacología'),
    ('Semiologia',   'Semiología'),
    ('Microbiologia','Microbiología'),
    ('Publica',      'Pública'),
    ('Psicologia',   'Psicología'),
    ('Clinica',      'Clínica'),
    ('Psicometria',  'Psicometría'),
    ('Intervencion', 'Intervención'),
    ('Psicologica',  'Psicológica'),
    ('Neuropsicologia','Neuropsicología'),
    ('Administracion','Administración'),
    ('Innovacion',   'Innovación'),
    ('Matematica',   'Matemática'),
    ('Auditoria',    'Auditoría'),
    ('Microeconomia','Microeconomía'),
    ('Macroeconomia','Macroeconomía'),
    ('Econometria',  'Econometría'),
    ('Economia',     'Economía'),
    ('Politica',     'Política'),
    ('Economico',    'Económico'),
    ('Comunicacion', 'Comunicación'),
    ('Redaccion',    'Redacción'),
    ('Periodistica', 'Periodística'),
    ('Semiotica',    'Semiótica'),
    ('Opinion',      'Opinión'),
    ('Produccion',   'Producción'),
    ('Fotografia',   'Fotografía'),
    ('Calculo',      'Cálculo'),
    ('Algebra',      'Álgebra'),
    ('Analisis',     'Análisis'),
    ('Topologia',    'Topología'),
    ('Numerico',     'Numérico'),
    ('Teoria',       'Teoría'),
    ('Numeros',      'Números'),
    ('Basico',       'Básico'),
    ('Tecnologia',   'Tecnología'),
    ('Restauracion', 'Restauración'),
    ('Parametrico',  'Paramétrico'),
    ('Contaduria',   'Contaduría'),
]

APELLIDO_REPLACEMENTS = [
    ('Gonzalez', 'González'),
    ('Rodriguez','Rodríguez'),
    ('Gomez',    'Gómez'),
    ('Lopez',    'López'),
    ('Martinez', 'Martínez'),
    ('Garcia',   'García'),
    ('Hernandez','Hernández'),
    ('Diaz',     'Díaz'),
    ('Alvarez',  'Álvarez'),
    ('Ramirez',  'Ramírez'),
    ('Sanchez',  'Sánchez'),
    ('Perez',    'Pérez'),
    ('Jimenez',  'Jiménez'),
    ('Gutierrez','Gutiérrez'),
    ('Cardenas', 'Cárdenas'),
    ('Nunez',    'Núñez'),
    ('Mejia',    'Mejía'),
]

SERVICIO_REPLACEMENTS = [
    ('matricula', 'matrícula'),
    ('creditos',  'créditos'),
    ('Credito',   'Crédito'),
]

def run():
    conn = get_connection()
    try:
        cur = conn.cursor()

        # 1) Renombrar programa_academico (PK) — con FKs en cascada
        for old, new in PROGRAMA_RENAMES.items():
            cur.execute("SELECT 1 FROM programa_academico WHERE nombre = %s", (old,))
            if not cur.fetchone():
                print(f"  [skip] programa '{old}' no existe")
                continue
            print(f"  programa: '{old}' -> '{new}'")
            cur.execute("INSERT INTO programa_academico (nombre, facultad, modo, duracion) "
                        "SELECT %s, facultad, modo, duracion FROM programa_academico WHERE nombre = %s",
                        (new, old))
            cur.execute("UPDATE matricula SET prog_acad = %s WHERE prog_acad = %s", (new, old))
            cur.execute("UPDATE costo SET prog_academico = %s WHERE prog_academico = %s", (new, old))
            cur.execute("UPDATE plan_estudio SET nombre_programa = %s WHERE nombre_programa = %s", (new, old))
            cur.execute("UPDATE cuenta_corriente SET descripcion_mov = REPLACE(descripcion_mov, %s, %s) "
                        "WHERE descripcion_mov LIKE %s", (old, new, f'%{old}%'))
            cur.execute("DELETE FROM programa_academico WHERE nombre = %s", (old,))

        # 2) Actualizar facultades
        for old, new in FACULTAD_RENAMES.items():
            cur.execute("UPDATE programa_academico SET facultad = %s WHERE facultad = %s", (new, old))

        # 3) Asignaturas (nombre y descripcion)
        for old, new in ASIGNATURA_REPLACEMENTS:
            cur.execute("UPDATE asignatura SET nombre = REPLACE(nombre, %s, %s) WHERE nombre LIKE %s",
                        (old, new, f'%{old}%'))
            cur.execute("UPDATE asignatura SET descripcion = REPLACE(descripcion, %s, %s) WHERE descripcion LIKE %s",
                        (old, new, f'%{old}%'))

        # 4) Servicios (descripcion)
        for old, new in SERVICIO_REPLACEMENTS:
            cur.execute("UPDATE servicio SET descripcion = REPLACE(descripcion, %s, %s) WHERE descripcion LIKE %s",
                        (old, new, f'%{old}%'))

        # 5) Usuarios (nombre — apellidos)
        for old, new in APELLIDO_REPLACEMENTS:
            cur.execute("UPDATE usuario SET nombre = REPLACE(nombre, %s, %s) WHERE nombre LIKE %s",
                        (old, new, f'%{old}%'))

        # 6) Estudiantes (nombre — apellidos)
        for old, new in APELLIDO_REPLACEMENTS:
            cur.execute("UPDATE estudiante SET nombre = REPLACE(nombre, %s, %s) WHERE nombre LIKE %s",
                        (old, new, f'%{old}%'))

        conn.commit()
        print("\nMigración completada exitosamente.")

    except Exception as e:
        conn.rollback()
        print(f"\nError — rollback realizado: {e}")
        raise
    finally:
        close_connection(conn)

if __name__ == '__main__':
    print("=== Migración: tildes en datos ===\n")
    run()
