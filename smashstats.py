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
formError = "Too many parameters. You should try conjoining character or move names that are multiple words.\n`Ex: ?viz duckhunt backair`"
moveError1 = "The move \"%s\" does not exist."
moveError2 = "This character does not have the move \"%s\"."
charError1 = "The character \"%s\" doesn't exist."
charError2 = "The character \"%s\" has no data yet."

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
    embed = discord.Embed(color=embedColor)
    img = (hboxPath % char) + cmdData["image"]
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

    if len(msg) > 3:
        await req.channel.send(formError)
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
    if len(msg) == 3:
        move = msg[2].lower()
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

    # Sends the message response.
    if cmd == "viz":
        embed, attach = CreateImageEmbed(cmdData[move], char)
    else:
        return
    await req.channel.send(embed=embed, file=attach)

client.run(token)
