import statistics
import numpy as np
from typing import Sequence, Tuple, Dict
from blocklib.configuration import get_config


class PPRLIndex:
    """Base class for PPRL indexing/blocking."""

    def __init__(self):
        """Initialise base class."""
        self.rec_dict = None
        self.ent_id_col = None
        self.rec_id_col = None
        self.revert_index = {}
        self.stats = {}

    def build_reversed_index(self, data: Sequence[Sequence]):
        """Method which builds the index for all database.

           Argument:
           - data: list of tuples
                PII datasets

           See derived classes for actual implementations.
        """
        raise NotImplementedError("Derived class needs to implement")

    def summarize_reversed_index(self, reversed_index: Dict):
        """Summarize statistics of reverted index / blocks."""
        assert len(reversed_index) > 0
        # statistics of block
        lengths = [len(rv) for rv in reversed_index.values()]
        self.stats['num_of_blocks'] = len(lengths)
        self.stats['len_of_blocks'] = lengths
        self.stats['min_size'] = min(lengths)
        self.stats['max_size'] = max(lengths)
        self.stats['avg_size'] = int(statistics.mean(lengths))
        self.stats['med_size'] = int(statistics.median(lengths))
        self.stats['std_size'] = statistics.stdev(lengths)
        # find how many blocks each entity / record is a member of
        rec_to_block = {}
        for block_id, block in reversed_index.items():
            for rec in block:
                if rec in rec_to_block:
                    rec_to_block[rec].append(block_id)
                else:
                    rec_to_block[rec] = [block_id]
        num_of_blocks_per_rec = [len(x) for x in rec_to_block.values()]
        self.stats['num_of_blocks_per_rec'] = num_of_blocks_per_rec

        print('Number of Blocks:   {}'.format(self.stats['num_of_blocks']))
        print('Minimum Block Size: {}'.format(self.stats['min_size']))
        print('Maximum Block Size: {}'.format(self.stats['max_size']))
        print('Average Block Size: {}'.format(self.stats['avg_size']))
        print('Median Block Size:  {}'.format(self.stats['med_size']))
        print('Standard Deviation of Block Size:  {}'.format(self.stats['std_size']))

        return self.stats

    def select_reference_value(self, reference_data: Sequence[Sequence], ref_data_config: Dict):
        """Load reference data for methods need reference."""
        # read configurations
        ref_default_features = get_config(ref_data_config, 'blocking-features')
        ref_random_seed = get_config(ref_data_config, 'random-state')
        num_vals = get_config(ref_data_config, 'num-reference-values')

        # extract features in config
        rec_features = [''.join([dtuple[x] for x in ref_default_features]) for dtuple in reference_data]

        # generate reference values
        rnd = np.random.RandomState(ref_random_seed)
        index = rnd.choice(range(len(rec_features)), num_vals, replace=False)
        ref_val_list = [rec_features[x] for x in index]

        print('  Selected %d random reference values' % (len(ref_val_list)))
        return ref_val_list