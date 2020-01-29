from asyncio import TimeoutError
from typing import List

import discord
import yaml
from yaml import safe_load as yaml_load

prefix = "?"
charPath = "characters/{}.yml"
embed_color = 00000000
moveError = "The move **{}** does not exist. `?help` for more."
charError = "That character doesn't exist. `?help` for more."
hBoxError = "**{}** does not have a hitbox gif yet. `?help` for more."
matchMsg = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```{}```"
number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
cmds = ("{}viz".format(prefix), "{}vis".format(prefix))

client = discord.Client()
tokenFile = open("test", "r")
token = tokenFile.read().strip()
tokenFile.close()


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
        synData = yaml_load(f)

    synList = list(synData.keys())
    if name in synList:
        return name

    for key in synList:
        if name in synData[key]:
            return key

    return ""


def get_character(char: str) -> dict:
    """
    Returns the parsed Yaml of the character as a dictionary
    :param char: `str` char name
    :return: `dict` empty if failed
    """
    char: str = translate(char, "charSynonyms.yml")
    if len(char) == 0:
        return {}

    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    with open(charPath.format(char)) as f:
        try:
            char_data: dict = yaml_load(f)
        except yaml.YAMLError as e:
            print(e)
            return {}

    return char_data


def get_real_move_name(move_name: str, char_data: dict) -> str:
    """
    Extracts the move's code name from the character data
    :param move_name: `str`
    :param char_data: `dict`
    :return: `str` empty if not found
    """
    move: str = translate(move_name, "moveSynonyms.yml")
    if len(move) == 0:
        entry_name: str
        for entry_name in char_data.keys():
            if "names" in char_data[entry_name].keys() and move_name in char_data[entry_name]["names"]:
                move = entry_name
    return move


# Takes in a move name and a character's move data.
# Returns a list of moves that match the move name.
def get_matching_moves(moves: list, char_data: dict) -> list:
    """
    Returns the list of moves in the character data matching any of the moves passed in
    :param moves: `list`
    :param char_data: `dict`
    :return: `list`
    """
    matching = []

    for entry in moves:
        if "image" in char_data[entry]:
            matching.append(entry)

    return matching


async def parse_move_selection(moves: List[str], char_data: dict, message: discord.Message) -> str:
    """
    Async function to ask for user input on a list of moves to pick one.
    :param moves: `List[str]`
    :param char_data: `dict`
    :param message: `discord.Message`
    :return: `str` empty if failed
    """
    msg: str = ""
    count_possibilities: int = 0

    for move in moves:
        count_possibilities += 1
        move_name = char_data[move]["title"]
        msg += "\n {}. {}".format(count_possibilities, move_name)

    response = await message.channel.send(matchMsg.format(msg))

    for i, _ in enumerate(moves):
        await response.add_reaction(number_emojis[i])

    answer_index: int = await wait_for_move_selection(message, response)
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

    embed: discord.Embed = discord.Embed(title=char_data["title"], color=embed_color)
    embed.set_image(url=img_url)
    return embed


async def wait_for_move_selection(req: discord.Message, resp: discord.Message) -> int:
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
            await client.wait_for('reaction_add',
                                  timeout=120.0,
                                  check=lambda react, user: str(react.emoji) in number_emojis and user == req.author)

            # Updates the response sent earlier with the newly added reactions.
            resp = await req.channel.fetch_message(resp.id)  # TODO: Check if this is useful, resp should be the same
            for reaction in resp.reactions:
                users = await reaction.users().flatten()
                if reaction.count > 1 and req.author in users:
                    n = number_emojis.index(reaction.emoji)
                    return n
    except TimeoutError:
        return -1


def log_error(msg: str):
    """
    Logs an error message
    :param msg: `str`
    :return: `None`
    """
    with open("log", "a") as log:
        log.write(msg + "\n")


# Sets the bots status on start up.
@client.event
async def on_ready():
    servers: list = client.guilds
    server: discord.Guild
    for server in servers:
        print(server.name)
    print(len(servers))
    await client.change_presence(status=discord.Status.do_not_disturb,
                                 activity=discord.Game(
                                     name="Type {}help".format(prefix)
                                 ))


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Parses the message so that msg[0] is the command, msg[1] the character and msg[2] teh move
    msg: List[str] = message.content.split(" ", 1)
    msg += msg.pop().rsplit()
    if len(msg) < 2:
        await message.channel.send(
            "You have to specify a character and a move\nCorrect syntax: `{}viz character move`".format(prefix))
        return

    # This actually allows for the command to register from messages like "?vizbdfraibdfwuya character move"
    # not sure if wanted
    if msg[0].startswith(cmds):
        char_data: dict = get_character(msg[1].lower())
        if len(char_data) == 0:
            await message.channel.send(charError)
            log_error(message.content)
            return

        # Gets move data
        move: str = msg[-1]
        if move not in char_data.keys():
            move = get_real_move_name(move, char_data)
        if len(move) == 0:
            await message.channel.send(moveError.format(move))
            log_error(message.content)
            return

        # Checks if the move has multiple hitboxes
        matching = [entry for entry in char_data.keys() if move in entry]
        if len(matching) > 1:
            moves: list = get_matching_moves(matching, char_data)
            if len(moves) == 0:
                await message.channel.send(hBoxError.format(char_data[move]["title"]))
                return
            elif len(moves) == 1:
                move = moves[0]
            else:
                move = await parse_move_selection(moves, char_data, message)
                if len(move) == 0:
                    return

        # Sends the message response.
        try:
            embed: discord.Embed = create_image_embed(char_data[move])
        except KeyError as e:
            print("An error has occurred during the creation of the embed:\n{}".format(e.args))
            await message.channel.send(hBoxError.format(char_data[move]["title"]))
            return
        await message.channel.send(embed=embed)
    elif msg[0].startswith("{}help".format(prefix)):
        with open("help", "r") as helpFile:
            helpMsg = helpFile.read()
        await message.author.send(helpMsg)
        await message.channel.send("Sent you a DM {}.".format(message.author.mention))


client.run(token)
