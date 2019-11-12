import gzip
import random
import statistics
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
        self.stats['avg_size'] = int(statistics.mean(lengths))
        self.stats['med_size'] = int(statistics.median(lengths))
        self.stats['std_size'] = statistics.stdev(lengths)
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
        print('Minimum Block Size: {}'.format(self.stats['min_size']))
        print('Maximum Block Size: {}'.format(self.stats['max_size']))
        print('Average Block Size: {}'.format(self.stats['avg_size']))
        print('Median Block Size:  {}'.format(self.stats['med_size']))
        print('Standard Deviation of Block Size:  {}'.format(self.stats['std_size']))

        return self.stats

    def load_reference_data(self, ref_data_config):
        """Load reference data for methods need reference."""
        # read configurations
        ref_data_path = get_config(ref_data_config, 'path')
        ref_header_line = get_config(ref_data_config, 'header_line')
        ref_default_features = get_config(ref_data_config, 'default_features')
        ref_random_seed = get_config(ref_data_config, 'random_seed')
        num_vals = get_config(ref_data_config, 'num_vals')

        # load reference data as a dictionary
        rec_dict = self.__read_csv_gz_file__(ref_data_path, ref_header_line)
        print('Loaded reference values database: %d records' % (len(rec_dict)))

        # extract features in config
        rec_features = [''.join([dtuple[x] for x in ref_default_features])
                        for dtuple in rec_dict.values()]

        # generate reference values
        random.seed(ref_random_seed)
        ref_val_list = set()

        while len(ref_val_list) < num_vals:
            # random select one reference value allow repeat
            rand_ref_val = random.choice(rec_features)
            ref_val_list.add(rand_ref_val)

        print('  Selected %d random reference values' % (len(ref_val_list)))
        return ref_val_list

    def __read_csv_gz_file__(self, file_name, header_line, rec_id_col=None):
        """Read a CSV or Gz file and return a dictionary.

        The keys are unique record identifiers and values are lists that
        contain actual record.
        """
        rec_dict = {}

        # read in file
        is_gz_file = file_name.lower().endswith('gz')
        in_file = gzip.open(file_name) if is_gz_file else open(file_name)

        if header_line:
            header_line = in_file.readline()  # skip over header line

        for rec_count, rec in enumerate(in_file):
            if type(rec) == bytes:
                rec = rec.decode()
            rec = rec.split(',')
            rec = list(map(lambda x: x.strip(), rec))

            # check uniqueness of record id
            rec_id =  rec_count if rec_id_col is None else rec[rec_id_col]
            if rec_id in rec_dict:
                raise ValueError('Record ID "{}" is not unique in file {}'.format(rec_id, file_name))

            rec_dict[rec_id] = rec

        return rec_dict
