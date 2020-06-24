"""Class that implement candidate block generations."""
from typing import Dict, Sequence, Tuple, Type, List, Optional
from .configuration import get_config
from .pprlindex import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .validation import validate_signature_config


PPRLSTATES = {
    "p-sig": PPRLIndexPSignature,
    "lambda-fold": PPRLIndexLambdaFold,
}  # type: Dict[str, Type[PPRLIndex]]



class CandidateBlockingResult:
    """Object for holding candidate blocking results."""

    def __init__(self, blocks: Dict, state: PPRLIndex):
        """
        Initialise a blocking result object.
        :param blocks: A dictionary where key is set of 1 bits in bloom filter and value is a list of record IDs
        :param state: A PPRLIndex state that contains configuration of blocking
        """
        self.blocks = blocks
        self.state = state


def generate_candidate_blocks(data: Sequence[Tuple[str, ...]], signature_config: Dict, header: Optional[List[str]] = None,
                              verbose: bool = False):
    """
    :param data: list of tuples E.g. ('0', 'Kenneth Bain', '1964/06/17', 'M')
    :param signature_config:
        A description of how the signatures should be generated.
        Schema for the signature config is found in
        ``docs/schema/signature-config-schema.json``
    :param header: column names (optional)
        Program should throw exception if block features are string but header is None
    :param verbose: print additional information to std out.

    :return: A 2-tuple containing
        A list of "signatures" per record in data.
        Internal state object from the signature generation (or None).

    """
    # validate config of blocking
    validate_signature_config(signature_config)

    # extract algorithm and its config
    algorithm = signature_config.get('type', 'not specified')
    config = signature_config.get('config', 'not specified')

    # check if blocking features are column index or feature name
    blocking_features = get_config(config, 'blocking-features')
    feature_type = type(blocking_features[0])
    error_msg = 'All feature types should be the same - either feature name or feature index'
    assert all(type(x) == feature_type for x in blocking_features[1:]), error_msg

    # header should not be None if blocking features are string
    if feature_type == str:
        assert header, 'Header must not be None if blocking features are string'

    if algorithm in PPRLSTATES:
        state = PPRLSTATES[algorithm](config)
        reversed_index = state.build_reversed_index(data, verbose, header)
        state.summarize_reversed_index(reversed_index)

        # make candidate blocking result object
        candidate_block_obj = CandidateBlockingResult(reversed_index, state)

    else:
        raise NotImplementedError('The algorithm {} is not supported yet'.format(algorithm))

    return candidate_block_obj
