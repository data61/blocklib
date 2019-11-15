from blocklib import PPRLIndex


def test_init():
    """Test constructor for base class PPRLIndex."""
    pprl = PPRLIndex()

    assert pprl.rec_dict is None
    assert pprl.ent_id_col is None
    assert pprl.rec_id_col is None
    assert pprl.revert_index == {}
    assert pprl.stats == {}


def test_summarize_reversed_index():
    """Test summarize_reversed_index for base class PPRLIndex."""
    pprl = PPRLIndex()

    reversed_index = {
        'Jo': ['id1', 'id2', 'id3'],
        'Fr': ['id2', 'id4'],
        'Li': ['id5']
    }

    stats = pprl.summarize_reversed_index(reversed_index)
    assert stats['num_of_blocks'] == 3
    assert stats['len_of_blocks'] == [3, 2, 1]
    assert stats['min_size'] == 1
    assert stats['max_size'] == 3
    assert stats['avg_size'] == 2
    assert stats['med_size'] == 2
    assert stats['num_of_blocks_per_rec'] == [1, 2, 1, 1, 1]
