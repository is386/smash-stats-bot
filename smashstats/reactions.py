from asyncio import TimeoutError
from typing import List

from discord import Message, User
from discord.ext.commands import Context

timeout = 60.0
number_emojis: List[str] = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣',
                            '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


async def move_selection(ctx: Context, resp: Message, emoji_count: int) -> int:
    """
    Wait for the user to pick a number emoji.

    :param ctx: `Context` original message context
    :param resp: `Message` message to add reactions to
    :param emoji_count: `int` number of emojis to react with
    :return: `int` or -1 if nothing is chosen
    """
    for i in range(emoji_count):
        await resp.add_reaction(number_emojis[i])

    try:
        # This loop prevents a bug where if you did two stats cmds and reacted to one of them,
        # it would send the follow up message to both messages instead of the one that was reacted to.
        while True:
            await ctx.bot.wait_for('reaction_add',
                                   timeout=timeout,
                                   check=lambda react, user: str(react.emoji) in number_emojis and user == ctx.author)

            # Updates the response sent earlier with the newly added reactions.
            resp = await ctx.channel.fetch_message(resp.id)
            for reaction in resp.reactions:
                users: List[User] = await reaction.users().flatten()
                if reaction.count > 1 and ctx.author in users:
                    n: int = number_emojis.index(reaction.emoji)
                    return n
    except TimeoutError:
        return -1
