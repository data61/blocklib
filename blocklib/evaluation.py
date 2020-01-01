"""Module to evaluate blocking when ground truth is available."""
from tqdm import tqdm


def assess_blocks_2party(filtered_reverse_indices, data, print_result=False):
    """Assess pair completeness and reduction ratio of blocking result.

    :ivar filtered_reverse_indices for each data provider, a dict containing the mapping from block id to corresponding record ids.
    :ivar data: a list of lists of entity_ids for 2 data providers
    """
    # currently just support for two party
    dp1_signature, dp2_signature = filtered_reverse_indices
    dp1_data, dp2_data = data

    cand_pairs = {}  # key is record id of data provider1 and value is list of record ids from data provider 2
    num_block_true_matches = 0
    num_block_false_matches = 0

    keys = set(dp1_signature.keys()).intersection(dp2_signature.keys())
    for key in tqdm(keys, desc='assessing blocks', total=len(keys), unit='key'):
        dp1_recs = dp1_signature.get(key, None)
        dp2_recs = dp2_signature.get(key, None)
        if dp1_recs is None or dp2_recs is None:
            continue
        for d1 in dp1_recs:
            d1_entity = dp1_data[d1]
            d1_cache = cand_pairs.get(d1_entity, set())
            for d2 in dp2_recs:
                d2_entity = dp2_data[d2]
                if d2_entity not in d1_cache:
                    d1_cache.add(d2_entity)
                    if d2_entity == d1_entity:
                        num_block_true_matches += 1
                    else:
                        num_block_false_matches += 1
            cand_pairs[d1_entity] = d1_cache

    num_cand_rec_pairs = num_block_true_matches + num_block_false_matches
    total_rec = len(dp1_data) * len(dp2_data)

    entity1 = set(dp1_data)
    entity2 = set(dp2_data)
    num_all_true_matches = len(entity1.intersection(entity2))

    # pair completeness is the "recall" before matching stage
    rr = 1.0 - float(num_cand_rec_pairs) / total_rec
    pc = float(num_block_true_matches) / num_all_true_matches
    if print_result:
        print('rr = {}'.format(round(rr, 4)))
        print('pc = {}'.format(round(pc, 4)))
    return rr, pc
