import pytest

from smashstats.moveset import split_char_move, parse_move, translate_move, get_move_data
from smashstats import move_model

# TODO: either make get_move_data() not depend from ctx or split it up more so we can make a test
# ?viz
# ?viz banjo
# ?viz banjo nair
# ?viz banjo neutral air
# ?viz banjo dair1
# ?viz banjo dair2
# ?viz inkling nspecial
# ?viz dr. mario back aerial
# Use these for get_move_data()
# parse_multi_moves and send_move_selector require user input/context


def test_split_char_move():
    msg = "?viz bowser jr nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "bowserjr" and move == "nair"

    msg = "?viz banjo and kazooie nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "banjo" and move == "nair"

    msg = "?viz king k rool neutral air".split()
    char, move = split_char_move(msg[1:])
    assert char == "kingkrool" and move == "neutralair"

    msg = "?viz wolf forward tilt".split()
    char, move = split_char_move(msg[1:])
    assert char == "wolf" and move == "forwardtilt"

    msg = "?viz rob nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "rob" and move == "nair"

    msg = "?viz robin nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "robin" and move == "nair"

    msg = "?viz mario nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "mario" and move == "nair"

    msg = "?viz drmario nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "drmario" and move == "nair"


def test_parse_move():
    assert parse_move("nair", "banjo") == "nair"
    assert parse_move("neutralair", "banjo") == "nair"
    assert parse_move("nspecial1", "banjo") == "nspecial1"
    assert parse_move("nspecial2", "banjo") == "nspecial2"
    assert parse_move("nspecial6", "banjo") == ""
    assert parse_move("iohioehgioaeig", "banjo") == ""


def test_translate_move():
    assert translate_move("forwardtilt") == "ftilt"
    assert translate_move("forwardssmashdown") == "fsmash"
    assert translate_move("fhoaiuwhfawo eiofew") == ""


def test_get_move_data():
    assert get_move_data("banjo", "asdasds") is None
    assert get_move_data("asdasds", "nair") is None
    assert get_move_data("asdasds", "asdasds") is None
    assert get_move_data("banjo", "nair1") == sample_move_data


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
