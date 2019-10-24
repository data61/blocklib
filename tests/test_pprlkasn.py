"""Test class PPRLIndexKAnonymousSortedNeighbour"""

from blocklib import PPRLIndexKAnonymousSortedNeighbour


def test_kasn():
    """Test KASN based on SIM."""
    config = {
        'k': 100,
        'sim_measure': {'algorithm': 'Dice',
                        'ngram_len': '2',
                        'ngram_padding': True,
                        'padding_start_char': chr(1),
                        'padding_end_char': chr(2)},
        'min_sim_threshold': 0.8,
        'overlap': 0.0,
        'sim_or_size': 'SIM',
        'default_features': [1, 2],
        'sorted_first_val': chr(1),
        'ref_data_config': {'path': 'datasets/4611_50_overlap_no_mod_alice.csv',
                            'header_line': True,
                            'default_features': [1, 2],
                            'num_vals': 40,
                            'random_seed': 42}
    }
    snn_sim = PPRLIndexKAnonymousSortedNeighbour(config)
    data = snn_sim.__read_csv_gz_file__('datasets/4611_50_overlap_no_mod_bob.csv',
                                        header_line=False, rec_id_col=0)
    snn_sim.build_inverted_index(data)

    # test SIZE based
    config['sim_or_size'] = 'SIZE'
    snn_size = PPRLIndexKAnonymousSortedNeighbour(config)
    snn_size.build_inverted_index(data) 
