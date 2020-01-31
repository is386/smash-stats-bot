from discord import Game, Embed
from discord.ext import commands

import moveset
import embeds
from secret import token

prefix = "?"
status_msg: str = "Type {}help"
embed_error: str = "An error has occurred during the creation of the embed:\n{}"

bot: commands.Bot = commands.Bot(
    command_prefix=prefix,
    help_command=None,
    activity=Game(status_msg.format(prefix)))


@bot.command(name='viz', aliases=['vis'])
async def visualize_hitbox(ctx: commands.Context):
    """
    Async function to sends an embedded message with a hitbox visual.
    :param ctx: `discord.ext.commands.Context`
    :return: `None`
    """
    move_data: dict = await moveset.get_move_data(ctx)
    if len(move_data) == 0:
        return

    try:
        embed: Embed = embeds.create_image_embed(move_data)
        await ctx.send(embed=embed)
    except KeyError as e:
        print(embed_error.format(e.args))
        await ctx.send(moveset.hbox_error.format(move_data["title"]))


@bot.command(name='help')
async def send_help(ctx: commands.Context):
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
