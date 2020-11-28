from discord import Embed
from smashstats import move_model

embed_color: int = 00000000

def create_viz_embed(move: move_model.Move) -> Embed:
    """
    Create the image embed object from the move object.

    :param move: `move_model.Move` move's data model
    :return: `Embed` image message to send to the user
    """
    embed: Embed = Embed(title=move.get_title(), color=embed_color)
    embed.set_image(url=move.get_image().replace(" ", ""))
    return embed


def create_stats_embed(move: move_model.Move) -> Embed:
    """
    Create the text embed object from the move object.

    :param move: `move_model.Move` move's data model
    :return: `Embed` text message to send to the user
    """
    embed: Embed = Embed(title=move.get_title(),
                         color=embed_color)
    frame_data: dict = move.get_frame_data()

    for fd in frame_data.keys():
        if frame_data[fd] is not None:
            embed.add_field(name=fd, value=frame_data[fd], inline=True)

    return embed
