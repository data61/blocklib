import time
import pytest
from blocklib.simmeasure import EditSim, DiceSim

def test_editsim():
    """Test Edit similarity measure."""
    # with minimum threshold
    sim = EditSim(dict(min_threshold=0.9))
    # Joyce and Joycee w is calculated as 1 - 1/6 < 0.9 -> score is 0
    score = sim.sim('Joyce', 'Joycee')
    assert score == 0

    assert sim.sim('Joyce', 'Joyce') == 1

    # test invalid threshold
    with pytest.raises(ValueError) as e:
        sim = EditSim(dict(min_threshold=1.1))
        sim.sim('Joyce', 'Joycee')
        assert e == 'Illegal value for minimum threshold (not between 0 and 1): 1.1'

    # test corner case
    score = sim.sim('', '')
    assert score == 0

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

    # check exactly same
    score = sim.sim('Joyce', 'Joyce')
    assert score == 1.0

    # check using cache
    start = time.time()
    score1 = sim.sim('Joyce is a girl', 'Joyce is a gril', cache=True)
    time1 = time.time() - start
    start = time.time()
    score2 = sim.sim('Joyce is a girl', 'Joyce is a gril', cache=True)
    time2 = time.time() - start
    assert time1 > time2
    # dice similarity should give higher score since it is based on bi-gram
    s1 = 'JoJo isis'
    s2 = 'Jo is'
    score_dice = sim.sim(s1, s2, cache=True)
    score_edit = EditSim({}).sim(s1, s2)
    assert score_dice > score_edit