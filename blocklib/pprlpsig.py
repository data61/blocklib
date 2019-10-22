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

    def build_revert_index(self, data, rec_id_col=None):
        """Build reverted index given P-Sig method."""
        revert_index = {}
        # Build index of records
        if rec_id_col is not None:
            rec_ids = [dtuple[rec_id_col] for dtuple in data]
        else:
            rec_ids = range(len(data))

        # Build reverted index
        for rec_id, dtuple in zip(rec_ids, data):
            attr_ind = self.attr_select_list
            signature = ''.join([dtuple[ind] for ind in attr_ind])
            if signature in revert_index:
                revert_index[signature].append(rec_id)
            else:
                revert_index[signature] = [rec_id]

        # Filter revert index based on ratio
        n = len(data)
        revert_index = {k: v for k, v in revert_index.items()
                        if len(v) < n * self.max_occur_ratio and
                           len(v) > n * self.min_occur_ratio}

        # cache this?
        return revert_index
