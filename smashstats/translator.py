from typing import List
from yaml import safe_load


def trans(name: str, file_path: str) -> list:
    """
    Translate a synonyms (move or char) into the base name.

    :param name: `str` name/synonym to translate
    :param file_path: `str` synonyms file path
    :return: `list` list of all the possible matches, empty if none
    """
    # Dictionary with a "main" move/char name as the key and a list with synonyms for the move/char as the values.
    # Keeps the move/char name consistent while allowing for multiple ways to refer to a move/char.
    # Example: nair = neutral air, bayonetta = bayo.
    # TODO: Database table with each synonym associated with the original name, better lookup performances
    with open(file_path, 'r') as f:
        synonyms: dict = safe_load(f)

    code_names: List[str] = [name] if name in list(synonyms.keys()) else []
    code_names += [item[0] for item in synonyms.items() if name in item[1]]

    return code_names
