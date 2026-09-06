from re import search, sub, Match
from sqlite3 import Connection
from typing import List, Tuple

from smashstats import database, move_model

char_error: str = "That character doesn't exist. Try picking one from the autocomplete list."
move_error: str = "The move **{}** does not exist for **{}**. Try picking one from the autocomplete list."
hbox_error: str = "**{}** does not have a hitbox gif yet."
stats_error: str = "**{}** does not have frame data yet."
empty_move_error: str = "You have to specify a move."
select_msg: str = "This move has several versions. Pick the one you want:"

# Discord allows at most 25 options in a select menu or autocomplete response.
max_choices: int = 25

synonyms_db: Connection = database.connect_to_synonyms_db()
chars_db: Connection = database.connect_to_characters_db()


class MoveLookupError(Exception):
    """Raised when user input cannot be resolved to a character or move."""


def normalize(text: str) -> str:
    """
    Lowercase the text and strip anything that isn't a letter or a digit.

    :param text: `str` raw user input
    :return: `str` normalized text
    """
    return sub(r"[^\w\d]|[_\-]", "", text.lower())


def find_character(name: str) -> str:
    """
    Resolve user input to a character's code name.

    Exact name and synonym matches win outright; anything else falls back to a
    substring search, which is what free-typed input (rather than a pick from
    the autocomplete list) tends to need.

    :param name: `str` user given character name
    :return: `str` code name, "" if not found
    """
    name = normalize(name)
    if len(name) == 0:
        return ""

    char: str = database.select_char(name, synonyms_db)
    if len(char) != 0:
        return char

    matches = {database.select_char(m, synonyms_db)
               for m in database.get_similar_chars(name, synonyms_db)}
    matches.discard("")

    if len(matches) == 0:
        return ""

    # Prefer a name that starts with what was typed, then the shortest one, so
    # "mario" doesn't resolve to "drmario".
    return sorted(matches, key=lambda c: (not c.startswith(name), len(c), c))[0]


def resolve_character(name: str) -> str:
    """
    Resolve user input to a character's code name, or fail loudly.

    :param name: `str` user given character name
    :return: `str` code name
    :raises MoveLookupError: if the character can't be found
    """
    char: str = find_character(name)
    if len(char) == 0:
        raise MoveLookupError(char_error)
    return char


def resolve_moves(char_name: str, move_name: str) -> List[str]:
    """
    Resolve user input to every move code name it could mean.

    :param char_name: `str` character's code name
    :param move_name: `str` user given move name
    :return: `List[str]` one code name, or several when the move has multiple hitboxes
    :raises MoveLookupError: if the move can't be found
    """
    original: str = move_name.strip()
    move: str = normalize(move_name)

    if len(move) == 0:
        raise MoveLookupError(empty_move_error)

    # An exact code name, which is what the autocomplete list sends.
    if database.char_has_move(char_name, move, chars_db):
        return [move]

    move = parse_move(move, char_name)
    if len(move) == 0:
        raise MoveLookupError(move_error.format(original, char_name))

    # Min Min's back air reuses her forward air data.
    if move == "bair" and char_name == "minmin":
        move = "fair"

    candidates: List[str] = [m for m in database.get_move_list(char_name, chars_db)
                             if move in m]
    if len(candidates) == 0:
        raise MoveLookupError(move_error.format(original, char_name))

    return sort_moves(candidates)


def sort_moves(moves: List[str]) -> List[str]:
    """
    Sort move code names so trailing numbers order naturally (nair2 before nair11).

    :param moves: `List[str]` move code names
    :return: `List[str]` sorted code names
    """
    def key(move: str) -> Tuple[str, int]:
        match: Match = search(r'\d+$', move)
        if match is None:
            return move, 0
        return move[:match.start()], int(match.group())

    return sorted(moves, key=key)


