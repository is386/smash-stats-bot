from smashstats.translator import trans


def test_trans():
    # SmashStats says Trans Rights
    assert len(trans("mario", "synonyms/characters.yml")) == 3
    assert len(trans("rob", "synonyms/characters.yml")) == 3
    assert len(trans("mrgameandwatch", "synonyms/characters.yml")) == 1
    assert len(trans("bowser", "synonyms/characters.yml")) == 2
    assert len(trans("bowserjr", "synonyms/characters.yml")) == 1
