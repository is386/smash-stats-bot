import pytest

from smashstats import move_model
from smashstats.moveset import (MoveLookupError, character_choices,
                                find_character, get_move_data, move_choices,
                                normalize, parse_move, resolve_character,
                                resolve_moves, sort_moves, translate_move,
                                with_frame_data, with_hitboxes)


def test_normalize():
    assert normalize("Bowser Jr.") == "bowserjr"
    assert normalize("Banjo & Kazooie") == "banjokazooie"
    assert normalize("forward-tilt") == "forwardtilt"
    assert normalize("  ") == ""


def test_find_character():
    # Exact code names.
    assert find_character("wolf") == "wolf"
    assert find_character("bowser jr") == "bowserjr"
    assert find_character("king k rool") == "kingkrool"

    # Synonyms.
    assert find_character("banjo and kazooie") == "banjo"
    assert find_character("kazooie") == "banjo"

    # An exact match must win over a longer substring match.
    assert find_character("mario") == "mario"
    assert find_character("drmario") == "drmario"
    assert find_character("dr. mario") == "drmario"
    assert find_character("rob") == "rob"
    assert find_character("robin") == "robin"

    # Misses.
    assert find_character("iohioehgioaeig") == ""
    assert find_character("") == ""


def test_resolve_character():
    assert resolve_character("Banjo & Kazooie") == "banjo"

    with pytest.raises(MoveLookupError):
        resolve_character("iohioehgioaeig")


def test_resolve_moves_single():
    assert resolve_moves("banjo", "nair") == ["nair1"]
    assert resolve_moves("banjo", "neutral air") == ["nair1"]
    assert resolve_moves("banjo", "nspecial2") == ["nspecial2"]
    # A code name straight from the autocomplete list.
    assert resolve_moves("banjo", "nair1") == ["nair1"]
    # A move synonym that only the synonyms db knows.
    assert resolve_moves("mario", "fireball") == ["nspecial1"]


def test_resolve_moves_multiple():
    assert resolve_moves("banjo", "dair") == ["dair1", "dair2"]
    assert resolve_moves("banjo", "forward tilt") == ["ftilt1", "ftilt2", "ftilt3"]

    # Min Min's back air reuses her forward air data.
    assert resolve_moves("minmin", "bair") == resolve_moves("minmin", "fair")

    # Hero has 22 down specials. The old reaction picker capped out at 16 and
    # refused them; a select menu holds 25.
    hero_dspecials = resolve_moves("hero", "dspecial")
    assert len(hero_dspecials) == 22
    assert hero_dspecials[:3] == ["dspecial1", "dspecial2", "dspecial3"]


def test_resolve_moves_errors():
    with pytest.raises(MoveLookupError):
        resolve_moves("banjo", "iohioehgioaeig")

    with pytest.raises(MoveLookupError):
        resolve_moves("banjo", "nspecial6")

    with pytest.raises(MoveLookupError):
        resolve_moves("banjo", "   ")


def test_sort_moves():
    # Trailing numbers sort numerically, not as text.
    assert sort_moves(["nair11", "nair2", "nair12", "nair4"]) == [
        "nair2", "nair4", "nair11", "nair12"]
    assert sort_moves(["uair1", "jab2", "jab1"]) == ["jab1", "jab2", "uair1"]


def test_parse_move():
    assert parse_move("nair", "banjo") == "nair"
    assert parse_move("neutralair", "banjo") == "nair"
    assert parse_move("nspecial1", "banjo") == "nspecial1"
    assert parse_move("nspecial2", "banjo") == "nspecial2"
    assert parse_move("nspecial6", "banjo") == ""
    assert parse_move("iohioehgioaeig", "banjo") == ""


def test_translate_move():
    assert translate_move("forwardtilt", "banjo") == "ftilt"
    assert translate_move("forwardssmashdown", "banjo") == "fsmash"
    assert translate_move("fireball", "mario") == "nspecial1"
    assert translate_move("fhoaiuwhfawo eiofew", "banjo") == ""


def test_with_hitboxes():
    assert with_hitboxes("banjo", ["nair1"]) == ["nair1"]
    # Air dodges have a row but no gif.
    assert with_hitboxes("banjo", ["airdodge1"]) == []
    assert with_hitboxes("banjo", ["nair1", "airdodge1"]) == ["nair1"]
    assert with_hitboxes("banjo", ["iohioehgioaeig"]) == []


def test_with_frame_data():
    assert with_frame_data("banjo", ["nair1"]) == ["nair1"]
    # Two of hero's 22 down specials have a gif but no numbers.
    assert with_frame_data("hero", ["dspecial16", "dspecial17"]) == []
    assert with_frame_data("hero", ["dspecial1", "dspecial16"]) == ["dspecial1"]
    assert with_frame_data("banjo", ["iohioehgioaeig"]) == []


def test_character_choices():
    # An empty query offers a starting list.
    assert len(character_choices("")) == 25

    choices = character_choices("mario")
    assert "mario" in choices and "drmario" in choices
    # The exact match ranks first.
    assert choices[0] == "mario"

    assert character_choices("iohioehgioaeig") == []
    assert len(character_choices("")) <= 25


def test_move_choices():
    choices = move_choices("banjo", "")
    assert len(choices) <= 25
    labels = [label for label, _ in choices]
    values = [value for _, value in choices]
    # Moveset order, so an untyped list opens on jab rather than on airdodges.
    assert values[0] == "jab1"
    assert labels[0] == "Jab 1 (jab1)"
    assert "airdodge1" not in values

    # Searchable by title as well as by code name.
    assert ("Neutral Air (nair1)", "nair1") in move_choices("banjo", "neutral")
    assert ("Neutral Air (nair1)", "nair1") in move_choices("banjo", "nair")

    assert move_choices("banjo", "iohioehgioaeig") == []


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
