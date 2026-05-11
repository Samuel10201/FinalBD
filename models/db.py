import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Crea y retorna una conexion a PostgreSQL (Supabase).
    Usa DATABASE_URL del .env.
    
    Retorna:
        psycopg2.connection: Conexión a la base de datos
    
    Raises:
        psycopg2.Error: Si no puede conectarse a la BD
    """
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError('DATABASE_URL no configurada en .env')
        
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.Error as e:
        print(f"Error de conexión a la BD: {e}")
        raise


def close_connection(conn):
    """Cierra una conexión a la base de datos de forma segura.
    
    Args:
        conn (psycopg2.connection): Conexión a cerrar
    """
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"Error cerrando conexión: {e}")
