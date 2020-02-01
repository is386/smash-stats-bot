import sqlite3

from discord import Game, Embed
from discord.ext import commands

from smashstats import moveset, embeds
from secret import token

db_name = "prefixes.db"
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
    conn: sqlite3.Connection = sqlite3.connect(db_name)
    c: sqlite3.Cursor = conn.cursor()
    c = c.execute(
        "SELECT prefix FROM prefixes WHERE server_id={}".format(ctx.guild.id))
    rows = c.fetchall()

    if len(rows) == 0:
        return default_prefix

    p = rows[0][0]
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


@bot.command(name='prefix')
@commands.has_permissions(administrator=True)
async def set_prefix(ctx: commands.Context, prefix: str):
    """
    Async function to send a direct message with the help text.
    :param ctx: `Context`
    :param prefix: `str`
    :return: `None`
    """
    # TODO: If the user is missing an argument, tell them the correct format.
    # TODO: If the server_id exists, then update. Else do an insert. Right now theres only update.

    if len(prefix) > 3:
        ctx.send("That prefix is too long. It must 3 characters or less.")
        return

    conn: sqlite3.Connection = sqlite3.connect(db_name)
    c: sqlite3.Cursor = conn.cursor()
    c.execute(
        'UPDATE prefixes SET prefix="{}" WHERE server_id={}'.format(prefix, ctx.guild.id))
    conn.commit()
    conn.close()
    await ctx.send("Your new prefix has been set to **{}**".format(prefix))


@set_prefix.error
async def set_prefix_error(ctx: commands.Context, error: commands.CommandError):
    """
    Async function to send a message if a user is missing permissions to change the prefix.
    :param ctx: `Context`
    :param error: `commands.CommandError`
    :return: `None`
    """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("{} you need the permission **Administrator** to set the prefix.".format(ctx.author.mention))


bot.run(token)
