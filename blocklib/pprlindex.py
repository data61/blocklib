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

    def summarize_revert_index(self):
        """Summarize statistics of reverted index / blocks."""
        assert len(self.revert_index) > 0
        lengths = [len(rv) for rv in self.revert_index.values()]
        self.stats['min_size'] = min(lengths)
        self.stats['max_size'] = max(lengths)
        self.stats['avg_size'] = statistics.mean(lengths)
        self.stats['med_size'] = statistics.median(lengths)
        return self.stats
