from typing import List, Optional, Tuple

import discord

from smashstats import embeds, move_model, moveset

timeout: float = 120.0
not_yours: str = "Only the person who ran the command can use this."


def build_response(char_name: str, move_name: str, user_id: int,
                   want_hitbox: bool) -> Tuple[discord.Embed, Optional[discord.ui.View]]:
    """
    Build the embed for a resolved move, plus a view to see its other half.

    :param char_name: `str` character's code name
    :param move_name: `str` move's code name
    :param user_id: `int` id of the user allowed to press the button
    :param want_hitbox: `bool` True for the gif, False for the frame data
    :return: `Tuple` the embed and a view, or None when there is no other half
    :raises moveset.MoveLookupError: if the move has no data to show
    """
    move: move_model.Move = moveset.get_move_data(char_name, move_name)

    if move is None:
        raise moveset.MoveLookupError(
            moveset.move_error.format(move_name, char_name))

    title: str = move.get_title()

    if want_hitbox:
        if move.get_image() is None:
            raise moveset.MoveLookupError(moveset.hbox_error.format(title))
        embed: discord.Embed = embeds.create_viz_embed(move)
        has_other: bool = len(move.get_frame_data()) != 0
    else:
        if len(move.get_frame_data()) == 0:
            raise moveset.MoveLookupError(moveset.stats_error.format(title))
        embed = embeds.create_stats_embed(move)
        has_other = move.get_image() is not None

    if not has_other:
        return embed, None

    return embed, MoveDetailView(move, user_id, want_hitbox)


class OwnedView(discord.ui.View):
    """A view only the user who ran the command may interact with."""

    def __init__(self, user_id: int):
        super().__init__(timeout=timeout)
        self.user_id: int = user_id
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Reject anyone who didn't run the original command.

        :param interaction: `Interaction` the component interaction
        :return: `bool` True if the press is allowed
        """
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(not_yours, ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """
        Grey out the components once the view expires.

        :return: `None`
        """
        for item in self.children:
            item.disabled = True

        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class MoveDetailView(OwnedView):
    """A button that shows the other half of a move: stats <-> hitbox."""

    def __init__(self, move: move_model.Move, user_id: int, showing_hitbox: bool):
        """
        :param move: `move_model.Move` the move already on screen
        :param user_id: `int` id of the user allowed to press the button
        :param showing_hitbox: `bool` True if the gif is the one on screen
        """
        super().__init__(user_id)
        self.move: move_model.Move = move
        self.showing_hitbox: bool = showing_hitbox
        self.toggle.label = "Show stats" if showing_hitbox else "Show hitbox"

    @discord.ui.button(label="​", style=discord.ButtonStyle.secondary)
    async def toggle(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Send the half of the move that isn't on screen yet.

        :param interaction: `Interaction` the button press
        :param button: `Button` the button that was pressed
        :return: `None`
        """
        if self.showing_hitbox:
            embed: discord.Embed = embeds.create_stats_embed(self.move)
        else:
            embed = embeds.create_viz_embed(self.move)

        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)
        self.stop()


class MoveSelectView(OwnedView):
    """A dropdown for picking between a move's multiple hitboxes."""

    def __init__(self, char_name: str, moves: List[str], user_id: int, want_hitbox: bool):
        """
        :param char_name: `str` character's code name
        :param moves: `List[str]` move code names to choose from
        :param user_id: `int` id of the user allowed to use the dropdown
        :param want_hitbox: `bool` True for the gif, False for the frame data
        """
        super().__init__(user_id)
        self.char_name: str = char_name
        self.want_hitbox: bool = want_hitbox
        self.picker.options = [
            discord.SelectOption(
                label=(moveset.move_title(char_name, m) or m)[:100], value=m)
            for m in moves[:moveset.max_choices]
        ]

    @discord.ui.select(placeholder="Pick a version")
    async def picker(self, interaction: discord.Interaction, select: discord.ui.Select):
        """
        Show the move the user picked, replacing the dropdown.

        :param interaction: `Interaction` the dropdown selection
        :param select: `Select` the dropdown that was used
        :return: `None`
        """
        try:
            embed, view = build_response(
                self.char_name, select.values[0], self.user_id, self.want_hitbox)
        except moveset.MoveLookupError as error:
            await interaction.response.edit_message(content=str(error), embed=None, view=None)
            self.stop()
            return

        await interaction.response.edit_message(content=None, embed=embed, view=view)

        if view is not None:
            view.message = await interaction.original_response()

        self.stop()
