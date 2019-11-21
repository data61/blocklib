from blocklib import PPRLIndex
import numpy as np

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


def test_select_reference_value():
    """Test selection of reference value."""
    reference_config = {
        "blocking-features": [1, 2],
        "random-state": 0,
        "num-reference-values": 3
    }
    reference_data = [
        (1, 'Joyce', 'Wang'),
        (2, 'Jone', 'White'),
        (3, 'Fred', 'Yu'),
        (4, 'Lindsay', 'Lin'),
        (5, 'Evelyn', 'Lai')
    ]
    pprl = PPRLIndex()
    ref_val_list = pprl.select_reference_value(reference_data, reference_config)
    index = np.random.RandomState(0).choice(range(len(reference_data)), 3, replace=False)
    expected = [reference_data[x][1] + reference_data[x][2] for x in index]
    assert ref_val_list == expected