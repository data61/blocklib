from blocklib.simmeasure import EditSim, DiceSim


def test_editsim():
    """Test Edit similarity measure."""
    # with minimum threshold
    sim = EditSim(dict(min_threshold=0.9))
    score = sim.sim('Joyce', 'Joyce')
    assert score == 1

    # without minimum threshold
    sim = EditSim({})
    score = sim.sim('Joyce', 'Jone')
    assert score > 0


def test_dicesim():
    """Test Dice similarity measure."""
    config = dict(ngram_len=2, ngram_padding=1, padding_start_char='a', padding_end_char='z')
    sim = DiceSim(config)

    score = sim.sim('Joyce wears a T-shrt today', 'Jayce wear an T-shrt today', cache=True)
    assert score > 0.8