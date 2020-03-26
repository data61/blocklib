import statistics
from collections import defaultdict
from typing import Dict, List, Sequence, Any

import numpy as np

from .configuration import get_config
from .encoding import flip_bloom_filter
from .pprlindex import PPRLIndex
from .signature_generator import generate_signatures


class PPRLIndexPSignature(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        Reference scalability entity resolution using probability signatures
        on parallel databases.

        This class includes an implementation of p-sig algorithm.
    """

    def __init__(self, config: Dict) -> None:
        """Initialize the class and set the required parameters.

        Arguments:
        - config: dict
            Configuration for P-Sig reverted index.

        """
        super().__init__()
        self.filter_config = get_config(config, "filter")
        self.blocking_config = get_config(config, "blocking-filter")
        self.signature_strategies = get_config(config, 'signatureSpecs')
        self.rec_id_col = config.get("record-id-col", None)

    def build_reversed_index(self, data: Sequence[Sequence], verbose: bool = False):
        """Build inverted index given P-Sig method."""

        # Build index of records
        if self.rec_id_col is None:
            record_ids = np.arange(len(data))
        else:
            record_ids = [x[self.rec_id_col] for x in data]

        reversed_index_per_strategy = \
            [defaultdict(list) for _ in range(len(self.signature_strategies))]  # type: List[Dict[str, List[Any]]]
        # Build inverted index
        # {signature -> record ids}
        for rec_id, dtuple in zip(record_ids, data):

            signatures = generate_signatures(self.signature_strategies, dtuple)

            for i, signature in enumerate(signatures):
                reversed_index_per_strategy[i][signature].append(rec_id)

        n = len(data)
        reversed_index_per_strategy = [self.filter_reversed_index(data, reversed_index) for reversed_index in
                                       reversed_index_per_strategy]
        if verbose:
            strat_stats = self.compute_strategies_stats(reversed_index_per_strategy, n)
            print("Statistics for the individual strategies:")
            for strat_stat in strat_stats:
                print(f'Strategy {strat_stat["strategy_idx"]}:')
                print(f'\tblock size {strat_stat["min_size"]} min, {strat_stat["max_size"]} max, '
                      + f'{strat_stat["avg_size"]:.2f} avg, {strat_stat["med_size"]} median, '
                      + f'{strat_stat["std_size"]:.2f} std')
                print(f'\t {strat_stat["num_of_blocks"]} blocks, {strat_stat["num_filtered_elements"]} filtered '
                      + f'elements, {(strat_stat["coverage"] * 100):.2f}% coverage')

        # combine the reversed indices into one
        filtered_reversed_index = reversed_index_per_strategy[0]
        for rev_idx in reversed_index_per_strategy[1:]:
            filtered_reversed_index.update(rev_idx)

        # check if final inverted index is empty
        if len(filtered_reversed_index) == 0:
            raise ValueError('P-Sig: All records are filtered out!')
        # map signatures in reversed_index into bloom filter
        num_hash_func = int(self.blocking_config.get("number-hash-functions", None))
        bf_len = int(self.blocking_config.get("bf-len", None))

        reversed_index = {}  # type: Dict[Any, List[Any]]

        for signature, rec_ids in filtered_reversed_index.items():
            bf_set = tuple(flip_bloom_filter(signature, bf_len, num_hash_func))
            if bf_set in reversed_index:
                reversed_index[bf_set].extend(rec_ids)
            else:
                reversed_index[bf_set] = rec_ids

        return reversed_index

    def compute_strategies_stats(self, reversed_index_per_strategy: Sequence[Dict[str, List[Any]]], num_elements: int):
        strat_stats = []
        for i, reversed_index in enumerate(reversed_index_per_strategy):
            lengths = [len(rv) for rv in reversed_index.values()]
            stats = {
                'strategy_idx': i,
                'num_of_blocks': len(lengths),
                'min_size': min(lengths),
                'max_size': max(lengths),
                'avg_size': int(statistics.mean(lengths)),
                'med_size': int(statistics.median(lengths)),
                'std_size': statistics.stdev(lengths),
                'num_filtered_elements': num_elements - sum(lengths),
                'coverage': sum(lengths) / num_elements}
            strat_stats.append(stats)
        return strat_stats

    def filter_reversed_index(self, data: Sequence[Sequence], reversed_index: Dict):
        # Filter inverted index based on ratio
        n = len(data)

        # filter blocks based on filter type
        filter_type = get_config(self.filter_config, "type")
        if filter_type == "ratio":
            min_occur_ratio = get_config(self.filter_config, 'min')
            max_occur_ratio = get_config(self.filter_config, 'max')
            reversed_index = {k: v for k, v in reversed_index.items() if n * max_occur_ratio > len(v) > n * min_occur_ratio}
        elif filter_type == "count":
            min_occur_count = get_config(self.filter_config, "min")
            max_occur_count = get_config(self.filter_config, "max")
            reversed_index = {k: v for k, v in reversed_index.items() if max_occur_count > len(v) > min_occur_count}
        else:
            raise NotImplementedError("Don't support {} filter yet.".format(filter_type))

        return reversed_index
