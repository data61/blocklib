import random
from typing import Any, Dict, List, Sequence, Optional, Union, cast
import logging
from pydantic.tools import parse_obj_as

from blocklib.configuration import get_config
from blocklib.utils import check_header
from blocklib.validation import PPRLIndexConfig


class PPRLIndex:
    """Base class for PPRL indexing/blocking."""

    def __init__(self, config: PPRLIndexConfig) -> None:
        """Initialise base class."""

        self.config: PPRLIndexConfig = cast(PPRLIndexConfig, config)
        self.rec_dict = None
        self.ent_id_col = None
        self.rec_id_col: Optional[int] = None

    def get_feature_to_index_map(self, data: Sequence[Sequence], header: Optional[List[str]] = None):
        """Return feature name to feature index mapping if there is a header and feature is of type string."""
        feature_type = type(self.blocking_features[0])  # type: ignore
        feature_to_index = None
        if len(data) == 0:
            return feature_to_index
        tuple_type = type(data[0])  # if data is CLKs, then tuple_type will be str, otherwise a tuple

        if header and feature_type == str and tuple_type != str:
            check_header(header, data[0])
            feature_to_index = {name: ind for ind, name in enumerate(header)}

        return feature_to_index

    def set_blocking_features_index(self, blocking_features, feature_to_index: Optional[Dict[str, int]] = None):
        """Set value of member variable blocking features index.

        self.blocking_features could be string (column name) or int (column index)
        self.blocking_features_index must be int (column index)

        """
        if feature_to_index:
            self.blocking_features_index = [feature_to_index[x] for x in blocking_features]
        else:
            self.blocking_features_index = blocking_features

    def build_reversed_index(self, data: Sequence[Sequence],  header: Optional[List[str]] = None):
        """Method which builds the index for all database.

           :param data: list of tuples, PII dataset
           :param header: file header, optional
           :rtype: ReversedIndexResult
           See derived classes for actual implementations.
        """
        raise NotImplementedError("Derived class needs to implement")

    @classmethod
    def select_reference_value(cls, reference_data: Sequence[Sequence], ref_data_config: Dict):
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

        logging.info('Selected %d random reference values' % (len(ref_val_list)))
        return ref_val_list


class ReversedIndexResult(object):

    def __init__(self, reversed_index: Dict, stats: Dict):
        self.reversed_index = reversed_index
        self.stats = stats

    def __eq__(self, other):
        return self.reversed_index == other.reversed_index and self.stats == other.stats
