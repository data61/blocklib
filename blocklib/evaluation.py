"""Module to evaluate blocking when ground truth is available."""
from tqdm import tqdm
import logging


def assess_blocks_2party(filtered_reverse_indices, data):
    """Assess pair completeness and reduction ratio of blocking result.

    :ivar filtered_reverse_indices for each data provider, a dict containing the mapping from block id to corresponding record ids.
    :ivar data: a list of lists of entity_ids for 2 data providers
    """
    # currently just support for two party
    dp1_signature, dp2_signature = filtered_reverse_indices
    dp1_data, dp2_data = data

    keys = set(dp1_signature.keys()).intersection(dp2_signature.keys())
    num_comparisons = 0
    found_matches = set()

    for key in tqdm(keys, desc='assessing blocks', total=len(keys), unit='key'):
        dp1_recs = dp1_signature.get(key, None)
        dp2_recs = dp2_signature.get(key, None)
        if dp1_recs is None or dp2_recs is None:
            continue
        num_comparisons += len(dp1_recs) * len(dp2_recs)

        found_matches.update(set(dp1_data[rec] for rec in dp1_recs).intersection(dp2_data[rec] for rec in dp2_recs))

    num_full_comparison = len(dp1_data) * len(dp2_data)
    if num_full_comparison == 0:
        raise ValueError('There are not records in the provided data. Therefore we cannot assess the blocking result.')

    entity1 = set(dp1_data)
    entity2 = set(dp2_data)
    num_all_true_matches = len(entity1.intersection(entity2))

    # pair completeness is the "recall" before matching stage
    rr = 1.0 - num_comparisons / num_full_comparison
    if len(found_matches) == 0:
        logging.warning("Pair completeness is zero, because there are no true matches in the provided data.")
        pc = 0
    else:
        pc = len(found_matches) / num_all_true_matches
    return rr, pc
