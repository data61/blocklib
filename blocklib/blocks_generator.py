"""Class that implement final block generations."""
from typing import Sequence, List, Dict, Tuple
import numpy as np
from collections import defaultdict
from .pprlindex import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .candidate_blocks_generator import CandidateBlockingResult


def generate_blocks_2party(candidate_block_objs: Sequence[CandidateBlockingResult]):
    """
    Generate final blocks given list of candidate block objects from 2 data providers.
    :param candidate_block_objs
    :return: filtered_reversed_indices: List of dictionaries
    """
    # check the PPRLIndex state is the same
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
        raise TypeError(f'Unsupported blocking instance {state_type}')

    return filtered_reversed_indices


def generate_reverse_blocks(reversed_indices: Sequence[Dict]):
    """
    Return a dictionary of record to block key mapping
    :param reversed_indices:
    :return:
    """
    rec_to_blockkey = []
    for reversed_index in reversed_indices:
        map_rec_block = defaultdict(list)
        for blk_key, rec_list in reversed_index.items():
            for rec in rec_list:
                map_rec_block[rec].append(blk_key)
        rec_to_blockkey.append(map_rec_block)
    return rec_to_blockkey


def generate_blocks_psig(reversed_indices: Sequence[Dict], block_states: Sequence[PPRLIndex], threshold:int):
    """
    Generate final blocks for P-Sig.
    :param reversed_indices:
    :param block_states:
    :param threshold: int
    :return:
    """
    # generate candidate bloom filters
    candidate_bloom_filters = []
    cbf_index_to_sig_maps = []
    for reversed_index, state in zip(reversed_indices, block_states):
        cbf, cbf_map = state.generate_block_filter(reversed_index)
        candidate_bloom_filters.append(cbf)
        cbf_index_to_sig_maps.append(cbf_map)

    # compute blocking filter (and operation)
    cbf = np.sum(candidate_bloom_filters, axis=0)
    block_filter = cbf >= threshold

    # filter reversed_indices with block filter
    for reversed_index, cbf_map in zip(reversed_indices, cbf_index_to_sig_maps):
        sig_pos = defaultdict(list)
        for pos, sig_list in cbf_map.items():
            for sig in sig_list:
                sig_pos[sig].append(pos)
        for sig, positions in sig_pos.items():
            if not all(block_filter[i] for i in positions):
                del reversed_index[sig]

    return reversed_indices


