import sqlite3

from discord import Game, Embed
from discord.ext import commands

from smashstats import moveset, embeds
from secret import token

default_prefix = "?"
status_msg: str = "Type {}help"
embed_error: str = "An error has occurred during the creation of the embed:\n{}"


async def get_prefix(bot, ctx) -> str:
    """
    Async function to get the server's custom prefix
    :param bot: `commands.Bot`
    :param ctx: `Context`
    :return: `str`
    """
    conn: sqlite3.Connection = sqlite3.connect("prefixes.db")
    c: sqlite3.Cursor = conn.cursor()
    c = c.execute(
        "SELECT prefix FROM prefixes WHERE server_id={}".format(ctx.guild.id))

    if c == None:
        return default_prefix

    p = c.fetchone()[0]
    conn.close()
    return p


bot: commands.Bot = commands.Bot(
    command_prefix=get_prefix,
    help_command=None,
    activity=Game(status_msg.format(default_prefix)))


@bot.command(name='viz', aliases=['vis'])
async def visualize_hitbox(ctx: commands.Context):
    """
    Async function to send an embedded message with a hitbox visual.
    :param ctx: `Context`
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
    :param ctx: `Context`
    :return: `None`
    """
    with open("help", "r") as help_file:
        help_msg: str = help_file.read()
    await ctx.author.send(help_msg)
    await ctx.send("Sent you a DM {}.".format(ctx.author.mention))


bot.run(token)
