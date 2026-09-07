from typing import List

import discord
from discord import app_commands

from smashstats import moveset, views
from secret import token

status_msg: str = "⚠️ UPDATE! Click my profile to fix cmds"
help_file: str = "help"
char_desc: str = "The character, e.g. banjo, bowserjr, kingkrool"
move_desc: str = "The move, e.g. nair, forward tilt, dspecial2"
unknown_error: str = "Something went wrong running that command."


class SmashStats(discord.Client):
    """The bot client, with an app command tree and no privileged intents."""

    def __init__(self):
        # Slash commands arrive as self-contained interaction payloads, so the
        # bot never needs to read message content.
        super().__init__(intents=discord.Intents.none(),
                         activity=discord.Activity(
                             type=discord.ActivityType.watching,
                             name=status_msg))
        self.tree: app_commands.CommandTree = app_commands.CommandTree(self)

    async def setup_hook(self):
        """
        Publish the command tree to Discord on startup.

        :return: `None`
        """
        await self.tree.sync()


client: SmashStats = SmashStats()


async def character_autocomplete(interaction: discord.Interaction,
                                 current: str) -> List[app_commands.Choice]:
    """
    Suggest character names as the user types.

    :param interaction: `Interaction` the in-progress command
    :param current: `str` what the user has typed so far
    :return: `List[Choice]`
    """
    return [app_commands.Choice(name=c, value=c)
            for c in moveset.character_choices(current)]


async def move_autocomplete(interaction: discord.Interaction,
                            current: str) -> List[app_commands.Choice]:
    """
    Suggest moves belonging to whichever character has been filled in.

    :param interaction: `Interaction` the in-progress command
    :param current: `str` what the user has typed so far
    :return: `List[Choice]`
    """
    char: str = moveset.find_character(interaction.namespace.character or "")

    if len(char) == 0:
        return []

    return [app_commands.Choice(name=label, value=value)
            for label, value in moveset.move_choices(char, current)]


async def send_move(interaction: discord.Interaction, character: str, move: str,
                    want_hitbox: bool):
    """
    Resolve the character and move, then answer with a gif or frame data.

    :param interaction: `Interaction` the command invocation
    :param character: `str` user given character name
    :param move: `str` user given move name
    :param want_hitbox: `bool` True for the gif, False for the frame data
    :return: `None`
    """
    try:
        char: str = moveset.resolve_character(character)
        candidates: List[str] = moveset.resolve_moves(char, move)

        # Drop the candidates that can't answer this command, so a dropdown
        # never offers an option that errors when picked.
        if want_hitbox:
            usable: List[str] = moveset.with_hitboxes(char, candidates)
            missing: str = moveset.hbox_error
        else:
            usable = moveset.with_frame_data(char, candidates)
            missing = moveset.stats_error

        if len(usable) == 0:
            title: str = moveset.move_title(char, candidates[0]) or move
            raise moveset.MoveLookupError(missing.format(title))

        candidates = usable

        if len(candidates) > 1:
            picker: views.MoveSelectView = views.MoveSelectView(
                char, candidates, interaction.user.id, want_hitbox)
            await interaction.response.send_message(moveset.select_msg, view=picker)
            picker.message = await interaction.original_response()
            return

        embed, view = views.build_response(
            char, candidates[0], interaction.user.id, want_hitbox)
    except moveset.MoveLookupError as error:
        await interaction.response.send_message(str(error), ephemeral=True)
        return

    # send_message has no Optional view: None would be dereferenced, unlike
    # edit_message where None means "remove the components".
    await interaction.response.send_message(
        embed=embed, view=view if view is not None else discord.utils.MISSING)

    if view is not None:
        view.message = await interaction.original_response()


@client.tree.command(name="stats", description="Show frame data for a character's move.")
@app_commands.describe(character=char_desc, move=move_desc)
@app_commands.autocomplete(character=character_autocomplete, move=move_autocomplete)
async def stats(interaction: discord.Interaction, character: str, move: str):
    """
    Answer with a move's frame data.

    :param interaction: `Interaction` the command invocation
    :param character: `str` user given character name
    :param move: `str` user given move name
    :return: `None`
    """
    await send_move(interaction, character, move, want_hitbox=False)


@client.tree.command(name="viz", description="Show the hitbox gif for a character's move.")
@app_commands.describe(character=char_desc, move=move_desc)
@app_commands.autocomplete(character=character_autocomplete, move=move_autocomplete)
async def viz(interaction: discord.Interaction, character: str, move: str):
    """
    Answer with a move's hitbox gif.

    :param interaction: `Interaction` the command invocation
    :param character: `str` user given character name
    :param move: `str` user given move name
    :return: `None`
    """
    await send_move(interaction, character, move, want_hitbox=True)


@client.tree.command(name="help", description="Explain how to use the bot.")
async def send_help(interaction: discord.Interaction):
    """
    Answer with the help text, visible only to the user who asked.

    :param interaction: `Interaction` the command invocation
    :return: `None`
    """
    with open(help_file, "r") as f:
        help_msg: str = f.read()
    await interaction.response.send_message(help_msg, ephemeral=True)


@client.tree.error
async def on_command_error(interaction: discord.Interaction,
                           error: app_commands.AppCommandError):
    """
    Tell the user the command failed, then re-raise for the logs.

    :param interaction: `Interaction` the command invocation
    :param error: `AppCommandError` what went wrong
    :return: `None`
    """
    if interaction.response.is_done():
        await interaction.followup.send(unknown_error, ephemeral=True)
    else:
        await interaction.response.send_message(unknown_error, ephemeral=True)

    raise error


if __name__ == "__main__":
    client.run(token)
