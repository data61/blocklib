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
        config = {
            "blocking_features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max-occur-ratio": 0.5,
                "min-occur-ratio": 0.0,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
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
        assert candidate_block_obj.blocks == {'Fred': ['id4', 'id5'], 'Lindsay': ['id6']}

        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data)
        cbf, cbf_map = psig.generate_block_filter(reversed_index)
        assert all(candidate_block_obj.extra['candidate_block_filter'] == cbf)
        assert candidate_block_obj.extra['cbf_map'] == cbf_map
