from sqlite3 import Connection, Cursor, connect


def connect_to_prefix_db(db_name: str):
    """
    Connect to the given DB and create a prefixes table.

    :param db_name: `str` name of the database
    :return: `Connection` connection to db
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
