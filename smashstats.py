import discord
from yaml import safe_load as yamlLoad
from asyncio import TimeoutError

prefix = "?"
charPath = "characters/%s.yml"
embedColor = 00000000
moveError = "The move **%s** does not exist. `?help` for more."
charError = "The character **%s** doesn't exist. `?help` for more."
hBoxError = "**%s** does not have a hitbox gif yet. `?help` for more."
matchMsg = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```%s```"
nums = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
cmds = ["viz", "vis"]

client = discord.Client()
tokenFile = open("test", "r")
token = tokenFile.read().strip()
tokenFile.close()


# Takes a move/char and translates it based on the synonyms yaml.
# Returns False if the move/char does not exist and returns the root move/char name if the move/char is a synonym.
def Translate(og, synFile):
    # Dictionary with a "main" move/char name as the key and synonyms for the move/char as the values.
    # Keeps the move/char name consistent while allowing for multiple ways to refer to a move/char.
    # Example: nair = neutral air, bayonetta = bayo.
    synData = yamlLoad(open(synFile))

    synList = list(synData.keys())
    if og in synList:
        return og

    for i in synList:
        if og in synData[i]:
            return i

    return False


# Takes in a string that could be a character name.
# Returns the data for the character. Returns False if the given character does not exist or has no data.
def GetCharacter(char):
    char = Translate(char, "charSynonyms.yml")
    if not char:
        return False

    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    charData = yamlLoad(open(charPath % char))

    if charData == None:
        return False

    return charData


# Takes in a move name and a character's move data.
# Returns the move in a specific format. Returns False if the move was not found.
def GetMove(ogMove, charData):
    move = Translate(ogMove, "moveSynonyms.yml")
    if not move:
        for i in charData.keys():
            if "names" in charData[i].keys() and ogMove in charData[i]["names"]:
                move = i
    return move


# Takes in a move name and a character's move data.
# Returns a list of moves that match the move name.
def GetMatchingMoves(moves, charData):
    matching = []

    for i in moves:
        if "image" in charData[i]:
            matching.append(i)

    return matching


# Takes in a list of moves, a character's move data, and the original request.
# Sends a message to the user asking them to pick the move from the list.
# Returns the move that the user picked.
async def ParseMoveSelection(movesList, charData, req):
    msg = ""
    c = 0

    for i in movesList:
        c += 1
        moveName = charData[i]["title"]
        msg += ("\n %d. %s" % (c, moveName))

    resp = await req.channel.send(matchMsg % msg)

    for i in range(len(movesList)):
        await resp.add_reaction(nums[i])

    n = await WaitForMoveSelection(req, resp)
    await resp.delete()

    if n == -1:
        return False
    return movesList[n]


# Takes in a character's data.
# Returns an embed object with an image link.
def CreateImageEmbed(charData):
    try:
        imgURL = charData["image"]
    except KeyError:
        return False
    embed = discord.Embed(title=charData["title"], color=embedColor)
    embed.set_image(url=imgURL)
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
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="Type %shelp" % prefix))


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
    if cmd in cmds:
        # Gets character's move data.
        char = ''.join(e for e in msg[1] if e.isalnum()).lower()
        charData = GetCharacter(char)
        if not charData:
            await req.channel.send(charError % char)
            LogError(req.content)
            return

        # Gets move data
        if len(msg) > 2:
            move = ''.join(e for e in "".join(
                msg[2:]) if e.isalnum()).lower().lower()
            tempMove = move

            if move not in charData.keys():
                move = GetMove(move, charData)

            if not move:
                await req.channel.send(moveError % tempMove)
                LogError(req.content)
                return

            # Checks if the move has multiple hitboxes
            matching = [i for i in charData.keys() if move in i]
            if len(matching) > 1:
                moves = GetMatchingMoves(matching, charData)
                if not moves:
                    await req.channel.send(hBoxError % charData[move]["title"])
                    return
                elif len(moves) == 1:
                    move = moves[0]
                else:
                    move = await ParseMoveSelection(moves, charData, req)
                    if not move:
                        return
        else:
            move = char

    # Sends the message response.
    if cmd == "viz" or cmd == "vis":
        embed = CreateImageEmbed(charData[move])
        if embed == False:
            await req.channel.send(hBoxError % charData[move]["title"])
            return
        await req.channel.send(embed=embed)
        return
    elif cmd == "help":
        helpFile = open("help", "r")
        helpMsg = helpFile.read()
        helpFile.close()
        await req.author.send(helpMsg)
        return


client.run(token)
