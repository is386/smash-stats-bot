from re import sub, search, Match
from sqlite3 import Connection
from typing import List

from discord import Message
from discord.ext.commands import Context
from yaml import safe_load, YAMLError

from smashstats import database, reactions

char_path: str = "characters/{}.yml"
syntax_error: str = "You have to specify a character and a move\nCorrect syntax: `{}viz character move`"
move_error: str = "The move **{}** does not exist. `?help` for more."
char_error: str = "That character doesn't exist. `?help` for more."
hbox_error: str = "**{}** does not have a hitbox gif yet. `?help` for more."
select_msg: str = "There are multiple hitboxes for this move. React within 60s with the hitbox you would like (Sender Only):\n```{}```"
synonyms_db: Connection = database.connect_to_synonyms_db()


async def get_move_data(ctx: Context) -> dict:
    """
    Get the YAML data for a character's move.

    :param ctx: `Context` message that has the character and move
    :return: `dict` on success, an empty dictionary on fail
    """
    msg: List[str] = ctx.message.content.lower().split()
    if len(msg) < 2:
        await ctx.send(syntax_error.format(ctx.prefix))
        return {}

    # Removes special characters from character and move
    for i, string in enumerate(msg):
        msg[i] = sub(r"[^\w\d]|[_\-]", "", string)

    # Parses the full character and move name
    if len(msg) <= 10:
        char, move = split_char_move(msg[1:])
        if len(char) == 0:
            await ctx.send(char_error)
            return {}
        elif len(move) == 0:
            await ctx.send(syntax_error.format(ctx.prefix))
            return {}
    else:
        await ctx.send("That message is too long!")
        return {}

    # Gets character data
    try:
        char_data: dict = get_character(char.lower())
    except YAMLError as e:
        print(e)
        return {}

    # Gets move data
    orig_move: str = move

    # Checks if the move ends in a number
    n_match: Match = search(r'\d+$', move)
    n = ""

    # Removes the number if there is one
    if n_match is not None:
        n = move[n_match.start():n_match.end()]
        move = move[:n_match.start()]

    if move not in char_data.keys():
        move = get_real_move_name(move, char_data)

    # This checks if the move plus the number is in the moveset
    # Also checks if there was a number in the given move. This is
    # to prevent the case where a numberless move is given and
    # the bot thinks its not in the moveset (since all moves end in a 1 now)
    if len(move) == 0 or (move + n not in char_data.keys() and len(n) != 0):
        await ctx.send(move_error.format(orig_move))
        return {}

    # Appends the number back to the move
    move = move + n

    # Finds moves that match parsed move. If so, that move has multiple hitboxes.
    matching_moves = [entry for entry in char_data.keys() if move in entry]
    if len(matching_moves) > 1:
        selection_moves = []
        # Removes the matching moves that do not have an image
        for i in matching_moves:
            if "image" in char_data[i].keys():
                selection_moves.append(str(i))
        if len(selection_moves) == 0:
            await ctx.send(hbox_error.format(move))
            return {}
        elif len(selection_moves) == 1:
            move = selection_moves[0]
        else:
            move = await parse_move_selection(selection_moves, char_data, ctx)
            if len(move) == 0:
                return {}
    # If there are no matches and the move didn't have a number on it
    # appends 1 to the end so that it can be found in the character's
    # moveset (all moves end in a 1 now even if theres no second part)
    # ex: nair = nair1 in the yaml
    elif move[-1].isalpha():
        move += "1"

    return char_data[move]


def split_char_move(msg: list) -> tuple:
    """
    Split the character from the move name.

    :param msg: `list` original msg
    :return: `tuple` like: (char, move), can be unpacked on call
    """
    acc: str = msg.pop(0)
    matching: List[str] = database.get_similar_chars(acc, synonyms_db)
    if len(matching) < 1:
        return '', ''

    char: str = acc
    while len(matching) > 0 and len(msg) > 0:
        tmp: str = msg.pop(0)
        acc += tmp
        matching = [match for match in matching if acc in match]
        if len(matching) < 1:
            msg.insert(0, tmp)
            break
        char = acc

    return database.select_char(char, synonyms_db), ''.join(msg)


def get_character(char: str) -> dict:
    """
    Get the parsed Yaml of the character as a dictionary.

    :param char: `str` char name
    :return: `dict` empty if failed
    :raise: `yaml.YAMLError`
    """
    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    with open(char_path.format(char)) as f:
        try:
            char_data: dict = safe_load(f)
        except YAMLError:
            raise YAMLError
        except FileNotFoundError:
            raise FileNotFoundError

    return char_data


def get_real_move_name(move_name: str, char_data: dict) -> str:
    """
    Extract the move's code name from the character data.

    :param move_name: `str` user given move name
    :param char_data: `dict` character's yaml data
    :return: `str` empty if not found
    """
    move: str = database.select_move(move_name, synonyms_db)
    if len(move) == 0:
        entry_name: str
        for entry_name in char_data.keys():
            if "names" in char_data[entry_name].keys() and move_name in char_data[entry_name]["names"]:
                return entry_name
            # DUCT TAPE FOR HERO'S SPELLS LOL IGNORE FOR NOW
            elif "title" in char_data[entry_name].keys() and move_name == "".join(char_data[entry_name]["title"].split()).lower():
                return entry_name
    return move.pop() if len(move) != 0 else ""


async def parse_move_selection(moves: List[str], char_data: dict, ctx: Context) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.

    :param moves: `List[str]` moves that are similar
    :param char_data: `dict` character's yaml data
    :param ctx: `Context` original message context
    :return: `str` empty if failed
    """
    msg: str = ""

    for i, move in enumerate(moves):
        move_name = char_data[move]["title"]
        msg += "\n {}. {}".format(i + 1, move_name)

    response: Message = await ctx.send(select_msg.format(msg))
    answer_index: int = await reactions.move_selection(ctx, response, len(moves))

    if answer_index == -1:
        await response.edit(content="You took too long to select a move.")
        await response.clear_reactions()
        return ""

    await response.delete()
    return moves[answer_index]
