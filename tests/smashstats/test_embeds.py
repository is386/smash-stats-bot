import pytest
from smashstats import embeds, move_model


def test_create_image_embed():
    move = move_model.Move("test", "title", "url")
    embed = embeds.create_image_embed(move)
    assert embed.image.url == "url" and embed.title == "title"
