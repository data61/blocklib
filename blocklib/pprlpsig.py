import os
import time
import math
import hashlib
from collections import defaultdict

from .pprlindex import PPRLIndex

class PPRLIndexPSignature(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        Reference scalability entity resolution using probability signatures
        on parallel databases.

        This class includes an implmentation of p-sig algorithm.
    """

    def __init__(self, config):
        """Initialize the class and set the required parameters.

        Arguments:
        - config: dict
            Configuration for P-Sig reverted index.

        """
        self.num_hash_funct = self.get_config(config,'num_hash_funct')
        self.attr_select_list = self.get_config(config,'attr_select_list')
        self.bf_len = self.get_config(config,'bf_len')
        self.min_occur_ratio = self.get_config(config,'min_occur_ratio')
        self.max_occur_ratio = self.get_config(config,'max_occur_ratio')

    def get_config(self, config, arg_name):
        """Get arg value if arg_name exists in the config.

        Arguments
        ---------
        config: dict
        arg_name: str

        """
        value = config.get(arg_name, 'not specified')
        if value == 'not specified':
            raise ValueError('P-Sig: Argument "{}" is not specified'.format(arg_name))
        return value

    def build_invert_index(self, data, rec_id_col=None):
        """Build reverted index given P-Sig method."""
        invert_index = {}
        # Build index of records
        if rec_id_col is not None:
            rec_ids = [dtuple[rec_id_col] for dtuple in data]
        else:
            rec_ids = range(len(data))

        # Build reverted index
        for rec_id, dtuple in zip(rec_ids, data):
            attr_ind = self.attr_select_list
            signature = ''.join([dtuple[ind] for ind in attr_ind])
            if signature in invert_index:
                invert_index[signature].append(rec_id)
            else:
                invert_index[signature] = [rec_id]

        # Filter revert index based on ratio
        n = len(data)
        invert_index = {k: v for k, v in invert_index.items()
                        if len(v) < n * self.max_occur_ratio and
                           len(v) > n * self.min_occur_ratio}
        if len(invert_index) == 0:
            raise ValueError('P-Sig: All records are filtered out!')

        # Generate candidate Bloom Filter
        candidate_bloom_filter = self.generate_bloom_filter(invert_index)
        # cache this?
        return invert_index, candidate_bloom_filter

    def generate_bloom_filter(self, invert_index):
        """Generate candidate bloom filter for inverted index."""
        # config for hashing
        h1 = hashlib.sha1
        h2 = hashlib.md5
        num_hash_funct = self.num_hash_funct
        bf_len = self.bf_len

        # go through each signature and generate bloom filter of it
        # -- we only store the set of indice that flipped to 1
        candidate_bloom_filter = set()
        for signature in invert_index:
            hex_str1 = h1(signature.encode('utf-8')).hexdigest()
            hex_str2 = h2(signature.encode('utf-8')).hexdigest()
            int1 = int(hex_str1, 16)
            int2 = int(hex_str2, 16)

            # flip {num_hash_funct} times
            bfset = set()
            for i in range(num_hash_funct):
                gi = int1 + i * int2
                gi = int(gi % bf_len)
                bfset.add(gi)

            # union indices that have been flipped 1 in candidate bf
            candidate_bloom_filter = candidate_bloom_filter.union(bfset)

        return candidate_bloom_filter
