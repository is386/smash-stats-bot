from discord import Embed
from smashstats import move_model

embed_color: int = 00000000


def create_image_embed(move: move_model.Move) -> Embed:
    """
    Create the embed object from the move object..

    :param move: `move_model.Move` move's data model
    :return: `Embed` image message to send to the user
    :raise: `KeyError`
    """
    try:
        img_url: str = move.get_image()
    except KeyError:
        raise KeyError("Move image not found")

    embed: Embed = Embed(title=move.get_title(), color=embed_color)
    embed.set_image(url=img_url)
    return embed
