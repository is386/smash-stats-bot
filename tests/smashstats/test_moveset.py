from smashstats.moveset import get_all_similar, split_char_move


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
