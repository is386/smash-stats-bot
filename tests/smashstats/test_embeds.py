import pytest
from smashstats import embeds, move_model


def test_create_viz_embed():
    embed = embeds.create_viz_embed(sample_move_data)
    assert embed.image.url == "https://ultimateframedata.com/hitboxes/banjo_and_kazooie/Banjo_KazooieNAir.gif"
    assert embed.title == "Neutral Air"


def test_create_stats_embed():
    embed = embeds.create_stats_embed(sample_move_data)
    assert embed.title == "Neutral Air"
    assert embed.fields[0].name == "Startup"
    assert embed.fields[0].value == "10/13/16/19/22/25/28/31"

    assert embed.fields[1].name == "On Shield"
    assert embed.fields[1].value == "-14/-13"

    assert embed.fields[2].name == "Active On"
    assert embed.fields[2].value == "10-11/13-14/16-17/19-20/22-23/25-26/28-29/31-32"

    assert embed.fields[3].name == "Total Frames"
    assert embed.fields[3].value == "47"

    assert embed.fields[4].name == "Landing Lag"
    assert embed.fields[4].value == "16"

    assert embed.fields[5].name == "Base Damage"
    assert embed.fields[5].value == "0.8/4.2"

    assert embed.fields[6].name == "Shield Lag"
    assert embed.fields[6].value == "4/10"

    assert embed.fields[7].name == "Shield Stun"
    assert embed.fields[7].value == "2/3"


sample_move_data = move_model.Move(
    "nair1", "Neutral Air", "https://ultimateframedata.com/hitboxes/banjo_and_kazooie/Banjo_KazooieNAir.gif")
sample_move_data.set_startup("10/13/16/19/22/25/28/31")
sample_move_data.set_onshield("-14/-13")
sample_move_data.set_activeon(
    "10-11/13-14/16-17/19-20/22-23/25-26/28-29/31-32")
sample_move_data.set_totalframes("47")
sample_move_data.set_landinglag("16")
sample_move_data.set_basedmg("0.8/4.2")
sample_move_data.set_shieldlag("4/10")
sample_move_data.set_shieldstun("2/3")
