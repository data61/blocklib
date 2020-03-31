import statistics
from typing import Sequence, Dict, List, Any


def reversed_index_per_strategy_stats(reversed_index_per_strategy: Sequence[Dict[str, List[Any]]], num_elements: int):
    strat_stats = []
    for i, reversed_index in enumerate(reversed_index_per_strategy):
        stats = reversed_index_stats(reversed_index, num_elements)
        stats['strategy_idx'] = i
        strat_stats.append(stats)
    return strat_stats


def reversed_index_stats(reversed_index: Dict[str, List[Any]], num_elements: int):
    lengths = [len(rv) for rv in reversed_index.values()]
    stats = {
        'num_of_blocks': len(lengths),
        'min_size': 0 if len(lengths) == 0 else min(lengths),
        'max_size': 0 if len(lengths) == 0 else max(lengths),
        'avg_size': 0 if len(lengths) == 0 else int(statistics.mean(lengths)),
        'med_size': 0 if len(lengths) == 0 else int(statistics.median(lengths)),
        'std_size': 0 if len(lengths) == 0 else statistics.stdev(lengths),
        'num_filtered_elements': num_elements - sum(lengths),
        'coverage': 0 if len(lengths) == 0 else sum(lengths) / num_elements}
    return stats
