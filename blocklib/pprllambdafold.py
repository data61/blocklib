import hashlib
import numpy as np
from collections import defaultdict
from blocklib.configuration import get_config
from .pprlindex import PPRLIndex


class PPRLIndexLambdaFold(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        An LSH-Based Blocking Approach with a Homomorphic Matching Technique for Privacy-Preserving Record Linkage.

        This class includes an implementation of Lambda-fold redundant blocking method.
    """

    def __init__(self, config):
        """Initialize the class and set the required parameters.

        Arguments:
        - config: dict
            Configuration for P-Sig reverted index.

        """
        super().__init__()
        # Lambda: number of redundant tables
        self.Lambda = int(get_config(config, "Lambda"))
        # bf-len: length of bloom filter
        self.bf_len = int(get_config(config, "bf-len"))
        # num_hash_function
        self.num_hash_function = int(get_config(config, "num-hash-funcs"))
        # K: number of base Hamming LSH hashing functions
        self.K = int(get_config(config, "K"))
        # blocking-features: list of blocking feature indices
        self.blocking_features = get_config(config, "blocking-features")

    def __record_to_bf__(self, record):
        """Convert a record to list of bigrams and then map to a bloom filter."""
        bloom_filter = np.zeros(self.bf_len, dtype=bool)
        s = ''.join([record[i] for i in self.blocking_features])
        # generate list of bigram of s. hash each bigram to position of bit 1 and flip bloom filter
        ngram = 2
        h1 = hashlib.sha1
        h2 = hashlib.md5
        for i in range(len(s) - ngram + 1):
            # get bigram
            gram = s[i: i + ngram]
            # get 2 family of hash functions
            hex_str1 = h1(gram.encode('utf-8')).hexdigest()
            hex_str2 = h2(gram.encode('utf-8')).hexdigest()
            int1 = int(hex_str1, 16)
            int2 = int(hex_str2, 16)
            # hash and flip K times
            bit_index = set()
            for j in range(self.num_hash_function):
                gi = int1 + j * int2
                gi = int(gi % self.bf_len)
                bit_index.add(gi)
            # flip bit positions
            bit_index = list(bit_index)
            bloom_filter[bit_index] = 1
        return bloom_filter

    def build_inverted_index(self, data, rec_id_col=None, random_state=None):
        """Build inverted index for PPRL Lambda-fold blocking method.

        :param data: list of lists
        :param rec_id_col: integer
        :return:
        """
        # create record index lists
        if rec_id_col is None:
            record_ids = np.arange(len(data))
        else:
            record_ids = [x[rec_id_col] for x in data]

        # build Lambda fold tables and add to the invert index
        invert_index = {}
        for i in range(self.Lambda):
            lambda_table = defaultdict(list)
            for rec_id, rec in zip(record_ids, data):
                bloom_filter = self.__record_to_bf__(rec)
                # sample K indices from [0, bf-len]
                rnd = np.random.RandomState(random_state)
                indices = rnd.choice(range(self.bf_len), self.K)
                block_key = ''.join(bloom_filter[indices].astype(np.int8).astype(str))
                lambda_table[block_key].append(rec_id)
            invert_index.update(lambda_table)

        return invert_index



