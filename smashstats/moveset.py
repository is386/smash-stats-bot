from re import sub, search, Match
from sqlite3 import Connection
from typing import List

from discord import Message
from discord.ext.commands import Context

from smashstats import database, reactions, move_model

syntax_error: str = "You have to specify a character and a move\nCorrect syntax: `{}viz character move`"
move_error: str = "The move **{}** does not exist. `{}help` for more."
char_error: str = "That character doesn't exist. `{}help` for more."
hbox_error: str = "**{}** does not have a hitbox gif yet. `{}help` for more."
stats_error: str = "**{}** does not have stats yet. `{}help` for more."
select_msg: str = "There are multiple hitboxes for this move. React within 60s with the hitbox you would like (Sender Only):\n```{}```"
synonyms_db: Connection = database.connect_to_synonyms_db()
chars_db: Connection = database.connect_to_characters_db()


async def get_move(ctx: Context) -> dict:
    """
    Get the YAML data for a character's move.

    :param ctx: `Context` message that has the character and move
    :return: `dict` on success, an empty dictionary on fail
    """
    # Get the message.
    msg: List[str] = ctx.message.content.lower().split()
    if len(msg) < 2:
        await ctx.send(syntax_error.format(ctx.prefix))
        return None

    # Remove special characters from the message.
    for i, string in enumerate(msg):
        msg[i] = sub(r"[^\w\d]|[_\-]", "", string)

    # Get the character name and move name from the message.
    if len(msg) <= 10:
        char, move = split_char_move(msg[1:])
        if len(char) == 0:
            await ctx.send(char_error.format(ctx.prefix))
            return None
        elif len(move) == 0:
            await ctx.send(syntax_error.format(ctx.prefix))
            return None
    else:
        await ctx.send("That message is too long!")
        return None

    # Get the given move's code name.
    orig_move: str = move
    move = parse_move(move, char)
    if len(move) == 0:
        await ctx.send(move_error.format(orig_move, ctx.prefix))
        return None

    # For minmin
    move = "fair" if move == "bair" and char == "minmin" else move

    # Parse moves that have multiple hitboxes.
    moveset = database.get_move_list(char, chars_db)
    multi_moves = [entry for entry in moveset if move in entry]
    if len(multi_moves) > 1:
        move = await parse_multi_moves(ctx, multi_moves, char)
        if len(move) == 0:
            return None
        elif move == "no hitboxes":
            await ctx.send(hbox_error.format(move, ctx.prefix))
            return None
    elif move[-1].isalpha():
        move += "1"

    # Construct Move object.
    move_data: move_model.Move = get_move_data(char, move)
    if move_data is None:
        await ctx.send(move_error.format(orig_move, ctx.prefix))
        return None

    return move_data


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


def parse_move(move_name: str, char_name: str) -> str:
    """
    Parse the given move name by its synonym.

    :param move_name: `str` user given move name
    :param move_name: `str` user given character name
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


async def parse_multi_moves(ctx: Context, moves: List[str], char_name: str) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.

    :param ctx: `Context` original message context
    :param moves: `List[str]` moves that are similar
    :param char_name: `str` character's name
    :return: `str` empty if failed, "no hitboxes" if moves don't have hitboxes.
    """
    if str(ctx.command) == "viz":
        moves_to_select = []
        for i in moves:
            if database.move_has_hitbox(char_name, i, chars_db):
                moves_to_select.append(str(i))

        if len(moves_to_select) == 0:
            return "no hitboxes"
        elif len(moves_to_select) == 1:
            move = moves_to_select[0]
        else:
            move = await send_move_selector(char_name, moves_to_select, ctx)
    else:
        # TODO: check for no frame data
        move = await send_move_selector(char_name, moves, ctx)

    return move


async def send_move_selector(char: str, moves: List[str], ctx: Context) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.

    :param char_name: `str` character's name
    :param moves: `List[str]` moves that are similar
    :param ctx: `Context` original message context
    :return: `str` empty if failed
    """
    msg: str = ""

    for i, move in enumerate(moves):
        move_name = database.get_move_title(char, move, chars_db)
        msg += "\n {}. {}".format(i + 1, move_name)

    response: Message = await ctx.send(select_msg.format(msg))
    answer_index: int = await reactions.move_selection(ctx, response, len(moves))

    if answer_index == -1:
        await response.edit(content="You took too long to select a move.")
        await response.clear_reactions()
        return ""

    await response.delete()
    return moves[answer_index]


def get_move_data(char_name: str, move_name: str) -> move_model.Move:
    """
    Return a move object with the code name, title, and image.

    :param char: `str` character's name
    :param move: `str` move name
    :return: `move_mode.Move` None if failed
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
