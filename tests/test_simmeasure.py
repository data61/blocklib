from blocklib.simmeasure import EditSim, DiceSim

def test_editsim():
    """Test Edit similarity measure."""
    # with minimum threshold
    sim = EditSim(dict(min_threshold=0.9))
    score = sim.sim('Joyce', 'Joyce')
    assert score == 1

    # without minimum threshold
    sim = EditSim({})
    score1 = sim.sim('Joyce', 'Joyyce')
    score2 = sim.sim('Joyce', 'Jyoce')

    # Pair (Joyce, Joyyce) only need 1 deletion while Pair (Joyce, Jyoce) needs 2 substitution
    assert score1 > score2


def test_dicesim():
    """Test Dice similarity measure."""
    config = dict(ngram_len=2, ngram_padding=1, padding_start_char='a', padding_end_char='z')
    sim = DiceSim(config)

    # dice similarity should give higher score since it is based on bi-gram
    s1 = 'JoJo isis'
    s2 = 'Jo is'
    score_dice = sim.sim(s1, s2, cache=True)
    score_edit = EditSim({}).sim(s1, s2)
    assert score_dice > score_edit