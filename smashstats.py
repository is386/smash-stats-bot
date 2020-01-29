from typing import List

import discord
import yaml
from yaml import safe_load as yaml_load
from asyncio import TimeoutError

prefix = "?"
charPath = "characters/{}.yml"
embed_color = 00000000
moveError = "The move **%s** does not exist. `?help` for more."
charError = "That character doesn't exist. `?help` for more."
hBoxError = "**%s** does not have a hitbox gif yet. `?help` for more."
matchMsg = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```{}```"
nums = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
cmds = ["viz", "vis"]

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
        await response.add_reaction(nums[i])

    answer_index: int = await WaitForMoveSelection(message, response)
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
        img_url = char_data["image"]
    except KeyError:
        raise KeyError("Character not found")

    embed = discord.Embed(title=char_data["title"], color=embed_color)
    embed.set_image(url=img_url)
    return embed


# Takes in the original request, and the response the bot sent.
# Returns a number based on the emoji they picked for the move selected.
# Returns -1 if the user picks nothing.
async def WaitForMoveSelection(req, resp):
    try:
        # Checks if the reaction to a message matches the indicated emoji.
        def CheckReaction(reaction, user):
            e = str(reaction.emoji)
            return e in nums and user == req.author

        # This loop prevents a bug where if you did two stats cmds and reacted to one of them,
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await client.wait_for('reaction_add', timeout=120.0, check=CheckReaction)

            # Updates the response sent earlier with the newly added reactions.
            resp = await req.channel.fetch_message(resp.id)

            for r in resp.reactions:
                users = await r.users().flatten()
                if r.count > 1 and req.author in users:
                    n = nums.index(r.emoji)
                    return n

    except TimeoutError:
        return -1


# Takes in a string that is a message that caused an error.
# Saves that message in a log file.
def LogError(msg):
    logFile = open("log", "a")
    logFile.write(msg + "\n")
    logFile.close()
    return


# Sets the bots status on start up.
@client.event
async def on_ready():
    servers = list(client.guilds)
    for s in servers:
        print(s.name)
    print(len(servers))
    await client.change_presence(status=discord.Status.do_not_disturb,
                                 activity=discord.Game(name="Type %shelp" % prefix))


@client.event
async def on_message(req):
    if req.author == client.user:
        return

    # Parses the message for the command.
    msg = req.content.split()
    if not msg:
        return

    if msg[0][0] != prefix:
        return

    cmd = msg[0][1:].lower()
    moveIndex = 2
    charData = {}
    if cmd in cmds:
        # This iterates over the request and joins the character name until
        # it is found. This helps when a user puts spaces in a character's
        # name. This does slowdown the bot a bit though so I need to fix
        # this soon.
        for i in range(2, len(msg[1:]) + 2):
            # Gets character's move data.
            char = ''.join(e for e in "".join(
                msg[1:i]) if e.isalnum()).lower()
            temp = get_character(char)
            if temp:
                charData = temp
                moveIndex = i

        if not charData:
            await req.channel.send(charError)
            LogError(req.content)
            return

        # Gets move data
        if len(msg) > moveIndex:
            move = ''.join(e for e in "".join(
                msg[moveIndex:]) if e.isalpha()).lower().lower()
            tempMove = move

            if move not in charData.keys():
                move = get_real_move_name(move, charData)

            if not move:
                await req.channel.send(moveError % tempMove)
                LogError(req.content)
                return

            # Checks if the move has multiple hitboxes
            matching = [i for i in charData.keys() if move in i]
            if len(matching) > 1:
                moves = get_matching_moves(matching, charData)
                if not moves:
                    await req.channel.send(hBoxError % charData[move]["title"])
                    return
                elif len(moves) == 1:
                    move = moves[0]
                else:
                    move = await parse_move_selection(moves, charData, req)
                    if not move:
                        return
        else:
            move = char

    # Sends the message response.
    if cmd == "viz" or cmd == "vis":
        embed = create_image_embed(charData[move])
        if not embed:
            await req.channel.send(hBoxError % charData[move]["title"])
            return
        await req.channel.send(embed=embed)
        return
    elif cmd == "help":
        helpFile = open("help", "r")
        helpMsg = helpFile.read()
        helpFile.close()
        await req.author.send(helpMsg)
        await req.channel.send("Sent you a DM %s." % req.author.mention)
        return


client.run(token)
