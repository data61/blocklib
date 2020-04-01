from blocklib.stats import reversed_index_per_strategy_stats, reversed_index_stats


def test_reversed_index_per_strategy_stats_empty():
    # empty
    reversed_index_per_strategy = [{}, {}]
    stats = reversed_index_per_strategy_stats(reversed_index_per_strategy, 0)
    for stat in stats:
        for k, val in stat.items():
            if not k == 'strategy_idx':
                assert val == 0


def test_reversed_index_stats():
    reversed_index = {'one': [1], 'two': [1, 2], 'three': [1, 2, 3, 4, 5, 6, 7]}
    stats = reversed_index_stats(reversed_index)
    assert stats['num_of_blocks'] == 3
    assert stats['min_size'] == 1
    assert stats['max_size'] == 7
    assert stats['med_size'] == 2
    assert stats['avg_size'] == 10/3
    assert stats['sum_of_blocks'] == 10

