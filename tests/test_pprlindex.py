from blocklib import PPRLIndex


def test_init():
    """Test constructor for base class PPRLIndex."""
    pprl = PPRLIndex()

    assert pprl.rec_dict is None
    assert pprl.ent_id_col is None
    assert pprl.rec_id_col is None
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
    # We are re-ordering the blocks length here as the method returns [2, 1, 3] with Python 3.5 instead of [3, 2, 1]
    # in all other Python versions. This may be due to the fact that from Python3.6, the dictionaries have been updated
    # to be ordered. https://stackoverflow.com/questions/39980323/are-dictionaries-ordered-in-python-3-6
    length_of_blocks = stats['len_of_blocks']
    length_of_blocks.sort()
    assert length_of_blocks == [1, 2, 3]
    assert stats['min_size'] == 1
    assert stats['max_size'] == 3
    assert stats['avg_size'] == 2
    assert stats['med_size'] == 2
    # Same comment as the block length.
    num_of_blocks_per_rec = stats['num_of_blocks_per_rec']
    num_of_blocks_per_rec.sort()
    assert num_of_blocks_per_rec == [1, 1, 1, 1, 2]
