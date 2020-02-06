import pytest

from smashstats.moveset import get_all_similar, split_char_move, get_character, get_real_move_name


# TODO: either make get_move_data() not depend from ctx or split it up more so we can make a test


def test_get_all_similar():
    assert len(get_all_similar("synonyms/characters.yml", "banjo")) == 4


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


def test_get_character():
    assert get_character("mario") == mario_char_data
    with pytest.raises(FileNotFoundError):
        get_character("fhaubfhaiwfbwa")


def test_get_real_move_name():
    assert get_real_move_name("forwardtilt", mario_char_data) == "ftilt"
    assert get_real_move_name(
        "forwardssmashdown", mario_char_data) == "fsmash"
    assert get_real_move_name("fhoaiuwhfawo eiofew", mario_char_data) == ""


# Cannot test parse_move_selection due to its dependency to user input in Discord

# Collapse this pls
mario_char_data = {
    'airdodge1': {'fields': None, 'title': 'Airdodge'},
    'bair1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioBAir.gif', 'title': 'Back Air'},
    'bthrow1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioBThrow.gif', 'title': 'Back Throw'},
    'dair1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDAir.gif', 'title': 'Down Air (Normal)'},
    'dair2': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDAirLanding.gif', 'title': 'Down Air (Landing)'},
    'dashattack1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDashAttack.gif', 'title': 'Dash Attack'},
    'dsmash1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDSmash.gif', 'title': 'Down Smash'},
    'dspecial1': {'fields': None, 'title': 'F.L.U.D.D.'},
    'dspecial2': {'fields': None, 'title': 'F.L.U.D.D. (Max)'},
    'dtaunt1': {'title': 'Down Taunt'},
    'dthrow1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDThrow.gif', 'title': 'Down Throw'},
    'dtilt1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDTilt.gif', 'title': 'Down Tilt'},
    'fair1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFAir.gif', 'title': 'Forward Air'},
    'fsmash1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmash.gif', 'title': 'Forward Smash'},
    'fsmash2': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmashDown.gif', 'title': 'Forward Smash Down'},
    'fsmash3': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmashUp.gif', 'title': 'Forward Smash Up'},
    'fthrow1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFThrow.gif', 'title': 'Forward Throw'},
    'ftilt1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTilt.gif', 'title': 'Forward Tilt'},
    'ftilt2': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTiltDown.gif', 'title': 'Forward Tilt Down'},
    'ftilt3': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTiltUp.gif', 'title': 'Forward Tilt Up'},
    'getupattack1': {'fields': None, 'title': 'Getup Attack'},
    'grabdash1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDashGrab.gif', 'title': 'Dash Grab'},
    'grabpivot1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioPivotGrab.gif', 'title': 'Pivot Grab'},
    'grabstanding1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioGrab.gif', 'title': 'Standing Grab'},
    'jab1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab1.gif', 'title': 'Jab 1'},
    'jab2': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab2.gif', 'title': 'Jab 2'},
    'jab3': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab3.gif', 'title': 'Jab 3'},
    'ledgeattack1': {'fields': None, 'title': 'Ledge Attack'},
    'mario1': {'fields': None, 'image': 'hurtbox.png', 'title': 'Mario'},
    'nair1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioNAir.gif', 'title': 'Neutral Air'},
    'nspecial1': {'fields': None, 'title': 'Fireball'}, 'oos1': {'fields': None, 'title': 'Out of Shield Options'},
    'pummel1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioPummel.gif', 'title': 'Pummel'},
    'roll1': {'fields': None, 'title': 'Rolls'}, 'spotdodge1': {'fields': None, 'title': 'Spot Dodge'},
    'sspecial1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioCape.gif', 'title': 'Cape'},
    'staunt1': {'title': 'Side Taunt'}, 'tripattack1': {'fields': None, 'title': 'Trip Getup Attack'},
    'uair1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUAir.gif', 'title': 'Up Air'},
    'usmash1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUSmash.gif', 'title': 'Up Smash'},
    'uspecial1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioSuperJumpPunch.gif', 'title': 'Super Jump Punch'},
    'utaunt1': {'title': 'Up Taunt'}, 'uthrow1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUThrow.gif', 'title': 'Up Throw'},
    'utilt1': {'fields': None, 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUTilt.gif', 'title': 'Up Tilt'}}
