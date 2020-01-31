from discord import Embed

embed_color: int = 00000000


def create_image_embed(char_data: dict) -> Embed:
    """
    Creates the embed object from the character data with the character image.
    :param char_data: `dict`
    :return: `discord.Embed`
    :raise: `KeyError`
    """
    try:
        img_url: str = char_data["image"]
    except KeyError:
        raise KeyError("Character not found")

    embed: Embed = Embed(title=char_data["title"], color=embed_color)
    embed.set_image(url=img_url)
    return embed
