import pytest
from smashstats import embeds, move_model


def test_create_viz_embed():
    move = move_model.Move("test", "title", "url")
    embed = embeds.create_viz_embed(move)
    assert embed.image.url == "url" and embed.title == "title"
