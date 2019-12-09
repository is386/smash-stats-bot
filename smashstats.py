# TODO
# DOWNLOAD ALL HITBOXES
# IMPLEMENT STAT EMBEDS FOR RIDLEY
# GET ALL STATS

import discord
from yaml import safe_load as yamlLoad

prefix = "?"
cmdPath = "characters/%s/commands.yml"
hboxPath = "characters/%s/hitboxes/"
embedColor = 00000000
moveError1 = "The move \"%s\" does not exist."
moveError2 = "This character does not have the move \"%s\"."
charError1 = "The character \"%s\" doesn't exist."
charError2 = "The character \"%s\" has no data yet."
hBoxError = "This move does not have a hitbox graphic."
matchMsg = "There are multiple hitboxes for this move:\n```%s```"
nums = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

client = discord.Client()
tokenFile = open("token", "r")
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
def CreateImageEmbed(cmdData, char):
    try:
        img = (hboxPath % char) + cmdData["image"]
    except KeyError:
        return False, False
    embed = discord.Embed(title=cmdData["title"] ,color=embedColor)
    f = CreateEmbedAttachment(embed, img, "image")
    return embed, f


# Takes an embed, file name, and option to declare the attachment as a thumbnail or image.
# Returns a file object that can be attached to an embedded message.
def CreateEmbedAttachment(embed, filename, attachType):
    # This assures the image is uploaded as a gif file.
    imgURL = "attachment://" + "img.gif"

    # This sets the url of the image the message will use.
    if attachType == "thumbnail":
        embed.set_thumbnail(url=imgURL)
    elif attachType == "image":
        embed.set_image(url=imgURL)

    f = discord.File(filename, "img.gif")
    return f


# Waits for a reaction on stats or viz and then sends the opposite command if the message is reacted to.
async def WaitForReaction(req, resp):
    try:
        # Checks if the reaction to a message matches the indicated emoji.
        def CheckReaction(reaction, user):
            return str(reaction.emoji) in nums and user == req.author

        # This loop prevents a bug where if you did two stats cmds and reacted to one of them, 
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await client.wait_for('reaction_add', timeout=60.0, check=CheckReaction)

            # Updates the response sent earlier with the newly added reactions.
            resp = await req.channel.fetch_message(resp.id)
            # Makes sure the response being reacted to isn't some other message from before.
            for r in resp.reactions:
                if r.count > 1:
                    n = nums.index(r.emoji)
                    return n

    except TimeoutError:
        return

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
    if cmd != "viz" and cmd != "stats":
        return

    # Parses the character name.
    char = msg[1].lower()
    tempChar = char
    char = Translate(char, "charSynonyms.yml")
    if char == "Invalid":
        await req.channel.send(charError1 % tempChar)
        return

    # Parses the move name.
    move = char
    if len(msg) > 2:
        move = "".join(msg[2:]).lower()
        tempMove = move
        move = Translate(move, "moveSynonyms.yml")
        if move == "Invalid":
            await req.channel.send(moveError1 % tempMove)
            return

    # Dictionary with command name as the key and the command attributes (title, text, image, etc.) as the values.
    cmdData = yamlLoad(open(cmdPath % char))
    if cmdData == None:
        await req.channel.send(charError2 % char)
        return
    elif move not in list(cmdData.keys()):
        await req.channel.send(moveError2 % tempMove)
        return

    # Checks if the move has multiple hitboxes
    matching = [i for i in cmdData.keys() if move in i]
    if len(matching) > 1:
        s = ""

        for i in range(len(matching)):
            m = cmdData[matching[i]]["title"]
            s += ("\n %d. %s" % (i+1 ,m))

        resp = await req.channel.send(matchMsg % s)

        for i in range(len(matching)):
            await resp.add_reaction(nums[i])

        n = await WaitForReaction(req, resp)
        move = matching[n]
        await resp.delete()

    # Sends the message response.
    if cmd == "viz":
        embed, attach = CreateImageEmbed(cmdData[move], char)
        if embed == False:
            await req.channel.send(hBoxError)
            return
    else:
        return
    await req.channel.send(embed=embed, file=attach)


client.run(token)
