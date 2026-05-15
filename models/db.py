import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()

_pool = None


def _get_pool():
    global _pool
    if _pool is None or _pool.closed:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError('DATABASE_URL no configurada en .env')
        _pool = SimpleConnectionPool(1, 5, database_url, cursor_factory=RealDictCursor)
    return _pool


def get_connection():
    return _get_pool().getconn()


def close_connection(conn):
    if conn:
        try:
            _get_pool().putconn(conn)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
