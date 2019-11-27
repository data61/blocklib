import pytest
from blocklib import generate_blocks_2party, generate_reverse_blocks
from blocklib import generate_candidate_blocks, flip_bloom_filter


class TestBlocksGenerator:

    def test_candidate_block_type(self):
        """Test throw of type error when passing wrong candidate block types."""
        with pytest.raises(TypeError):
            generate_blocks_2party([{'Fr': [1, 2]}, {'Jo': [3, 4]}])


    def test_generate_reverse_block(self):
        """Test generating reverse block."""
        reversed_indices = [
            {'Fr': ['r1', 'r2'],
             'Jo': ['r3', 'r4']},
            {'Li': [1, 2, 3],
             'Xu': [2, 3, 4]}
        ]
        record_to_blocks = generate_reverse_blocks(reversed_indices)
        assert record_to_blocks[0] == {'r1': ['Fr'], 'r2': ['Fr'], 'r3': ['Jo'], 'r4': ['Jo']}
        assert record_to_blocks[1] == {1: ['Li'], 2: ['Li', 'Xu'], 3: ['Li', 'Xu'], 4: ['Xu']}

    def test_lambdafold(self):
        """Test block generator for PPRLLambdaFold method."""
        config = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "num-hash-funcs": 500,
            "K": 30,
            "random_state": 0,
            "record-id-col": 0,
        }
        blocking_config = {'type': 'lambda-fold',
                           'version': 1,
                           'config': config}
        # party Alice
        records_alice = [['id1', "Joyce", "Wang"],
                         ['id2', "Fred", "Yu"]]
        # party Bob
        records_bob = [['id3', "Joyce", "Wang"],
                       ['id4', "Lindsay", "Lin"]]
        # generate candidate blocks
        candidate_obj_alice = generate_candidate_blocks(records_alice, blocking_config)
        candidate_obj_bob = generate_candidate_blocks(records_bob, blocking_config)

        # blocks generator
        filtered_records = generate_blocks_2party([candidate_obj_alice, candidate_obj_bob])
        filtered_alice = filtered_records[0]
        filtered_bob = filtered_records[1]
        assert list(filtered_alice.values()) == [['id1'], ['id1'], ['id1'], ['id1'], ['id1']]
        assert list(filtered_bob.values()) == [['id3'], ['id3'], ['id3'], ['id3'], ['id3']]

    def test_psig(self):
        """Test block generator for PPRLPsig method."""
        data1 = [('id1', 'Joyce', 'Wang', 'Ashfield'),
                 ('id2', 'Joyce', 'Hsu', 'Burwood'),
                 ('id3', 'Joyce', 'Shan', 'Lewishm'),
                 ('id4', 'Fred', 'Yu', 'Strathfield'),
                 ('id5', 'Fred', 'Zhang', 'Chippendale'),
                 ('id6', 'Lindsay', 'Jone', 'Narwee')]
        data2 = [('4', 'Fred', 'Yu', 'Strathfield'),
                 ('5', 'Fred', 'Zhang', 'Chippendale'),
                 ('6', 'Li', 'Jone', 'Narwee')]

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
        filtered_alice = filtered_records[0]
        filtered_bob = filtered_records[1]

        expected_bf_sets = {}
        for string in ['Fr', 'Fred', 'Li']:
            bf_set = flip_bloom_filter(string, config['blocking-filter']['bf-len'],
                                       config['blocking-filter']['number-hash-functions'])
            expected_bf_sets[tuple(bf_set)] = True

        assert all(key in expected_bf_sets for key in filtered_alice)
        assert filtered_alice.keys() == filtered_bob.keys()

