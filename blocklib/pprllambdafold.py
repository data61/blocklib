import random
from collections import defaultdict
from typing import Dict, Sequence, Any, List
from blocklib.configuration import get_config
from .pprlindex import PPRLIndex
from .utils import deserialize_filters
from .encoding import generate_bloom_filter
from bitarray import bitarray
import hashlib


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
        # Lambda: number of redundant tables
        self.mylambda = int(get_config(config, "Lambda"))
        # bf-len: length of bloom filter
        self.bf_len = int(get_config(config, "bf-len"))
        # num_hash_function
        num_hash_fun = get_config(config, "num-hash-funcs")
        if num_hash_fun == 'opt':
            print('determining the optimal number of hash functions...')

            def expected_popcount(n, k):
                """ return the expected popcount of a Bloomfilter of length 'n' after 'k' insertions.
                Note that in this context, k does not mean the number of hash functions.

                :param (int) n: the length of the Bloom filter
                :param (int) k: the number of insertions
                :return: expected popcount
                """
                sum = 0
                for i in range(k):
                    sum += (1 - 1 / n) ** i
                return sum

            def find_optimal_k(n):
                best_diff = n
                best_k = -1
                for k in range(n):
                    diff = abs(expected_popcount(n, k) - n / 2)
                    if diff < best_diff:
                        best_diff = diff
                        best_k = k
                return best_k

            self.num_insertions = find_optimal_k(self.bf_len)
            self.num_hash_function = 'opt'
            print(f'set num_insertions to {self.num_insertions}')
        else:
            self.num_hash_function = int(num_hash_fun)
        # K: number of base Hamming LSH hashing functions
        self.K = int(get_config(config, "K"))
        # blocking-features: list of blocking feature indices
        self.blocking_features = get_config(config, "blocking-features")
        self.input_clks = get_config(config, 'input-clks')
        self.random_state = get_config(config, "random_state")
        self.record_id_col = config.get("record-id-col", None)

    def generate_bloom_filter(self, list_of_strs: List[str]):
        # go through each signature and generate bloom filter of it
        # -- we only store the set of index that flipped to 1
        bf = bitarray(self.bf_len)
        bf.setall(False)

        def bits_per_token(num_tokens, total_bits):
            k = int(total_bits / num_tokens)
            residue = total_bits % num_tokens
            return ([k + 1] * residue) + ([k] * (num_tokens - residue))

        for token, num_insertions in zip(list_of_strs, bits_per_token(len(list_of_strs), self.num_insertions)):
            # config for hashing
            h1 = hashlib.sha1
            h2 = hashlib.md5

            sha_bytes = h1(token.encode('utf-8')).digest()
            md5_bytes = h2(token.encode('utf-8')).digest()
            int1 = int.from_bytes(sha_bytes, 'big') % self.bf_len
            int2 = int.from_bytes(md5_bytes, 'big') % self.bf_len

            for i in range(num_insertions):
                gi = (int1 + i * int2) % self.bf_len
                bf[gi] = 1
        return bf

    def __record_to_bf__(self, record: Sequence):
        """Convert a record to list of bigrams and then map to a bloom filter."""
        s = ''.join([record[i] for i in self.blocking_features])
        # generate list of bigram of s. hash each bigram to position of bit 1 and flip bloom filter
        ngram = 2
        grams = [s[i: i + ngram] for i in range(len(s) - ngram + 1)]
        if self.num_hash_function == 'opt':
            bloom_filter = self.generate_bloom_filter(grams)
        else:
            bloom_filter = generate_bloom_filter(grams, self.bf_len, self.num_hash_function)
        return bloom_filter

    def build_reversed_index(self, data: Sequence[Any]):
        """Build inverted index for PPRL Lambda-fold blocking method.

        :param data: list of lists
        :param rec_id_col: integer
        :return:
        """
        # create record index lists
        if self.record_id_col is None:
            record_ids = list(range(len(data)))
        else:
            record_ids = [x[self.record_id_col] for x in data]

        random.seed(self.random_state)

        if self.input_clks:
            clks = deserialize_filters(data)
        else:
            clks = [self.__record_to_bf__(rec) for rec in data]
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

