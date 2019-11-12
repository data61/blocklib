import hashlib
import time
import numpy as np
from blocklib.configuration import get_config
from .pprlindex import PPRLIndex
from .signature_generator import generate_signatures
from .encoding import generate_bloom_filter


class PPRLIndexPSignature(PPRLIndex):
    """Class that implements the PPRL indexing technique:

        Reference scalability entity resolution using probability signatures
        on parallel databases.

        This class includes an implementation of p-sig algorithm.
    """

    def __init__(self, config):
        """Initialize the class and set the required parameters.

        Arguments:
        - config: dict
            Configuration for P-Sig reverted index.

        """
        super().__init__()
        self.filter_config = get_config(config, "filter")
        self.blocking_config = get_config(config, "blocking-filter")
        self.signature_strategies = get_config(config, 'signatureSpecs')

    def build_inverted_index(self, data, rec_id_col=None):
        """Build inverted index given P-Sig method."""
        start_time = time.time()
        invert_index = {}
        # Build index of records
        if rec_id_col is not None:
            rec_ids = [dtuple[rec_id_col] for dtuple in data]
        else:
            rec_ids = range(len(data))

        # Build inverted index
        # {signature -> record ids}
        for rec_id, dtuple in zip(rec_ids, data):

            signatures = generate_signatures(self.signature_strategies, dtuple)

            for signature in signatures:
                if signature in invert_index:
                    invert_index[signature].append(rec_id)
                else:
                    invert_index[signature] = [rec_id]

        invert_index = self.filter_inverted_index(data, invert_index)

        delta_time = time.time() - start_time
        self.stats['blocking_time'] = delta_time

        return invert_index

    def filter_inverted_index(self, data, invert_index):
        # Filter inverted index based on ratio
        n = len(data)

        # filter blocks based on filter type
        filter_type = get_config(self.filter_config, "type")
        if filter_type == "ratio":
            min_occur_ratio = get_config(self.filter_config, 'min_occur_ratio')
            max_occur_ratio = get_config(self.filter_config, 'max_occur_ratio')
            invert_index = {k: v for k, v in invert_index.items() if n * max_occur_ratio > len(v) > n * min_occur_ratio}
        elif filter_type == "count":
            min_occur_count = get_config(self.filter_config, "min_occur_count")
            max_occur_count = get_config(self.filter_config, "max_occur_count")
            invert_index = {k: v for k, v in invert_index.items() if n * max_occur_count > len(v) > min_occur_count}
        else:
            raise NotImplementedError("Don't support {} filter yet.".format(filter_type))

        # check if final inverted index is empty
        if len(invert_index) == 0:
            raise ValueError('P-Sig: All records are filtered out!')
        return invert_index

    def generate_block_filter(self, invert_index):
        """Generate candidate blocking filter for inverted index e.g. bloom filter."""
        blocking_type = get_config(self.blocking_config, "type")
        if blocking_type == "bloom filter":
            cbf, cbd_index_to_sig_map = self.__generate_bloom_filter__(invert_index)
        else:
            raise NotImplementedError("Don't support {} blocking filter yet.".format(blocking_type))
        return cbf, cbd_index_to_sig_map

    def __generate_bloom_filter__(self, invert_index):
        """Generate bloom filter for inverted index."""
        num_hash_funct = int(get_config(self.blocking_config, "number_hash_functions"))
        bf_len = int(get_config(self.blocking_config, "bf_len"))

        candidate_block_filter, cbf_index_to_sig_map = generate_bloom_filter(invert_index.keys(),
                                                                             bf_len, num_hash_funct)

        #print("number of unset bits in cbf:", len(set(range(bf_len)).difference(candidate_bloom_filter)))
        return candidate_block_filter, cbf_index_to_sig_map
