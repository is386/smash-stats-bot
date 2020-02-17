import pytest

from smashstats.moveset import split_char_move, get_real_move_name


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


def test_get_real_move_name():
    assert get_real_move_name("forwardtilt") == "ftilt"
    assert get_real_move_name("forwardssmashdown") == "fsmash"
    assert get_real_move_name("fhoaiuwhfawo eiofew") == ""
