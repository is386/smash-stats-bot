import discord
from yaml import safe_load as yamlLoad

prefix = "?"
cmdPath = "characters/%s.yml"
embedColor = 00000000
moveError1 = "The move **%s** does not exist. `?help` for more."
charError1 = "The character **%s** doesn't exist. `?help` for more."
charError2 = "The character **%s** has no data yet. `?help` for more."
hBoxError = "**%s** does not have a hitbox gif yet. `?help` for more."
matchMsg = "There are multiple hitboxes for this move. React with the hitbox you would like (Sender Only):\n```%s```"
nums = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

client = discord.Client()
tokenFile = open("test", "r")
token = tokenFile.read().strip()
tokenFile.close()


# Takes a move/char and translates it based on the synonyms yaml.
# Returns "Invalid" if the move/char does not exist and returns the root move/char name if the move/char is a synonym.
def Translate(og, synFile):
    # Dictionary with a "main" move/char name as the key and synonyms for the move/char as the values.
    # Keeps the move/char name consistent while allowing for multiple ways to refer to a move/char.
    # Example: nair = neutral air, bayonetta = bayo
    synData = yamlLoad(open(synFile))

    synList = list(synData.keys())
    if og in synList:
        return og

    for i in synList:
        if og in synData[i]:
            return i

    return "Invalid"


# Takes in a cmd name.
# Returns an embed object and image file.
def CreateImageEmbed(cmdData):
    try:
        imgURL = cmdData["image"]
    except KeyError:
        return False
    embed = discord.Embed(title=cmdData["title"], color=embedColor)
    embed.set_image(url=imgURL)
    return embed


# Waits for a reaction on stats or viz and then sends the opposite command if the message is reacted to.
async def WaitForReaction(req, resp):
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

    # Checks cmd type.
    cmd = msg[0][1:].lower()
    if cmd == "viz" or cmd == "vis":

        # Parses the character name.
        char = msg[1].lower()
        tempChar = char
        char = Translate(char, "charSynonyms.yml")
        if char == "Invalid":
            await req.channel.send(charError1 % tempChar)
            return

        # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
        cmdData = yamlLoad(open(cmdPath % char))

        if cmdData == None:
            await req.channel.send(charError2 % char)
            return

        # Parses the move name.
        move = char
        if len(msg) > 2:
            move = "".join(msg[2:]).lower()
            if move not in cmdData.keys():
                tempMove = move
                move = Translate(move, "moveSynonyms.yml")
                if move == "Invalid":
                    for i in cmdData.keys():
                        if "names" in cmdData[i].keys() and tempMove in cmdData[i]["names"]:
                            move = i
                if move == "Invalid":
                    await req.channel.send(moveError1 % tempMove)
                    return

        # Checks if the move has multiple hitboxes
        matching = [i for i in cmdData.keys() if move in i]
        actualMatching = []
        if len(matching) > 1:
            s = ""
            b = 0
            for i in range(len(matching)):
                try:
                    m = cmdData[matching[i]]["image"]
                    actualMatching.append(matching[i])
                except KeyError:
                    b += 1
                    continue
                m = cmdData[matching[i]]["title"]
                s += ("\n %d. %s" % (i+1-b, m))

            if not actualMatching:
                await req.channel.send(hBoxError % cmdData[move]["title"])
                return
            elif len(actualMatching) == 1:
                move = actualMatching[0]
            else:
                resp = await req.channel.send(matchMsg % s)

                for i in range(len(actualMatching)):
                    await resp.add_reaction(nums[i])

                n = await WaitForReaction(req, resp)
                if n == -1:
                    return

                move = actualMatching[n]

                await resp.delete()

        # Sends the message response.
        if cmd == "viz" or cmd == "vis":
            embed = CreateImageEmbed(cmdData[move])
            if embed == False:
                await req.channel.send(hBoxError % cmdData[move]["title"])
                return
        embed.set_footer(
            text="You can send comments and questions to 1nder#5023")
        await req.channel.send(embed=embed)
        return

    elif cmd == "help":
        helpMsg = open("help", "r").read()
        await req.author.send(helpMsg)
        return
    else:
        return


client.run(token)
