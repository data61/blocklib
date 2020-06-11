import pytest

from blocklib import generate_candidate_blocks
from blocklib import PPRLIndexPSignature
from blocklib import flip_bloom_filter

data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
        ('id2', 'Joyce', 'Hsu', 'Burwood'),
        ('id3', 'Joyce', 'Shan', 'Lewishm'),
        ('id4', 'Fred', 'Yu', 'Strathfield'),
        ('id5', 'Fred', 'Zhang', 'Chippendale'),
        ('id6', 'Lindsay', 'Jone', 'Narwee')]


class TestCandidateBlockGenerator:

    def test_generate_candidate_blocks_assertion(self):
        global data

        # test when type of blocking is not specified
        with pytest.raises(ValueError):
            block_config = {'version': 1, 'config': {}}
            generate_candidate_blocks(data, block_config)

        # test when type of blocking is not implemented
        with pytest.raises(NotImplementedError):
            block_config = {'type': 'fancy-block', 'version': 1, 'config': {}}
            generate_candidate_blocks(data, block_config)

        # test when config of blocking is not specified
        with pytest.raises(ValueError):
            block_config = {'type': 'p-sig', 'version': 1}
            generate_candidate_blocks(data, block_config)

    def test_generate_candidate_blocks_psig(self):
        """Test generation of candidate blocks for p-sig."""
        global data
        num_hash_funcs = 4
        bf_len = 2048
        config = {
            "blocking_features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.0,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": num_hash_funcs,
                "bf-len": bf_len,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature-idx": 1}
                ]
            ]
        }

        block_config = {'type': 'p-sig',
                        'version': 1,
                        'config': config}
        candidate_block_obj = generate_candidate_blocks(data, block_config)
        bf_set_fred = str(tuple(flip_bloom_filter('Fred', bf_len, num_hash_funcs)))
        bf_set_lindsay = str(tuple(flip_bloom_filter('Lindsay', bf_len, num_hash_funcs)))
        assert candidate_block_obj.blocks == {bf_set_fred: ['id4', 'id5'], bf_set_lindsay: ['id6']}
