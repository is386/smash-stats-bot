from sqlite3 import Connection, Cursor, connect
from typing import List


def connect_to_prefix_db(db_name: str) -> Connection:
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


def connect_to_synonyms_db() -> Connection:
    """
    Connect to the synonyms database.

    :return: `Connection` connection to db
    """
    conn: Connection = connect("databases/synonyms.db")
    return conn


def connect_to_characters_db() -> Connection:
    """
    Connect to the synonyms database.

    :return: `Connection` connection to db
    """
    conn: Connection = connect("databases/characters.db")
    return conn


def get_similar_chars(char_name: str, db: Connection) -> List[str]:
    """
    Return a list of matches for the given character name.

    :param char_name: `str` name of the character
    :param db: `Connection` connection to the synonyms db
    :return: `List[str]`
    """
    chars: List[str] = []
    char_name = "%{}%".format(char_name)
    c: Cursor = db.cursor()

    c = db.execute("""
        SELECT
            name
        FROM
            characters
        WHERE
            name LIKE ?""", (char_name,))
    rows = c.fetchall()
    chars = [row[0] for row in rows]

    c = db.execute("""
        SELECT
            synonym
        FROM
            char_synonyms
        WHERE
            char_synonyms.synonym LIKE ?
    """, (char_name,))
    rows = c.fetchall()
    chars = chars + [row[0] for row in rows]

    return chars


def select_char(char_name: str, db: Connection) -> str:
    """
    Get the code name of the given character name.

    :param move_name: `str` name of the character
    :param db: `Connection` connection to the synonyms db
    :return: `str`
    """
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM characters where name=?", (char_name,))
    rows = c.fetchall()

    if len(rows) != 0:
        return rows[0][0]

    c = db.execute("""
        SELECT
            characters.name
        FROM
            characters, char_synonyms
        WHERE
            char_synonyms.synonym = ?
        AND
            char_synonyms.char_id = characters.id
    """, (char_name,))
    rows = c.fetchall()

    if len(rows) == 0:
        return ""

    return rows[0][0]


def select_move(move_name: str, db: Connection) -> str:
    """
    Get the code name of the given move.

    :param move_name: `str` name of the move
    :param db: `Connection` connection to the synonyms db
    :return: `str`
    """
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM moves where name=?", (move_name,))
    rows = c.fetchall()

    if len(rows) != 0:
        return rows[0][0]

    c = db.execute("""
        SELECT
            moves.name
        FROM
            moves, move_synonyms
        WHERE
            move_synonyms.synonym = ?
        AND
            move_synonyms.move_id = moves.id
    """, (move_name,))
    rows = c.fetchall()

    if len(rows) == 0:
        return ""

    return rows[0][0]


def char_has_move(char_name: str, move_name: str, db: Connection) -> bool:
    """
    Check if the character has the given move.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `bool`
    """
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            name
        FROM
            {}
        WHERE
            name=?""".format(char_name), (move_name,))
    rows = c.fetchall()

    if len(rows) == 0:
        return False

    return True


def get_move_list(char_name: str, db: Connection) -> List[str]:
    """
    Get a list of the moves the character has.

    :param char_name: `str` name of the character
    :param db: `Connection` connection to the characters db
    :return: `List[str]`
    """
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            name
        FROM
            {}
    """.format(char_name))
    rows = c.fetchall()

    if len(rows) == 0:
        return []

    return [row[0] for row in rows]


def move_has_hitbox(char_name: str, move_name: str, db: Connection) -> bool:
    """
    Check if the given move has a hitbox gif.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `bool`
    """
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            image
        FROM
            {}
        WHERE
            name=?""".format(char_name), (move_name,))
    rows = c.fetchall()

    if len(rows) == 0:
        return False

    return True


def get_move_title(char_name: str, move_name: str, db: Connection) -> str:
    """
    Get the full move name.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `bool`
    """
    c: Cursor = db.cursor()
    c = db.execute("""
        SELECT
            title
        FROM
            {}
        WHERE
            name=?""".format(char_name), (move_name,))
    rows = c.fetchall()

    if len(rows) == 0:
        return ""

    return rows[0][0]
