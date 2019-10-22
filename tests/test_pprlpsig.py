import unittest
from blocklib import PPRLIndexPSignature


class TestPSig(unittest.TestCase):

    def test_config(self):
        """Test p-sig configuration."""
        with self.assertRaises(ValueError):
            config = {'num_hash_funct': 20,
                      'bf_len': 2048,
                      'attr_select_list': [1],
                      'max_occur_ratio': 0.015}
            psig = PPRLIndexPSignature(config)

    def test_build_inverted_index(self):
        """Test build revert index."""
        data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
                ('id2', 'Joyce', 'Hsu', 'Burwood'),
                ('id3', 'Joyce', 'Shan', 'Lewishm'),
                ('id4', 'Fred', 'Yu', 'Strathfield'),
                ('id5', 'Fred', 'Zhang', 'Chippendale'),
                ('id6', 'Lindsay', 'Jone', 'Narwee')]
        config = {'num_hash_funct': 20,
                  'bf_len': 2048,
                  'signature_strategy': 'feature-value',
                  'signature_strategy_config': {},
                  'attr_select_list': [1],
                  'max_occur_ratio': 0.5,
                  'min_occur_ratio': 0.2}
        psig = PPRLIndexPSignature(config)
        invert_index, _ = psig.build_inverted_index(data, rec_id_col=0)
        assert invert_index == {'Fred': ['id4', 'id5']}
