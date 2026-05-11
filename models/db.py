"""
Modulo que permite a Python comunicarse con el SO. Sirve para encontrar las 
variables de entorno.
"""
import os
"""
Es un Driver. Se encarga de tomar las consultas SQL hechas desde Python y ponerlas
en el formato que espera Postgresql. Permite la conexion al servidor con el 
protocolo TCP.
"""
import psycopg2
"""
Es una clase tipo cursor que permite obtener los resultados de una consulta en un 
diccionario de Python en lugar de una tupla. Mucho mejor pq en una tupla la 
referencia son los indices, lo que es muy sensible, ya que si se cambia el orden de 
las columnas en la tabla original o la consulta entonces habra inconsistencias.
"""
from psycopg2.extras import RealDictCursor


def get_connection():
    """
    Crea y retorna una conexion a PostgreSQL (Supabase). Usa DATABASE_URL del .env.
    Retorna un objeto de tipo connection, que sirve para comunicarse con la db.
    """
    return psycopg2.connect(os.environ['DATABASE_URL'], cursor_factory=RealDictCursor)

def close_connection(conn):
    """Cierra una conexion a la base de datos de forma segura."""
    if conn and conn.closed == 0:
        conn.close()
