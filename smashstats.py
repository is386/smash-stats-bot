import re
from asyncio import TimeoutError
from typing import List

import discord
from discord.ext import commands
import yaml
from yaml import safe_load as yaml_load

from secret import token

prefix = "?"
char_path: str = "characters/{}.yml"
char_syns_path: str = "charSynonyms.yml"
move_syns_path: str = "moveSynonyms.yml"
embed_color: int = 00000000
status_msg: str = "Type {}help"
syntax_error: str = "You have to specify a character and a move\nCorrect syntax: `{}viz character move`"
move_error: str = "The move **{}** does not exist. `?help` for more."
char_error: str = "That character doesn't exist. `?help` for more."
hbox_error: str = "**{}** does not have a hitbox gif yet. `?help` for more."
embed_error: str = "An error has occurred during the creation of the embed:\n{}"
select_msg: str = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```{}```"
number_emojis: List[str] = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                            '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

bot: discord.ext.commands.Bot = commands.Bot(
    command_prefix=prefix,
    help_command=None,
    activity=discord.Game(status_msg.format(prefix)))


def translate(name: str, file_path: str) -> str:
    """
    Translates a synonyms (move or char) into the base name
    :param name: `str` name/synonym to translate
    :param file_path: `str` synonyms file path
    :return: `str` on success, an empty string if failed
    """
    # Dictionary with a "main" move/char name as the key and a list with synonyms for the move/char as the values.
    # Keeps the move/char name consistent while allowing for multiple ways to refer to a move/char.
    # Example: nair = neutral air, bayonetta = bayo.
    # TODO: Database table with each synonym associated with the original name, better lookup performances
    with open(file_path, 'r') as f:
        synonyms: dict = yaml_load(f)

    code_names: List[str] = list(synonyms.keys())
    if name in code_names:
        return name

    for key in code_names:
        if name in synonyms[key]:
            return key

    return ""


def split_char_move(msg: list) -> tuple:
    """
    Splits the character from the move name
    :param msg: `list` original msg
    :return: `tuple` like: (char, move), can be unpacked on call
    """
    acc: str = msg.pop(0)
    char: str = translate(acc, char_syns_path)
    while char == "" and len(msg) > 0:
        acc += msg.pop(0)
        char = translate(acc, char_syns_path)
    return char, ''.join(msg)


def get_character(char: str) -> dict:
    """
    Returns the parsed Yaml of the character as a dictionary
    :param char: `str` char name
    :return: `dict` empty if failed
    """
    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    with open(char_path.format(char)) as f:
        try:
            char_data: dict = yaml_load(f)
        except yaml.YAMLError:
            raise yaml.YAMLError()

    return char_data


def get_real_move_name(move_name: str, char_data: dict) -> str:
    """
    Extracts the move's code name from the character data
    :param move_name: `str`
    :param char_data: `dict`
    :return: `str` empty if not found
    """
    move: str = translate(move_name, move_syns_path)
    if len(move) == 0:
        entry_name: str
        for entry_name in char_data.keys():
            if "names" in char_data[entry_name].keys() and move_name in char_data[entry_name]["names"]:
                move = entry_name
    return move


