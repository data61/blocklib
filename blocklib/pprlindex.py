import statistics


class PPRLIndex:
    """General class that implements an indexing technique for PPRL."""

    def __init__(self):
        """Initialise base class.

        Parameters
        ----------
        nparty: int
            Number of parties

        """
        self.rec_dict = None
        self.ent_id_col = None
        self.rec_id_col = None
        self.revert_index = {}
        self.attr_select_list = {}
        self.stats = {}


    def build_revert_index(self, data, attr_select_lists):
        """Method which builds the index for all database.

           Argument:
           - data: list of tuples
                PII datasets
           - attr_select_lists: A list
                A list of attributes selected by users

           See derived classes for actual implementations.
        """
        pass


    def summarize_revert_index(self):
        """Summarize statistics of reverted index / blocks."""
        assert len(self.revert_index) > 0
        lengths = [len(rv) for rv in self.revert_index.values()]
        self.stats['min_size'] = min(lengths)
        self.stats['max_size'] = max(lengths)
        self.stats['avg_size'] = statistics.mean(lengths)
        self.stats['med_size'] = statistics.median(lengths)
        return self.stats
