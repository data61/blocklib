import numpy as np
from typing import Any, Dict, List, Sequence

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

    def build_reversed_index(self, data: Sequence[Sequence]):
        """Build inverted index given P-Sig method."""
        reversed_index = {}  # type: Dict[Any, List[Any]]
        # Build index of records
        if self.rec_id_col is None:
            record_ids = np.arange(len(data))
        else:
            record_ids = [x[self.rec_id_col] for x in data]

        # Build inverted index
        # {signature -> record ids}
        for rec_id, dtuple in zip(record_ids, data):

            signatures = generate_signatures(self.signature_strategies, dtuple)

            for signature in signatures:
                if signature in reversed_index:
                    reversed_index[signature].append(rec_id)
                else:
                    reversed_index[signature] = [rec_id]

        filtered_reversed_index = self.filter_reversed_index(data, reversed_index)

        # map signatures in reversed_index into bloom filter
        num_hash_func = int(self.blocking_config.get("number-hash-functions", None))
        bf_len = int(self.blocking_config.get("bf-len", None))

        reversed_index = {}
        for signature, rec_ids in filtered_reversed_index.items():
            bf_set = tuple(flip_bloom_filter(signature, bf_len, num_hash_func))
            reversed_index[bf_set] = rec_ids

        return reversed_index

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

        # check if final inverted index is empty
        if len(reversed_index) == 0:
            raise ValueError('P-Sig: All records are filtered out!')
        return reversed_index
