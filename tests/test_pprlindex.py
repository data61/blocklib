from blocklib import PPRLIndex
from blocklib.stats import reversed_index_stats
import random


def test_init(valid_psig_config):
    """Test constructor for base class PPRLIndex."""
    pprl = PPRLIndex(config=valid_psig_config)

    assert pprl.rec_dict is None
    assert pprl.ent_id_col is None
    assert pprl.rec_id_col is None


def test_summarize_reversed_index(valid_psig_config):
    """Test summarize_reversed_index for base class PPRLIndex."""
    pprl = PPRLIndex(config=valid_psig_config)

    reversed_index = {
        'Jo': ['id1', 'id2', 'id3'],
        'Fr': ['id2', 'id4'],
        'Li': ['id5']
    }

    stats = reversed_index_stats(reversed_index)
    assert stats['num_of_blocks'] == 3
    assert stats['min_size'] == 1
    assert stats['max_size'] == 3
    assert stats['avg_size'] == 2
    assert stats['med_size'] == 2


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

    ref_val_list = PPRLIndex.select_reference_value(reference_data, reference_config)
    combined = [reference_data[i][1] + reference_data[i][2] for i in range(len(reference_data))]
    random.seed(0)
    expected = random.sample(combined, 3)
    assert ref_val_list == expected


def test_get_feature_to_index_map(valid_psig_config):
    pprl = PPRLIndex(config=valid_psig_config)
    pprl.blocking_features = ['boo']
    assert pprl.get_feature_to_index_map([]) is None
