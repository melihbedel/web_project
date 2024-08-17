from mariadb import connect
from mariadb.connections import Connection


def _get_connection() -> Connection:
    ''' Connects to the database through MariaDB.'''
    
    return connect(
        user='root',
        password='1234',
        host='127.0.0.1',
        port=3306,
        database='web_teamwork'
    )


def read_query(sql: str, sql_params=()):
    "No results = [ ]"
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql: str, sql_params=()) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql: str, sql_params=()) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.rowcount


def read_query_additional(sql: str, sql_params=()):
    """No results = None"""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return cursor.fetchone()