import unittest
from blocklib import PPRLIndexPSignature


class TestPSig(unittest.TestCase):

    def test_config(self):
        """Test p-sig configuration."""
        with self.assertRaises(ValueError):
            config = {
                "blocking_features": [1],
                "filter": {
                    "type": "ratio",
                    "max-occur-ratio": 0.02,
                    "min-occur-ratio": 0.001,
                },
                "blocking-filter": {
                    "type": "bloom filter",
                    "number_hash_functions": 4,
                    "bf_len": 4096,
                },
            }
            PPRLIndexPSignature(config)

    def test_build_reversed_index(self):
        """Test build revert index."""
        data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
                ('id2', 'Joyce', 'Hsu', 'Burwood'),
                ('id3', 'Joyce', 'Shan', 'Lewishm'),
                ('id4', 'Fred', 'Yu', 'Strathfield'),
                ('id5', 'Fred', 'Zhang', 'Chippendale'),
                ('id6', 'Lindsay', 'Jone', 'Narwee')]
        config = {
            "blocking_features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max-occur-ratio": 0.5,
                "min-occur-ratio": 0.2,
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
        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data)
        assert reversed_index == {'Fred': ['id4', 'id5']}
