from sqlite3 import Connection, Cursor

from discord import Game, Embed, Message
from discord.ext import commands

from smashstats import moveset, embeds, database, move_model, reactions
from secret import token

db_name = "databases/prefixes.db"
default_prefix = "?"
status_msg: str = "@Ultimate Stats help"
red_circle: str = "🔴"
embed_error: str = "An error has occurred during the creation of the embed:\n{}"
prefix_error1: str = "{} you need the permission **Administrator** to set the prefix."
prefix_error2: str = "You have to specify a prefix.\nCorrect syntax: `{}prefix new_prefix`"
footer_msg: str = "React with 🔴 within 60s to see the {}."

prefix_conn: Connection = database.connect_to_prefix_db(db_name)


async def get_prefix(bot, ctx) -> str:
    """
    Async function to get the server's custom prefix.

    :param bot: `commands.Bot` the bot object that will use the prefix
    :param ctx: `Context` original user message's context
    :return: `str` the prefix
    """
    if ctx.guild is None:
        return default_prefix

    c: Cursor = prefix_conn.cursor()
    c = c.execute(
        "SELECT prefix FROM prefixes WHERE server_id=?", (ctx.guild.id,))
    rows = c.fetchall()

    if len(rows) == 0:
        return default_prefix

    return rows[0][0]


bot: commands.Bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(get_prefix),
    help_command=None,
    activity=Game(status_msg))


@bot.command(name='viz', aliases=['vis'])
async def visualize_hitbox(ctx: commands.Context):
    """
    Async function to send an embedded message with a hitbox visual.

    :param ctx: `Context` original user message's context
    :return: `None`
    """
    move: move_model.Move = await moveset.get_move(ctx)

    if move is None:
        return

    if move.get_image() is None:
        await ctx.send(moveset.hbox_error.format(move.get_title(), ctx.prefix))
        return

    embed: Embed = embeds.create_viz_embed(move)
    embed.set_footer(text=footer_msg.format("stats"))
    resp: Message = await ctx.send(embed=embed)
    await resp.add_reaction(red_circle)

    send_stats: bool = await reactions.choose_other_fd_cmd(ctx, resp)
    if send_stats:
        if len(move.get_frame_data()) == 0:
            await ctx.send(moveset.stats_error.format(move.get_title(), ctx.prefix))
        else:
            embed: Embed = embeds.create_stats_embed(move)
            await ctx.send(embed=embed)


@bot.command(name='stats', aliases=['stat', 'data'])
async def stats(ctx: commands.Context):
    """
    Async function to send an embedded message with a move's stats.

    :param ctx: `Context` original user message's context
    :return: `None`
    """
    move: move_model.Move = await moveset.get_move(ctx)

    if move is None:
        return

    if len(move.get_frame_data()) == 0:
        await ctx.send(moveset.stats_error.format(move.get_title(), ctx.prefix))
        return

    embed: Embed = embeds.create_stats_embed(move)
    embed.set_footer(text=footer_msg.format("hitbox"))
    resp: Message = await ctx.send(embed=embed)
    await resp.add_reaction(red_circle)

    send_viz: bool = await reactions.choose_other_fd_cmd(ctx, resp)
    if send_viz:
        if move.get_image() is None:
            await ctx.send(moveset.hbox_error.format(move.get_title(), ctx.prefix))
        else:
            embed: Embed = embeds.create_viz_embed(move)
            await ctx.send(embed=embed)


@bot.command(name='help')
async def send_help(ctx: commands.Context):
    """
    Async function to send a direct message with the help text.

    :param ctx: `Context` original user message's context
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

    :param ctx: `Context` original user message's context
    :param prefix: `str` the desired prefix
    :return: `None`
    """
    if len(prefix) > 3:
        await ctx.send("That prefix is too long. It must 3 characters or less.")
        return

    c: Cursor = prefix_conn.cursor()
    c.execute("""
        INSERT INTO
            prefixes (server_id, prefix)
        VALUES
            (?, ?)
        ON CONFLICT
            (server_id)
        DO UPDATE SET
            prefix=?
    """, (ctx.guild.id, prefix, prefix))
    prefix_conn.commit()
    await ctx.send("Your new prefix has been set to **{}**".format(prefix))


@set_prefix.error
async def set_prefix_error(ctx: commands.Context, error: commands.CommandError):
    """
    Async function to send a message if a user is missing permissions to change the prefix.

    :param ctx: `Context` original user message's context
    :param error: `commands.CommandError` the error invoked by the user
    :return: `None`
    """
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(prefix_error1.format(ctx.author.mention))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(prefix_error2.format(ctx.prefix))


bot.run(token)
