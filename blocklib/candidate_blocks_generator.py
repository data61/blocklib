"""Class that implement candidate block generations."""
from typing import Sequence, List, Dict, Tuple
import numpy as np
from collections import defaultdict
from .pprlindex import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .pprlkasn import PPRLIndexKAnonymousSortedNeighbour
from .validation import validate_signature_config

PPRLSTATES = {"p-sig": PPRLIndexPSignature,
              "lambda-fold": PPRLIndexLambdaFold,
              "kasn": PPRLIndexKAnonymousSortedNeighbour}


class CandidateBlockingResult:
    """Object for holding candidate blocking results."""

    def __init__(self, blocks: Dict, state: PPRLIndex, extra: Dict = {}):
        """
        Initialise a blocking result object.
        :param blocks:
        :param state:
        :param extra:
        """
        self.blocks = blocks
        self.state = state
        self.extra = extra


def make_candidate_block_object(reversed_index: Dict, state: PPRLIndex, algorithm: str):
    """
    Make candidate block object from reversed index and state.
    :param reversed_index:
    :param state:
    :param algorithm:
    :return:
    """
    assert algorithm in PPRLSTATES
    # make candidate block result object
    if algorithm == 'p-sig':
        cbf, cbf_index_to_sig_map = state.generate_block_filter(reversed_index)
        extra = dict(candidate_block_filter=cbf, cbf_map=cbf_index_to_sig_map)
        candidate_block_obj = CandidateBlockingResult(reversed_index, state, extra=extra)
    else:
        candidate_block_obj = CandidateBlockingResult(reversed_index, state)
    return candidate_block_obj


def generate_candidate_blocks(data: Sequence[Tuple[str, ...]], signature_config):
    """
    :param data: list of tuples E.g. ('0', 'Kenneth Bain', '1964/06/17', 'M')
    :param signature_config:
        A description of how the signatures should be generated.
        Schema for the signature config is found in
        ``docs/schema/signature-config-schema.json``

    :return: A 2-tuple containing
        A list of "signatures" per record in data.
        Internal state object from the signature generation (or None).

    """
    # validate config of blocking
    validate_signature_config(signature_config)

    # extract algorithm and its config
    algorithm = signature_config.get('type', 'not specified')
    config = signature_config.get('config', 'not specified')
    if config == 'not specified':
        raise ValueError('Please provide config for P-Sig from blocklib')

    # build corresponding PPLRIndex instance
    if algorithm == 'not specified':
        raise ValueError("Compute signature type is not specified.")

    elif algorithm in PPRLSTATES:
        state = PPRLSTATES[algorithm](config)
        reversed_index = state.build_reversed_index(data)
        state.summarize_reversed_index(reversed_index)

        # make candidate blocking result object
        candidate_block_obj = make_candidate_block_object(reversed_index, state, algorithm)

    else:
        raise NotImplementedError(f'The algorithm {algorithm} is not supported yet')

    return candidate_block_obj
