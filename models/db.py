import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    """Crea y retorna una conexion a PostgreSQL (Supabase). Usa DATABASE_URL del .env."""
    pass


def close_connection(conn):
    """Cierra una conexion a la base de datos de forma segura."""
    pass
