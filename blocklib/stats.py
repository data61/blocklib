import statistics
from typing import Sequence, Dict, List, Any


def reversed_index_per_strategy_stats(reversed_index_per_strategy: Sequence[Dict[str, List[Any]]], num_elements: int):
    strat_stats = []
    for i, reversed_index in enumerate(reversed_index_per_strategy):
        stats = reversed_index_stats(reversed_index)
        stats['strategy_idx'] = i
        _add_coverage_to_stats_per_stragegy(stats, num_elements)
        strat_stats.append(stats)
    return strat_stats


def _add_coverage_to_stats_per_stragegy(stats: Dict, num_elements: int):
    # shortcut, as each element can only be part of one block, we can just use the sum of the blocks
    stats['num_filtered_elements'] = num_elements - stats['sum_of_blocks']
    stats['coverage'] = 0 if stats['sum_of_blocks'] == 0 else stats['sum_of_blocks'] / num_elements


def reversed_index_stats(reversed_index: Dict[str, List[Any]]):
    lengths = [len(rv) for rv in reversed_index.values()]
    stats = {
        'num_of_blocks': len(lengths),
        'min_size': 0 if len(lengths) == 0 else min(lengths),
        'max_size': 0 if len(lengths) == 0 else max(lengths),
        'avg_size': 0 if len(lengths) == 0 else statistics.mean(lengths),
        'med_size': 0 if len(lengths) == 0 else int(statistics.median(lengths)),
        'std_size': 0 if 0 <= len(lengths) <= 1 else statistics.stdev(lengths),
        'sum_of_blocks': sum(lengths)
    }
    return stats
