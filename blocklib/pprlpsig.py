import logging
from collections import defaultdict
from typing import Dict, List, Sequence, Any, Optional, Union, cast

from .encoding import flip_bloom_filter
from .pprlindex import PPRLIndex, ReversedIndexResult
from .signature_generator import generate_signatures
from .stats import reversed_index_per_strategy_stats, reversed_index_stats
from .validation import PSigConfig


class PPRLIndexPSignature(PPRLIndex):
    """Class that implements the PPRL indexing technique:

    Reference scalability entity resolution using probability signatures
    on parallel databases.

    This class includes an implementation of p-sig algorithm.
    """

    def __init__(self, config: Union[PSigConfig, Dict]) -> None:
        """Initialize the class and set the required parameters.

        Arguments:
        - config: Configuration for P-Sig reverted index.

        """

        if isinstance(config, dict):
            config = PSigConfig.parse_obj(config)
        config = cast(PSigConfig, config)
        super().__init__(config)
        self.blocking_features = config.blocking_features
        self.filter_config = config.filter
        self.blocking_config = config.blocking_filter
        self.signature_strategies = config.signatures
        self.rec_id_col = config.record_id_column

    def build_reversed_index(self, data: Sequence[Sequence], header: Optional[List[str]] = None):
        """Build inverted index given P-Sig method.

        """
        feature_to_index = self.get_feature_to_index_map(data, header)
        self.set_blocking_features_index(self.blocking_features, feature_to_index)

        # Build index of records
        if self.rec_id_col is None:
            record_ids = list(range(len(data)))
        else:
            record_ids = [x[self.rec_id_col] for x in data]

        reversed_index_per_strategy = \
            [defaultdict(list) for _ in range(len(self.signature_strategies))]  # type: List[Dict[str, List[Any]]]
        # Build inverted index
        # {signature -> record ids}
        for rec_id, dtuple in zip(record_ids, data):

            signatures = generate_signatures(self.signature_strategies, dtuple, feature_to_index)

            for i, signature in enumerate(signatures):
                reversed_index_per_strategy[i][signature].append(rec_id)

        reversed_index_per_strategy = [self.filter_reversed_index(data, reversed_index) for reversed_index in
                                       reversed_index_per_strategy]
        # somehow the reversed_index of the first strategy gets overwritten in the next step. Thus, we generate the
        # statistics of the different strategies first.
        strategy_stats = reversed_index_per_strategy_stats(reversed_index_per_strategy, len(data))
        # combine the reversed indices into one
        filtered_reversed_index = reversed_index_per_strategy[0]
        for rev_idx in reversed_index_per_strategy[1:]:
            filtered_reversed_index.update(rev_idx)

        # check if final inverted index is empty
        if len(filtered_reversed_index) == 0:
            raise ValueError('P-Sig: All records are filtered out!')

        # compute coverage information
        entities = set()
        for recids in filtered_reversed_index.values():
            for rid in recids:
                entities.add(rid)
        coverage = len(entities) / len(record_ids)
        if coverage < 1:
            logging.warning(
                f'The P-Sig configuration leads to incomplete coverage ({round(coverage * 100, 2)}%)!\n'
                f'This means that not all records are part of at least one block. You can increase coverage by '
                f'adjusting the filter to be less aggressive or by finding signatures that produce smaller block sizes.'
            )

        # map signatures in reversed_index into bloom filter
        num_hash_func = self.blocking_config.number_of_hash_functions
        bf_len = self.blocking_config.bloom_filter_length

        reversed_index = {}  # type: Dict[str, List[Any]]

        for signature, rec_ids in filtered_reversed_index.items():
            bf_set = str(tuple(flip_bloom_filter(signature, bf_len, num_hash_func)))
            if bf_set in reversed_index:
                reversed_index[bf_set].extend(rec_ids)
            else:
                reversed_index[bf_set] = rec_ids

        # create some statistics around the blocking results
        stats = reversed_index_stats(reversed_index)
        stats['statistics_per_strategy'] = strategy_stats
        stats['coverage'] = coverage
        return ReversedIndexResult(reversed_index, stats)

    def filter_reversed_index(self, data: Sequence[Sequence], reversed_index: Dict):
        # Filter inverted index based on ratio
        n = len(data)

        # filter blocks based on filter type
        filter_type = self.filter_config.type
        if filter_type == "ratio":
            min_occur_ratio = self.filter_config.min
            max_occur_ratio = self.filter_config.max
            reversed_index = {k: v for k, v in reversed_index.items() if n * max_occur_ratio > len(v) > n * min_occur_ratio}
        elif filter_type == "count":
            min_occur_count = self.filter_config.min
            max_occur_count = self.filter_config.max
            reversed_index = {k: v for k, v in reversed_index.items() if max_occur_count > len(v) > min_occur_count}
        else:
            raise NotImplementedError("Don't support {} filter yet.".format(filter_type))

        return reversed_index
