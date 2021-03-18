import random

from collections import defaultdict
from typing import Dict, Sequence, Any, List, Optional, Union, cast

from .pprlindex import PPRLIndex, ReversedIndexResult
from .encoding import generate_bloom_filter
from .utils import deserialize_filters
from .stats import reversed_index_stats
from .validation import LambdaConfig


class PPRLIndexLambdaFold(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        An LSH-Based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage.

        This class includes an implementation of Lambda-fold redundant blocking method.
    """

    def __init__(self, config: Union[LambdaConfig, Dict]):
        """Initialize the class and set the required parameters.

        :param config: Configuration for P-Sig reverted index.
        """

        if isinstance(config, dict):
            config = LambdaConfig.parse_obj(config)
        config = cast(LambdaConfig, config)
        super().__init__(config)
        self.blocking_features = config.blocking_features
        # Lambda: number of redundant tables
        self.mylambda = config.Lambda
        self.bf_len = config.bloom_filter_length
        self.num_hash_function = config.number_of_hash_functions
        # K: number of base Hamming LSH hashing functions
        self.K = config.K
        self.input_clks = config.block_encodings
        self.random_state = config.random_state
        self.record_id_col = config.record_id_column

    def __record_to_bf__(self, record: Sequence, blocking_features_index: List[int]):
        """Convert a record to list of bigrams and then map to a bloom filter."""
        s = ''.join([record[i] for i in blocking_features_index])
        # generate list of bigram of s. hash each bigram to position of bit 1 and flip bloom filter
        ngram = 2
        grams = [s[i: i + ngram] for i in range(len(s) - ngram + 1)]
        bloom_filter = generate_bloom_filter(grams, self.bf_len, self.num_hash_function)
        return bloom_filter

    def build_reversed_index(self, data: Sequence[Any], header: Optional[List[str]] = None):
        """Build inverted index for PPRL Lambda-fold blocking method.

        :param data: list of lists
        :param header: file header, optional
        :return: reversed index as ReversedIndexResult
        """
        feature_to_index = self.get_feature_to_index_map(data, header)
        self.set_blocking_features_index(self.blocking_features, feature_to_index)

        # create record index lists
        if self.record_id_col is None:
            record_ids = list(range(len(data)))
        else:
            record_ids = [x[self.record_id_col] for x in data]

        random.seed(self.random_state)

        if self.input_clks:
            clks = deserialize_filters(data)
        else:
            clks = [self.__record_to_bf__(rec, self.blocking_features_index) for rec in data]
        bf_len = len(clks[0])

        # build Lambda fold tables and add to the invert index
        invert_index = {}  # type: Dict[Any, List[Any]]
        for i in range(self.mylambda):
            lambda_table = defaultdict(list)  # type: Dict[Any, Any]
            # sample K indices from [0, bf-len]
            indices = random.sample(range(bf_len), self.K)
            for rec_id, clk in zip(record_ids, clks):
                block_key = ''.join(['1' if clk[ind] else '0' for ind in indices])
                lambda_table['{}{}'.format(i, block_key)].append(rec_id)
            invert_index.update(lambda_table)

        return ReversedIndexResult(invert_index, reversed_index_stats(invert_index))

