"""Class to implement privacy preserving encoding."""
import hashlib
import numpy as np
from typing import List, Set


def flip_bloom_filter(string: str, bf_len: int, num_hash_funct: int):
    """
    Hash string and return indices of bits that have been flipped correspondingly.

    :param string: string: to be hashed and to flip bloom filter
    :param bf_len: int: length of bloom filter
    :param num_hash_funct: int: number of hash functions
    :return: bfset: a set of integers - indices that have been flipped to 1
    """
    # config for hashing
    h1 = hashlib.sha1
    h2 = hashlib.md5

    sha_bytes = h1(string.encode('utf-8')).digest()
    md5_bytes = h2(string.encode('utf-8')).digest()
    int1 = int.from_bytes(sha_bytes, 'big') % bf_len
    int2 = int.from_bytes(md5_bytes, 'big') % bf_len

    # flip {num_hash_funct} times
    bfset = set()
    for i in range(num_hash_funct):
        gi = (int1 + i * int2) % bf_len
        bfset.add(gi)

    return bfset


def generate_bloom_filter(list_of_strs: List[str], bf_len: int, num_hash_funct: int):
    """
    Generate a bloom filter given list of strings.

    :param return_cbf_index_sig_map:
    :param list_of_strs:
    :param bf_len:
    :param num_hash_funct:
    :return: bloom_filter_vector if return_cbf_index_sig_map is False else (bloom_filter_vector, cbf_index_sig_map)
    """
    # go through each signature and generate bloom filter of it
    # -- we only store the set of index that flipped to 1
    candidate_bloom_filter = set()  # type: Set[int]

    for signature in list_of_strs:
        bfset = flip_bloom_filter(signature, bf_len, num_hash_funct)
        # union indices that have been flipped 1 in candidate bf
        candidate_bloom_filter = candidate_bloom_filter.union(bfset)

    # massage the cbf into a numpy bool array from a set
    bloom_filter_vector = np.zeros(bf_len, dtype=bool)
    bloom_filter_vector[list(candidate_bloom_filter)] = True

    return bloom_filter_vector
