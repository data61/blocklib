import unittest
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


class TestCandidateBlockGenerator(unittest.TestCase):

    def test_generate_candidate_blocks_assertion(self):
        global data
        with pytest.raises(ValueError):
            block_config = {'version': 1, 'config': {}}
            generate_candidate_blocks(data, block_config)

        with pytest.raises(NotImplementedError):
            block_config = {'type': 'fancyblock', 'version': 1, 'config': {}}
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
                "max_occur_ratio": 0.5,
                "min_occur_ratio": 0.0,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number_hash_functions": num_hash_funcs,
                "bf_len": bf_len,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature_idx": 1}
                ]
            ]
        }

        block_config = {'type': 'p-sig',
                        'version': 1,
                        'config': config}
        candidate_block_obj = generate_candidate_blocks(data, block_config)
        bf_set_fred = tuple(flip_bloom_filter('Fred', bf_len, num_hash_funcs))
        bf_set_lindsay = tuple(flip_bloom_filter('Lindsay', bf_len, num_hash_funcs))
        assert candidate_block_obj.blocks == {bf_set_fred: ['id4', 'id5'], bf_set_lindsay: ['id6']}
