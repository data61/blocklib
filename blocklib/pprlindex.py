import statistics


class PPRLIndex:
    """Base class for PPRL indexing/blocking."""

    def __init__(self):
        """Initialise base class."""
        self.rec_dict = None
        self.ent_id_col = None
        self.rec_id_col = None
        self.revert_index = {}
        self.stats = {}

    def build_inverted_index(self, data):
        """Method which builds the index for all database.

           Argument:
           - data: list of tuples
                PII datasets

           See derived classes for actual implementations.
        """
        raise NotImplementedError("Derived class needs to implement")

    def summarize_invert_index(self, invert_index):
        """Summarize statistics of reverted index / blocks."""
        assert len(invert_index) > 0
        # statistics of block
        lengths = [len(rv) for rv in invert_index.values()]
        self.stats['num_of_blocks'] = len(lengths)
        self.stats['len_of_blocks'] = lengths
        self.stats['min_size'] = min(lengths)
        self.stats['max_size'] = max(lengths)
        self.stats['avg_size'] = statistics.mean(lengths)
        self.stats['med_size'] = statistics.median(lengths)

        # find how many blocks each entity / record is a member of
        rec_to_block = {}
        for block_id, block in invert_index.items():
            for rec in block:
                if rec in rec_to_block:
                    rec_to_block[rec].append(block_id)
                else:
                    rec_to_block[rec] = [block_id]
        num_of_blocks_per_rec = [len(x) for x in rec_to_block.values()]
        self.stats['num_of_blocks_per_rec'] = num_of_blocks_per_rec

        print('Number of Blocks:   {}'.format(self.stats['num_of_blocks']))
        print('Maximum Block Size: {}'.format(self.stats['min_size']))
        print('Minimum Block Size: {}'.format(self.stats['max_size']))
        print('Average Block Size: {}'.format(self.stats['avg_size']))
        print('Median Block Size:  {}'.format(self.stats['med_size']))
        print('Number of Blocks Per Record (Sorted): {}'.format(sorted(num_of_blocks_per_rec)))

        return self.stats
