from blocklib import assess_blocks_2party, generate_blocks, generate_candidate_blocks
import pytest


def test_assess_blocks_2party():
    """Test 2-party blocking assessment."""
    data1 = [('id1', 'Joyce', 'Wang', 'Ashfield'),
             ('id2', 'Joyce', 'Hsu', 'Burwood'),
             ('id3', 'Joyce', 'Shan', 'Lewishm'),
             ('id4', 'Fred', 'Yu', 'Strathfield'),
             ('id5', 'Fred', 'Zhang', 'Chippendale'),
             ('id6', 'Lindsay', 'Jone', 'Narwee')]
    data2 = [('id4', 'Fred', 'Yu', 'Strathfield'),
             ('id8', 'Fredrick', 'Zhang', 'Chippendale'),
             ('id9', 'Li', 'Jone', 'Narwee')]

    config = {
        "blocking-features": [1],
        "filter": {
            "type": "count",
            "max": 5,
            "min": 0,
        },
        "blocking-filter": {
            "type": "bloom filter",
            "number-hash-functions": 20,
            "bf-len": 2048,
        },
        "signatureSpecs": [
            [
                {"type": "feature-value", "feature": 1}
            ],
            [
                {"type": "characters-at", "config": {"pos": ["0:2"]}, "feature": 1},
            ]
        ]

    }

    blocking_config = {'type': 'p-sig',
                       'version': 1,
                       'config': config}

    def get_filtered_records(data_a, data_b):
        # generate candidate blocks
        candidate_obj_alice = generate_candidate_blocks(data_a, blocking_config)
        candidate_obj_bob = generate_candidate_blocks(data_b, blocking_config)
        # blocks generator
        return generate_blocks([candidate_obj_alice, candidate_obj_bob], K=2)

    # assess blocks
    subdata1 = [r[0] for r in data1]
    subdata2 = [r[0] for r in data2]
    rr, pc = assess_blocks_2party(get_filtered_records(data1, data2), [subdata1, subdata2])

    # compare expected and actual rr pc
    # final blocks should have blocking key Fr, Li and Fred
    num_all_comparison = len(data1) * len(data2)
    num_reduced_comparison = 2 + 1 + 2
    expected_rr = 1 - float(num_reduced_comparison / num_all_comparison)
    expected_pc = 1

    assert rr == expected_rr
    assert pc == expected_pc

    data2_b = data2[1:]  # no true matches between data1 and data2_b
    _, pc = assess_blocks_2party(get_filtered_records(data1, data2_b), [data1, data2_b])
    assert pc == 0

    with pytest.raises(ValueError):
        assess_blocks_2party([{}, {}], [[], []])
