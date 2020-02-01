import pytest
from smashstats import embeds


def test_create_image_embed():
    with pytest.raises(KeyError):
        char_data = {
            "test": "test"
        }
        embeds.create_image_embed(char_data)
