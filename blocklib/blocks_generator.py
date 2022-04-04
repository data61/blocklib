"""Module that implements final block generations."""
from collections import defaultdict
from typing import Any, Dict, Sequence, Set, List, cast
import ast
import numpy as np
from hashlib import blake2b

from blocklib import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .candidate_blocks_generator import CandidateBlockingResult


def check_block_object(candidate_block_objs: Sequence[CandidateBlockingResult]):
    """
    Check candidate block objects type and their states type.

    :raises TypeError: if conditions aren't met.
    :param candidate_block_objs: A list of candidate block result objects from 2 data providers
    """
    for obj in candidate_block_objs:
        if type(obj) != CandidateBlockingResult:
            raise TypeError('Unsupported blocking instance {}'.format(type(obj)))

    state_type = type(candidate_block_objs[0].state)
    for obj in candidate_block_objs:
        if type(obj.state) != state_type:
            raise TypeError('Unexpected state type found: {} where we expect: {}'.format(type(obj.state), state_type))


def generate_blocks(candidate_block_objs: Sequence[CandidateBlockingResult], K: int) -> List[Dict[Any, List[Any]]]:
    """
    Generate final blocks given list of candidate block objects from 2 or more than 2 data providers.

    :param candidate_block_objs: A list of CandidateBlockingResult from multiple data providers
    :param K: it specifies the minimum number of occurrence for records to be included in the final blocks
    :return: List of dictionaries, filter out records that appear in less than K parties
    """
    check_block_object(candidate_block_objs)
    assert len(candidate_block_objs) >= K >= 2

    # obtain list of objects
    state_type = type(candidate_block_objs[0].state)
    reversed_indices = [obj.blocks for obj in candidate_block_objs]
    block_states = [obj.state for obj in candidate_block_objs]  # type: Sequence[PPRLIndex]

    filtered_reversed_indices = []  # type: List[Dict[Any, List[Any]]]
    if state_type == PPRLIndexPSignature:
        block_states = cast(Sequence[PPRLIndexPSignature], block_states)
        filtered_reversed_indices = generate_blocks_psig(reversed_indices, block_states, threshold=K)

    # default strategy: use key in reversed index as block keys
    else:
        block_keys = defaultdict(int)  # type: Dict[Any, int]
        for reversed_index in reversed_indices:
            for key in reversed_index:
                block_keys[key] += 1
        final_block_keys = [key for key, count in block_keys.items() if count >= K]
        for reversed_index in reversed_indices:
            reversed_index = {k: v for k, v in reversed_index.items() if k in final_block_keys}
            filtered_reversed_indices.append(reversed_index)

    return filtered_reversed_indices


def generate_reverse_blocks(reversed_indices: Sequence[Dict]):
    """Invert a map from "blocks to records" to "records to blocks".

    :param reversed_indices: A list of dictionaries where key is the block key and value is a list of record IDs.
    :return: A list of dictionaries where key is the record ID and value is a set of blocking keys the record belongs to.
    """
    rec_to_blockkey = []
    for reversed_index in reversed_indices:
        map_rec_block = defaultdict(set)  # type: Dict[Any, Set[Any]]
        for blk_key, rec_list in reversed_index.items():
            for rec in rec_list:
                map_rec_block[rec].add(blk_key)
        rec_to_blockkey.append(map_rec_block)
    return rec_to_blockkey


def generate_blocks_psig(reversed_indices: Sequence[Dict], block_states: Sequence[PPRLIndexPSignature], threshold: int):
    """Generate blocks for P-Sig

    :param reversed_indices: A list of dictionaries where key is the block key and value is a list of record IDs.
    :param block_states: A list of PPRLIndex objects that hold configuration of the blocking job
    :param threshold: int which decides a pair when number of 1 bits in bloom filter is large than or equal to threshold
    :return: A list of dictionaries where blocks that don't contain any matches are deleted
    """
    # generate candidate bloom filters
    candidate_bloom_filters = []
    for reversed_index, state in zip(reversed_indices, block_states):
        cbf = set()  # type: Set[int]
        for bf_set in reversed_index:
            bf_set = ast.literal_eval(bf_set)
            cbf = cbf.union(bf_set)

        bf_len = block_states[0].blocking_config.bloom_filter_length
        bf_vector = np.zeros(bf_len, dtype=bool)
        bf_vector[list(cbf)] = True
        candidate_bloom_filters.append(bf_vector)

    # compute blocking filter (and operation)
    cbf_array = np.sum(np.stack(candidate_bloom_filters), axis=0)
    block_filter = cbf_array >= threshold

    # filter reversed_indices with block filter
    for reversed_index in reversed_indices:
        has_matches = {bf_set: all(block_filter[i] for i in ast.literal_eval(bf_set)) for bf_set in reversed_index}
        for bf_set in has_matches:
            if not has_matches[bf_set]:
                del reversed_index[bf_set]

    # because of collisions in counting bloom filter, there are blocks only unique to one filtered index
    # only keep blocks that exist in at least threshold many reversed indices
    keys = defaultdict(int)  # type: Dict[str, int]
    for reversed_index in reversed_indices:
        for k in reversed_index:
            keys[k] += 1
    common_keys = [k for k in keys if keys[k] >= threshold]
    clean_reversed_indices = []  # type: List[Dict[str, List]]
    compress_block_key = block_states[0].blocking_config.compress_block_key

    def optional_compression(key: str) -> str:
        if compress_block_key:
            return blake2b(key.encode(), digest_size=5).hexdigest()
        else:
            return key

    for reversed_index in reversed_indices:
        clean_reversed_indices.append(dict((optional_compression(k), reversed_index[k]) for k in common_keys if k in reversed_index))

    return clean_reversed_indices
