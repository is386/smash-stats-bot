import sqlite3


def connect_to_prefix_db(db_name: str):
    """
    Connects to the given DB and creates a prefixes table.
    :param db_name: `str`
    :return: `sqlite3.Connection`
    """
    conn: sqlite3.Connection = sqlite3.connect(db_name)
    c: sqlite3.Cursor = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS prefixes (
            server_id int not NULL,
            prefix char(256) NOT NULL,
            PRIMARY KEY (server_id)
        )
    """)
    conn.commit()
    return conn