def parse_move(move_name: str, char_name: str) -> str:
    """
    Parse the given move name by its synonym.

    :param move_name: `str` user given move name
    :param char_name: `str` character's code name
    :return: `str` empty if not found
    """
    n_match: Match = search(r'\d+$', move_name)
    n = ""

    if n_match is not None:
        n = move_name[n_match.start():n_match.end()]
        move_name = move_name[:n_match.start()]

    if not database.char_has_move(char_name, move_name, chars_db):
        move_name = translate_move(move_name, char_name)

    if len(move_name) == 0 or (not database.char_has_move(char_name, move_name + n, chars_db) and len(n) != 0):
        return ""

    return move_name + n


def translate_move(move_name: str, char_name: str) -> str:
    """
    Extract the move's code name from the character data.

    :param move_name: `str` user given move name
    :param char_name: `str` character's code name
    :return: `str` empty if not found
    """
    move: str = database.select_move(move_name, synonyms_db)
    # TODO: make table for canon move names
    if len(move) == 0:
        for m in database.get_move_list(char_name, chars_db):
            title: str = database.get_move_title(
                char_name, m, chars_db).split(",", 1)[0].lower().replace(" ", "")
            if move_name == title:
                return m
    return move


def move_title(char_name: str, move_name: str) -> str:
    """
    Get the full name of a move.

    :param char_name: `str` character's code name
    :param move_name: `str` move's code name
    :return: `str` "" if not found
    """
    return database.get_move_title(char_name, move_name, chars_db)


def with_hitboxes(char_name: str, moves: List[str]) -> List[str]:
    """
    Keep only the moves that have a hitbox gif.

    :param char_name: `str` character's code name
    :param moves: `List[str]` move code names
    :return: `List[str]` code names that have a gif
    """
    return [m for m in moves if database.move_has_hitbox(char_name, m, chars_db)]


def with_frame_data(char_name: str, moves: List[str]) -> List[str]:
    """
    Keep only the moves that have frame data.

    :param char_name: `str` character's code name
    :param moves: `List[str]` move code names
    :return: `List[str]` code names that have frame data
    """
    return [m for m in moves if database.move_has_frame_data(char_name, m, chars_db)]


def character_choices(query: str) -> List[str]:
    """
    Character code names matching a partial query, for autocomplete.

    :param query: `str` what the user has typed so far
    :return: `List[str]` at most `max_choices` code names
    """
    query = normalize(query)

    if len(query) == 0:
        return database.get_all_chars(synonyms_db)[:max_choices]

    matches = {database.select_char(m, synonyms_db)
               for m in database.get_similar_chars(query, synonyms_db)}
    matches.discard("")

    ranked: List[str] = sorted(
        matches, key=lambda c: (not c.startswith(query), len(c), c))
    return ranked[:max_choices]


def move_choices(char_name: str, query: str) -> List[Tuple[str, str]]:
    """
    A character's moves matching a partial query, for autocomplete.

    :param char_name: `str` character's code name
    :param query: `str` what the user has typed so far
    :return: `List[Tuple[str, str]]` at most `max_choices` (label, code name) pairs
    """
    query = normalize(query)
    choices: List[Tuple[str, str]] = []

    # Kept in db order, which runs jab -> tilts -> smashes -> aerials ->
    # specials, so browsing the list without typing lands on real moves rather
    # than alphabetically-first airdodges.
    for move in database.get_move_list(char_name, chars_db):
        title: str = move_title(char_name, move) or move
        if len(query) != 0 and query not in move and query not in normalize(title):
            continue

        label: str = "{} ({})".format(title, move)
        choices.append((label[:100], move))

        if len(choices) == max_choices:
            break

    return choices


def get_move_data(char_name: str, move_name: str) -> move_model.Move:
    """
    Return a move object with the code name, title, and image.

    :param char_name: `str` character's code name
    :param move_name: `str` move's code name
    :return: `move_model.Move` None if failed
    """
    move_data: tuple = database.select_move_data(
        char_name, move_name, chars_db)

    if len(move_data) == 0:
        return None

    move = move_model.Move(move_data[0], move_data[1], move_data[2])
    move.set_startup(move_data[3])
    move.set_onshield(move_data[4])
    move.set_activeon(move_data[5])
    move.set_totalframes(move_data[6])
    move.set_landinglag(move_data[7])
    move.set_basedmg(move_data[8])
    move.set_shieldlag(move_data[9])
    move.set_shieldstun(move_data[10])
    return move
