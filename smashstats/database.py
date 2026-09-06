from sqlite3 import Connection, Cursor, connect
from typing import List


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


def get_all_chars(db: Connection) -> List[str]:
    """
    Return every character's code name, alphabetically.

    :param db: `Connection` connection to the synonyms db
    :return: `List[str]`
    """
    c: Cursor = db.execute("SELECT name FROM characters ORDER BY name")
    return [row[0] for row in c.fetchall()]


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
    rows: List = c.fetchall()
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
    :return: `str` "" if not found
    """
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM characters where name=?", (char_name,))
    rows: List = c.fetchall()

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
    :return: `str` "" if not found
    """
    c: Cursor = db.cursor()
    c = db.execute("SELECT name FROM moves where name=?", (move_name,))
    rows: List = c.fetchall()

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
    rows: List = c.fetchall()

    if len(rows) == 0:
        return ""

    return rows[0][0]


def get_char_id(char_name: str, db: Connection) -> int:
    """
    Get the character's id in the db.

    :param char_name: `str` name of the character
    :param db: `Connection` connection to the characters db
    :return: `int` 0 if not found.
    """
    c: Cursor = db.cursor()
    c = db.execute("SELECT id FROM char_names WHERE name = ?", (char_name,))
    rows: List = c.fetchall()

    if len(rows) == 0:
        return 0

    return rows[0][0]


def select_move_data(char_name: str, move_name: str, db: Connection) -> tuple:
    """
    Get the name, title, and image of a move from the character's table.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `List[str]` [] if not found.
    """
    c: Cursor = db.cursor()
    i: int = get_char_id(char_name, db)
    c = db.execute("""
            SELECT
                *
            FROM
                frame_data, char_names
            WHERE
                frame_data.name = ?
            AND
                char_names.id = ?
            AND
                char_names.id = frame_data.char_id""", (move_name, i))
    rows: List = c.fetchall()

    if len(rows) == 0:
        return []

    return rows[0][1:12]


def char_has_move(char_name: str, move_name: str, db: Connection) -> bool:
    """
    Check if the character has the given move.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `bool`
    """
    c: Cursor = db.cursor()
    i: int = get_char_id(char_name, db)
    c = db.execute("""
            SELECT
                frame_data.name
            FROM
                frame_data, char_names
            WHERE
                frame_data.name = ?
            AND
                char_names.id = ?
            AND
                char_names.id = frame_data.char_id""", (move_name, i))
    rows: List = c.fetchall()

    if len(rows) == 0:
        return False

    return True


def get_move_list(char_name: str, db: Connection) -> List[str]:
    """
    Get a list of the moves the character has.

    :param char_name: `str` name of the character
    :param db: `Connection` connection to the characters db
    :return: `List[str]` [] if not found
    """
    c: Cursor = db.cursor()
    i: int = get_char_id(char_name, db)
    c = db.execute(
        "SELECT name FROM frame_data WHERE char_id = ?", (i,))
    rows: List = c.fetchall()

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
    i: int = get_char_id(char_name, db)
    c = db.execute("""
            SELECT
                image
            FROM
                frame_data, char_names
            WHERE
                frame_data.name = ?
            AND
                char_names.id = ?
            AND
                char_names.id = frame_data.char_id""", (move_name, i))
    rows: List = c.fetchall()

    if len(rows) == 0 or rows[0][0] is None:
        return False

    return True


def move_has_frame_data(char_name: str, move_name: str, db: Connection) -> bool:
    """
    Check if the given move has any frame data at all.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `bool`
    """
    c: Cursor = db.cursor()
    i: int = get_char_id(char_name, db)
    c = db.execute("""
            SELECT
                startup, on_shield, active_on, total_frames,
                landing_lag, base_dmg, shield_lag, shield_stun
            FROM
                frame_data, char_names
            WHERE
                frame_data.name = ?
            AND
                char_names.id = ?
            AND
                char_names.id = frame_data.char_id""", (move_name, i))
    rows: List = c.fetchall()

    if len(rows) == 0:
        return False

    return any(value is not None for value in rows[0])


def get_move_title(char_name: str, move_name: str, db: Connection) -> str:
    """
    Get the full move name.

    :param char_name: `str` name of the character
    :param move_name: `str` name of the move
    :param db: `Connection` connection to the characters db
    :return: `str` "" if not found
    """
    c: Cursor = db.cursor()
    i: int = get_char_id(char_name, db)
    c = db.execute("""
            SELECT
                title
            FROM
                frame_data, char_names
            WHERE
                frame_data.name = ?
            AND
                char_names.id = ?
            AND
                char_names.id = frame_data.char_id""", (move_name, i))
    rows: List = c.fetchall()

    if len(rows) == 0:
        return ""

    return rows[0][0]
