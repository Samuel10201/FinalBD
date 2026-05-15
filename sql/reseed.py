"""
Borra todos los datos de la BD y re-ejecuta seed.sql.
Ejecutar: python sql/reseed.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.db import get_connection, close_connection

TABLES_IN_ORDER = [
    'cuenta_corriente',
    'pago',
    'matricula',
    'costo',
    'plan_estudio',
    'estudiante',
    'usuario',
    'asignatura',
    'programa_academico',
    'servicio',
    'periodo',
]

SERIAL_SEQUENCES = [
    ('matricula', 'id', 'matricula_id_seq'),
    ('pago', 'id', 'pago_id_seq'),
    ('cuenta_corriente', 'id', 'cuenta_corriente_id_seq'),
]

def run():
    seed_path = os.path.join(os.path.dirname(__file__), 'seed.sql')
    with open(seed_path, 'r', encoding='utf-8') as f:
        seed_sql = f.read()

    conn = get_connection()
    try:
        cur = conn.cursor()

        print("1) Borrando datos existentes...")
        for table in TABLES_IN_ORDER:
            cur.execute(f'DELETE FROM {table}')
            print(f"   {table}: {cur.rowcount} filas eliminadas")

        print("\n2) Ejecutando seed.sql...")
        cur.execute(seed_sql)
        print("   Seed ejecutado correctamente.")

        print("\n3) Reseteando secuencias...")
        for table, col, seq in SERIAL_SEQUENCES:
            cur.execute(f"SELECT COALESCE(MAX({col}), 0) + 1 FROM {table}")
            next_val = cur.fetchone()[list(cur.description[0])[0]] if hasattr(cur, 'description') else 1
            cur.execute(f"SELECT COALESCE(MAX({col}), 0) + 1 as nv FROM {table}")
            row = cur.fetchone()
            nv = row['nv']
            cur.execute(f"SELECT setval('{seq}', {nv}, false)")
            print(f"   {seq} -> {nv}")

        conn.commit()
        print("\nRe-seed completado exitosamente.")

    except Exception as e:
        conn.rollback()
        print(f"\nError — rollback: {e}")
        raise
    finally:
        close_connection(conn)

if __name__ == '__main__':
    print("=== Re-seed de base de datos ===\n")
    run()
