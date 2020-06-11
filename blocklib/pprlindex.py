import random
from typing import Any, Dict, List, Sequence
from blocklib.configuration import get_config
from blocklib.stats import reversed_index_stats


class PPRLIndex:
    """Base class for PPRL indexing/blocking."""

    def __init__(self, config: Dict = {}) -> None:
        """Initialise base class."""
        self.rec_dict = None
        self.ent_id_col = None
        self.rec_id_col = None
        self.stats = {}  # type: Dict[str, Any]

    def build_reversed_index(self, data: Sequence[Sequence], verbose: bool):
        """Method which builds the index for all database.

           :param data: list of tuples, PII dataset
           :param verbose: print additional information to std out.

           See derived classes for actual implementations.
        """
        raise NotImplementedError("Derived class needs to implement")

    def summarize_reversed_index(self, reversed_index: Dict):
        """Summarize statistics of reverted index / blocks."""
        assert len(reversed_index) > 0
        # statistics of block
        self.stats = reversed_index_stats(reversed_index)
        # find how many blocks each entity / record is a member of
        rec_to_block = {}  # type: Dict[Any, List[Any]]
        for block_id, block in reversed_index.items():
            for rec in block:
                if rec in rec_to_block:
                    rec_to_block[rec].append(block_id)
                else:
                    rec_to_block[rec] = [block_id]
        num_of_blocks_per_rec = [len(x) for x in rec_to_block.values()]
        self.stats['num_of_blocks_per_rec'] = num_of_blocks_per_rec

        print('Statistics for the generated blocks:')
        print('\tNumber of Blocks:   {}'.format(self.stats['num_of_blocks']))
        print('\tMinimum Block Size: {}'.format(self.stats['min_size']))
        print('\tMaximum Block Size: {}'.format(self.stats['max_size']))
        print('\tAverage Block Size: {}'.format(self.stats['avg_size']))
        print('\tMedian Block Size:  {}'.format(self.stats['med_size']))
        print('\tStandard Deviation of Block Size:  {}'.format(self.stats['std_size']))

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
        random.seed(ref_random_seed)
        ref_val_list = random.sample(rec_features, num_vals)

        print('  Selected %d random reference values' % (len(ref_val_list)))
        return ref_val_list
