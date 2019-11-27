"""Module that implement final block generations."""
from typing import Sequence, List, Dict, Any, Set
import numpy as np
from collections import defaultdict
from .pprlindex import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .candidate_blocks_generator import CandidateBlockingResult


def generate_blocks_2party(candidate_block_objs: Sequence[CandidateBlockingResult]):
    """
    Generate final blocks given list of candidate block objects from 2 data providers.
    :param candidate_block_objs: A list of candidate block result objects from 2 data providers
    :return: filtered_reversed_indices: List of dictionaries
    """
    # check if the states are of same type
    assert type(candidate_block_objs[0].state) == type(candidate_block_objs[1].state)

    state_type = type(candidate_block_objs[0].state)
    reversed_indices = [obj.blocks for obj in candidate_block_objs]
    block_states = [obj.state for obj in candidate_block_objs]

    # normal blocking algorithm that do not need special generation
    if state_type in {PPRLIndexLambdaFold}:
        # decide final blocks keys - intersection of all reversed index keys
        block_keys = set(reversed_indices[0].keys())
        for reversed_index in reversed_indices[1:]:
            block_keys = block_keys.intersection(set(reversed_index.keys()))
        # filter reversed indices if keys not in block_keys
        filtered_reversed_indices = []
        for reversed_index in reversed_indices:
            reversed_index = {k: v for k, v in reversed_index.items() if k in block_keys}
            filtered_reversed_indices.append(reversed_index)

    elif state_type == PPRLIndexPSignature:
        filtered_reversed_indices = generate_blocks_psig(reversed_indices, block_states, threshold=2)

    else:
        raise TypeError('Unsupported blocking instance {}'.format(state_type))

    return filtered_reversed_indices


def generate_reverse_blocks(reversed_indices: Sequence[Dict]):
    """
    Return a list of dictionaries of record to block key mapping
    :param reversed_indices: A list of dictionaries where key is the block key and value is a list of record IDs.
    :return: rec_to_blockkey: A list of dictionaries where key is the record ID and value is a set of block key the record belongs to
    """
    rec_to_blockkey = []
    for reversed_index in reversed_indices:
        map_rec_block: Dict[Any, List[Any]] = defaultdict(list)
        for blk_key, rec_list in reversed_index.items():
            for rec in rec_list:
                map_rec_block[rec].add(blk_key)
        rec_to_blockkey.append(map_rec_block)
    return rec_to_blockkey


def generate_blocks_psig(reversed_indices: Sequence[Dict], block_states: Sequence[PPRLIndex], threshold: int):
    """
    Generate final blocks for P-Sig.
    :param reversed_indices: A list of dictionaries where key is the block key and value is a list of record IDs.
    :param block_states: A list of PPRLIndex objects that hold configuration of the blocking job
    :param threshold: int which decides a pair when number of 1 bits in bloom filter is large than or equal to threshold
    :return: reversed_indices: A list of dictionaries where blocks that don't contain any matches are deleted
    """
    # generate candidate bloom filters
    candidate_bloom_filters = []
    for reversed_index, state in zip(reversed_indices, block_states):
        cbf: Set[int] = set()
        for bf_set in reversed_index:
            cbf = cbf.union(bf_set)

        bf_len = int(block_states[0].blocking_config.get("bf_len", None))
        bf_vector = np.zeros(bf_len, dtype=bool)
        bf_vector[list(cbf)] = True
        candidate_bloom_filters.append(bf_vector)

    # compute blocking filter (and operation)
    cbf_array = np.sum(candidate_bloom_filters, axis=0)
    block_filter = cbf_array >= threshold

    # filter reversed_indices with block filter
    for reversed_index in reversed_indices:

        has_matches = {bf_set: all(block_filter[i] for i in bf_set) for bf_set in reversed_index}
        for bf_set in has_matches:
            if not has_matches[bf_set]:
                del reversed_index[bf_set]

    return reversed_indices


