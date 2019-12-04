from blocklib import assess_blocks_2party, generate_blocks_2party, generate_candidate_blocks


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
        "blocking_features": [1],
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
                {"type": "feature-value", "feature-idx": 1}
            ],
            [
                {"type": "characters-at", "config": {"pos": ["0:2"]}, "feature-idx": 1},
            ]
        ]

    }

    blocking_config = {'type': 'p-sig',
                       'version': 1,
                       'config': config}

    # generate candidate blocks
    candidate_obj_alice = generate_candidate_blocks(data1, blocking_config)
    candidate_obj_bob = generate_candidate_blocks(data2, blocking_config)

    # blocks generator
    filtered_records = generate_blocks_2party([candidate_obj_alice, candidate_obj_bob])

    # assess blocks
    subdata1 = [r[0] for r in data1]
    subdata2 = [r[0] for r in data2]
    rr, pc = assess_blocks_2party(filtered_records, [subdata1, subdata2])

    # compare expected and actual rr pc
    # final blocks should have blocking key Fr, Li and Fred
    num_all_comparison = len(data1) * len(data2)
    num_reduced_comparison = 2 + 1 + 2
    expected_rr = 1 - float(num_reduced_comparison / num_all_comparison)
    expected_pc = 1

    assert rr == expected_rr
    assert pc == expected_pc