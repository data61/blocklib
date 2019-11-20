import numpy as np


def assess_blocks_2party(filtered_reverse_indices, data):
    """Assess pair completeness and reduction ratio of blocking result.

    :ivar filtered_reverse_indices for each data provider, a dict containing the mapping from block id to corresponding record ids.
    :ivar data for each data provider, a list of tuples which only contains entity ID
    """
    # currently just support for two party
    dp1_signature, dp2_signature = filtered_reverse_indices
    dp1_data, dp2_data = data

    cand_pairs = {}  # key is record id of data provider1 and value is list of record ids from data provider 2
    num_block_true_matches = 0
    num_block_false_matches = 0

    keys = set(dp1_signature.keys()).intersection(dp2_signature.keys())
    for key in keys:
        dp1_recs = dp1_signature.get(key, None)
        dp2_recs = dp2_signature.get(key, None)
        if dp1_recs is None or dp2_recs is None:
            continue
        for d1 in dp1_recs:
            d1_entity = dp1_data[d1][0]
            d1_cache = cand_pairs.get(d1_entity, set())
            for d2 in dp2_recs:
                d2_entity = dp2_data[d2][0]
                if d2_entity not in d1_cache:
                    d1_cache.add(d2_entity)
                    if d2_entity == d1_entity:
                        num_block_true_matches += 1
                    else:
                        num_block_false_matches += 1
            cand_pairs[d1_entity] = d1_cache

    num_cand_rec_pairs = num_block_true_matches + num_block_false_matches
    total_rec = len(dp1_data) * len(dp2_data)

    entity1 = [r[0] for r in dp1_data]
    entity2 = [r[0] for r in dp2_data]
    num_all_true_matches = len(np.intersect1d(entity1, entity2))

    # pair completeness is the "recall" before matching stage
    rr = 1.0 - float(num_cand_rec_pairs) / total_rec
    pc = float(num_block_true_matches) / num_all_true_matches
    print('rr = {}'.format(round(rr, 4)))
    print('pc = {}'.format(round(pc, 4)))
    return rr, pc
