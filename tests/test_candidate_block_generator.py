import unittest
import pytest

from blocklib import generate_candidate_blocks
from blocklib import PPRLIndexPSignature

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
                "number_hash_functions": 20,
                "bf_len": 2048,
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
        assert candidate_block_obj.blocks == {'Fred': ['id4', 'id5'], 'Lindsay': ['id6']}

        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data)
        cbf, cbf_map = psig.generate_block_filter(reversed_index)
        assert all(candidate_block_obj.extra['candidate_block_filter'] == cbf)
        assert candidate_block_obj.extra['cbf_map'] == cbf_map
