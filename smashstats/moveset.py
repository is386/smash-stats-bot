from re import sub
from typing import List

from discord import Message
from discord.ext.commands import Context
from yaml import safe_load, YAMLError

from smashstats import reactions
from smashstats import translator


char_path: str = "characters/{}.yml"
char_syns_path: str = "synonyms/characters.yml"
move_syns_path: str = "synonyms/moves.yml"
syntax_error: str = "You have to specify a character and a move\nCorrect syntax: `{}viz character move`"
move_error: str = "The move **{}** does not exist. `?help` for more."
char_error: str = "That character doesn't exist. `?help` for more."
hbox_error: str = "**{}** does not have a hitbox gif yet. `?help` for more."
select_msg: str = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```{}```"


async def get_move_data(ctx: Context) -> dict:
    """
    Gets the YAML data for a character's move
    :param ctx: `Context` message that has the character and move
    :return: `dict` on success, an empty dictionary on fail
    """
    msg: List[str] = ctx.message.content.split()
    if len(msg) < 2:
        await ctx.send(syntax_error.format(ctx.prefix))
        return {}

    # Removes special characters from character and move
    for i, string in enumerate(msg):
        print(string)
        msg[i] = sub(r"[^\w\d]", "", string).lower()

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
    move = get_real_move_name(move, char_data)
    if move not in char_data.keys():
        await ctx.send(move_error.format(orig_move))
        return {}

    # Finds moves that match parsed move. If so, that move has multiple hitboxes.
    matching_moves = [entry for entry in char_data.keys() if move in entry]
    if len(matching_moves) > 1:
        # Removes the matching moves that do not have an image
        for i in matching_moves:
            if "image" not in char_data[i].keys():
                matching_moves.remove(i)

        if len(matching_moves) == 0:
            await ctx.send(hbox_error.format(move))
            return {}
        elif len(matching_moves) == 1:
            move = matching_moves[0]
        else:
            move = await parse_move_selection(matching_moves, char_data, ctx)
            if len(move) == 0:
                return {}

    return char_data[move]


def split_char_move(msg: list) -> tuple:
    """
    Splits the character from the move name
    :param msg: `list` original msg
    :return: `tuple` like: (char, move), can be unpacked on call
    """
    acc: str = msg.pop(0)
    char: str = translator.trans(acc, char_syns_path)
    while char == "" and len(msg) > 0:
        acc += msg.pop(0)
        char = translator.trans(acc, char_syns_path)
    return char, ''.join(msg)


def get_character(char: str) -> dict:
    """
    Returns the parsed Yaml of the character as a dictionary
    :param char: `str` char name
    :return: `dict` empty if failed
    :raise: `yaml.YAMLError`
    """
    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    with open(char_path.format(char)) as f:
        try:
            char_data: dict = safe_load(f)
        except YAMLError:
            raise YAMLError()

    return char_data


def get_real_move_name(move_name: str, char_data: dict) -> str:
    """
    Extracts the move's code name from the character data
    :param move_name: `str`
    :param char_data: `dict`
    :return: `str` empty if not found
    """
    move: str = translator.trans(move_name, move_syns_path)
    if len(move) == 0:
        entry_name: str
        for entry_name in char_data.keys():
            if "names" in char_data[entry_name].keys() and move_name in char_data[entry_name]["names"]:
                move = entry_name
    return move


async def parse_move_selection(moves: List[str], char_data: dict, ctx: Context) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.
    :param moves: `List[str]`
    :param char_data: `dict`
    :param ctx: `Context`
    :return: `str` empty if failed
    """
    msg: str = ""

    for i, move in enumerate(moves):
        move_name = char_data[move]["title"]
        msg += "\n {}. {}".format(i+1, move_name)

    response: Message = await ctx.send(select_msg.format(msg))
    answer_index: int = await reactions.move_selection(ctx, response, len(moves))
    await response.delete()

    if answer_index == -1:
        return ""
    return moves[answer_index]
