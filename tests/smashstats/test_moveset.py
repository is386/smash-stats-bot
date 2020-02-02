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
    msg = "?viz dr mario nair".split()
    char, move = split_char_move(msg[1:])
    assert char == "drmario" and move == "nair"


def test_get_character():
    assert get_character("mario") == mario_char_data
    with pytest.raises(FileNotFoundError):
        get_character("fhaubfhaiwfbwa")


def test_get_real_move_name():
    assert get_real_move_name("forwardtilt", mario_char_data) == "ftilt"
    assert get_real_move_name("forwardssmashdown", mario_char_data) == "fsmash"
    assert get_real_move_name("fhoaiuwhfawo eiofew", mario_char_data) == ""


# Cannot test parse_move_selection due to its dependency to user input in Discord

# Collapse this pls
mario_char_data = {'mario': {'title': 'Mario', 'image': 'hurtbox.png', 'fields': None},
                   'airdodge': {'title': 'Airdodge', 'fields': None}, 'bair': {'title': 'Back Air',
                                                                               'image': 'https://ultimateframedata.com/hitboxes/mario/MarioBAir.gif',
                                                                               'fields': None},
                   'bthrow': {'title': 'Back Throw',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioBThrow.gif',
                              'fields': None}, 'dair': {'title': 'Down Air (Normal)',
                                                        'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDAir.gif',
                                                        'fields': None},
                   'dair2': {'title': 'Down Air (Landing)',
                             'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDAirLanding.gif',
                             'fields': None}, 'dashattack': {'title': 'Dash Attack',
                                                             'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDashAttack.gif',
                                                             'fields': None},
                   'dsmash': {'title': 'Down Smash',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDSmash.gif',
                              'fields': None}, 'dtaunt': {'title': 'Down Taunt'},
                   'dthrow': {'title': 'Down Throw',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDThrow.gif',
                              'fields': None}, 'dtilt': {'title': 'Down Tilt',
                                                         'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDTilt.gif',
                                                         'fields': None},
                   'fair': {'title': 'Forward Air',
                            'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFAir.gif',
                            'fields': None}, 'fsmash': {'title': 'Forward Smash',
                                                        'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmash.gif',
                                                        'fields': None},
                   'fsmash2': {'title': 'Forward Smash Down',
                               'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmashDown.gif',
                               'fields': None}, 'fsmash3': {'title': 'Forward Smash Up',
                                                            'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFSmashUp.gif',
                                                            'fields': None},
                   'fthrow': {'title': 'Forward Throw',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFThrow.gif',
                              'fields': None}, 'ftilt': {'title': 'Forward Tilt',
                                                         'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTilt.gif',
                                                         'fields': None},
                   'ftilt2': {'title': 'Forward Tilt Down',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTiltDown.gif',
                              'fields': None}, 'ftilt3': {'title': 'Forward Tilt Up',
                                                          'image': 'https://ultimateframedata.com/hitboxes/mario/MarioFTiltUp.gif',
                                                          'fields': None},
                   'getupattack': {'title': 'Getup Attack', 'fields': None},
                   'grabdash': {'title': 'Dash Grab',
                                'image': 'https://ultimateframedata.com/hitboxes/mario/MarioDashGrab.gif',
                                'fields': None}, 'grabpivot': {'title': 'Pivot Grab',
                                                               'image': 'https://ultimateframedata.com/hitboxes/mario/MarioPivotGrab.gif',
                                                               'fields': None},
                   'grabstanding': {'title': 'Standing Grab',
                                    'image': 'https://ultimateframedata.com/hitboxes/mario/MarioGrab.gif',
                                    'fields': None}, 'jab': {'title': 'Jab 1',
                                                             'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab1.gif',
                                                             'fields': None},
                   'jab2': {'title': 'Jab 2',
                            'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab2.gif',
                            'fields': None}, 'jab3': {'title': 'Jab 3',
                                                      'image': 'https://ultimateframedata.com/hitboxes/mario/MarioJab3.gif',
                                                      'fields': None},
                   'ledgeattack': {'title': 'Ledge Attack', 'fields': None},
                   'nair': {'title': 'Neutral Air',
                            'image': 'https://ultimateframedata.com/hitboxes/mario/MarioNAir.gif',
                            'fields': None},
                   'oos': {'title': 'Out of Shield Options', 'fields': None},
                   'nspecial': {'title': 'Fireball', 'fields': None}, 'pummel': {'title': 'Pummel',
                                                                                 'image': 'https://ultimateframedata.com/hitboxes/mario/MarioPummel.gif',
                                                                                 'fields': None},
                   'roll': {'title': 'Rolls', 'fields': None},
                   'dspecial': {'title': 'F.L.U.D.D.', 'fields': None},
                   'dspecial2': {'title': 'F.L.U.D.D. (Max)', 'fields': None},
                   'spotdodge': {'title': 'Spot Dodge', 'fields': None},
                   'sspecial': {'title': 'Cape',
                                'image': 'https://ultimateframedata.com/hitboxes/mario/MarioCape.gif',
                                'fields': None}, 'staunt': {'title': 'Side Taunt'},
                   'tripattack': {'title': 'Trip Getup Attack', 'fields': None},
                   'uair': {'title': 'Up Air',
                            'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUAir.gif',
                            'fields': None}, 'uspecial': {'title': 'Super Jump Punch',
                                                          'image': 'https://ultimateframedata.com/hitboxes/mario/MarioSuperJumpPunch.gif',
                                                          'fields': None},
                   'usmash': {'title': 'Up Smash',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUSmash.gif',
                              'fields': None}, 'utaunt': {'title': 'Up Taunt'},
                   'uthrow': {'title': 'Up Throw',
                              'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUThrow.gif',
                              'fields': None}, 'utilt': {'title': 'Up Tilt',
                                                         'image': 'https://ultimateframedata.com/hitboxes/mario/MarioUTilt.gif',
                                                         'fields': None}}
