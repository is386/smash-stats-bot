from sqlite3 import Connection, Cursor, connect


def connect_to_prefix_db(db_name: str):
    """
    Connects to the given DB and creates a prefixes table.
    :param db_name: `str`
    :return: `Connection`
    """
    conn: Connection = connect(db_name)
    c: Cursor = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS prefixes (
            server_id int not NULL,
            prefix char(256) NOT NULL,
            PRIMARY KEY (server_id)
        )
    """)
    conn.commit()
    return conn
