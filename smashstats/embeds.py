from discord import Embed

embed_color: int = 00000000


def create_image_embed(move_data: dict) -> Embed:
    """
    Create the embed object from the move's data with the move's image.

    :param move_data: `dict` move's yaml data
    :return: `Embed` image message to send to the user
    :raise: `KeyError`
    """
    try:
        img_url: str = move_data["image"]
    except KeyError:
        raise KeyError("Move image not found")

    embed: Embed = Embed(title=move_data["title"], color=embed_color)
    embed.set_image(url=img_url)
    return embed
