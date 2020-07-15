import random
import numpy as np
from collections import defaultdict
from typing import Dict, Sequence, Any, List, Optional
from blocklib.configuration import get_config
from .pprlindex import PPRLIndex
from .encoding import generate_bloom_filter
from .utils import deserialize_filters, check_header


class PPRLIndexLambdaFold(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        An LSH-Based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage.

        This class includes an implementation of Lambda-fold redundant blocking method.
    """

    def __init__(self, config: Dict):
        """Initialize the class and set the required parameters.

        Arguments:
        - config: dict
            Configuration for P-Sig reverted index.

        """
        super().__init__()
        self.blocking_features = get_config(config, "blocking-features")
        # Lambda: number of redundant tables
        self.mylambda = int(get_config(config, "Lambda"))
        # bf-len: length of bloom filter
        self.bf_len = int(get_config(config, "bf-len"))
        # num_hash_function
        self.num_hash_function = int(get_config(config, "num-hash-funcs"))
        # K: number of base Hamming LSH hashing functions
        self.K = int(get_config(config, "K"))
        self.input_clks = get_config(config, 'input-clks')
        self.random_state = get_config(config, "random_state")
        self.record_id_col = config.get("record-id-col", None)

    def __record_to_bf__(self, record: Sequence, blocking_features_index: List[int]):
        """Convert a record to list of bigrams and then map to a bloom filter."""
        s = ''.join([record[i] for i in blocking_features_index])
        # generate list of bigram of s. hash each bigram to position of bit 1 and flip bloom filter
        ngram = 2
        grams = [s[i: i + ngram] for i in range(len(s) - ngram + 1)]
        bloom_filter = generate_bloom_filter(grams, self.bf_len, self.num_hash_function)
        return bloom_filter

    def build_reversed_index(self, data: Sequence[Any], verbose: bool = False, header: Optional[List[str]] = None):
        """Build inverted index for PPRL Lambda-fold blocking method.

        :param data: list of lists
        :param verbose: ignored
        :return:
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

        return invert_index