async def parse_move_selection(moves: List[str], char_data: dict, ctx: discord.ext.commands.Context) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.
    :param moves: `List[str]`
    :param char_data: `dict`
    :param message: `discord.Message`
    :return: `str` empty if failed
    """
    msg: str = ""

    for i, move in enumerate(moves):
        move_name = char_data[move]["title"]
        msg += "\n {}. {}".format(i+1, move_name)

    response: discord.Message = await ctx.send(select_msg.format(msg))

    for i, _ in enumerate(moves):
        await response.add_reaction(number_emojis[i])

    answer_index: int = await wait_for_move_selection(ctx, response)
    await response.delete()

    if answer_index == -1:
        return ""
    return moves[answer_index]


def create_image_embed(char_data: dict) -> discord.Embed:
    """
    Creates the embed object from the character data with the character image
    :param char_data: `dict`
    :return: `discord.Embed`
    :raise: `KeyError`
    """
    try:
        img_url: str = char_data["image"]
    except KeyError:
        raise KeyError("Character not found")

    embed: discord.Embed = discord.Embed(
        title=char_data["title"], color=embed_color)
    embed.set_image(url=img_url)
    return embed


async def wait_for_move_selection(ctx: discord.ext.commands.Context, resp: discord.Message) -> int:
    """
    Takes in the original request, and the response the bot sent.
    :param req: `discord.Message`
    :param resp: `discord.Message`
    :return: `int` or -1 if nothing is chosen
    """
    try:
        # This loop prevents a bug where if you did two stats cmds and reacted to one of them,
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await bot.wait_for('reaction_add',
                               timeout=120.0,
                               check=lambda react, user: str(react.emoji) in number_emojis and user == ctx.author)

            # Updates the response sent earlier with the newly added reactions.
            resp = await ctx.channel.fetch_message(resp.id)
            for reaction in resp.reactions:
                users: List[discord.User] = await reaction.users().flatten()
                if reaction.count > 1 and ctx.author in users:
                    n: int = number_emojis.index(reaction.emoji)
                    return n
    except TimeoutError:
        return -1


def log_error(msg: str):
    """
    Logs a message that caused an error.
    :param msg: `str`
    :return: `None`
    """
    with open("log", "a") as log:
        log.write(msg + "\n")


@bot.command(name='viz')
async def visualize_hitbox(ctx: discord.ext.commands.Context):
    """
    Async function to sends an embedded message with a hitbox visual.
    :param ctx: `discord.ext.commands.Context`
    :return: `None`
    """
    # Parses the message so that msg[0] is the command, msg[1] the character and msg[2] the move
    msg: List[str] = ctx.message.content.split(" ", 1)
    msg = msg.pop().rsplit()
    if len(msg) < 2:
        await ctx.send(syntax_error.format(prefix))
        return

    # Removes special characters from character and move
    for i, string in enumerate(msg):
        msg[i] = re.sub(r"[^\w\d]", "", string)

    # Parses the full character and move name
    if len(msg) <= 10:
        char, move = split_char_move(msg)
        if len(char) == 0:
            await ctx.send(char_error)
            log_error(ctx.message.content)
            return
        elif len(move) == 0:
            await ctx.send(syntax_error.format(prefix))
            return
    else:
        await ctx.send("That message is too long!")
        return

    # Gets character data
    try:
        char_data: dict = get_character(char.lower())
    except yaml.YAMLError as e:
        print(e)
        return

    # Gets move data
    orig_move: str = move
    move = get_real_move_name(move, char_data)
    if move not in char_data.keys():
        await ctx.send(move_error.format(orig_move))
        log_error(ctx.message.content)
        return

    # Finds moves that match parsed move. If so, that move has multiple hitboxes.
    matching_moves = [entry for entry in char_data.keys() if move in entry]
    if len(matching_moves) > 1:
        # Removes the matching moves that do not have an image
        for i in matching_moves:
            if "image" not in char_data[i]:
                matching_moves.remove(i)

        if len(matching_moves) == 0:
            await ctx.send(hbox_error.format(move))
            return
        elif len(matching_moves) == 1:
            move = matching_moves[0]
        else:
            move = await parse_move_selection(matching_moves, char_data, ctx)
            if len(move) == 0:
                return

    try:
        embed: discord.Embed = create_image_embed(char_data[move])
    except KeyError as e:
        print(embed_error.format(e.args))
        await ctx.send(hbox_error.format(char_data[move]["title"]))
        return
    await ctx.send(embed=embed)


@bot.command(name='help')
async def send_help(ctx: discord.ext.commands.Context):
    """
    Async function to send a direct message with the help text.
    :param ctx: `discord.ext.commands.Context`
    :return: `None`
    """
    with open("help", "r") as help_file:
        help_msg: str = help_file.read()
    await ctx.author.send(help_msg)
    await ctx.send("Sent you a DM {}.".format(ctx.author.mention))


bot.run(token)
