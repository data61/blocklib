import unittest
from blocklib import PPRLIndexPSignature, flip_bloom_filter

data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
        ('id2', 'Joyce', 'Hsu', 'Burwood'),
        ('id3', 'Joyce', 'Shan', 'Lewishm'),
        ('id4', 'Fred', 'Yu', 'Strathfield'),
        ('id5', 'Fred', 'Zhang', 'Chippendale'),
        ('id6', 'Lindsay', 'Jone', 'Narwee')]


class TestPSig(unittest.TestCase):

    def test_config(self):
        """Test p-sig configuration."""
        with self.assertRaises(ValueError):
            config = {
                "blocking-features": [1],
                "filter": {
                    "type": "ratio",
                    "max": 0.02,
                    "min": 0.001,
                },
                "blocking-filter": {
                    "type": "bloom filter",
                    "number-hash-functions": 4,
                    "bf-len": 4096,
                },
            }
            PPRLIndexPSignature(config)

    def test_combine_blocks_in_blocking_filter(self):
        """During blocking filter generation, if there is an index collision, then we should combine the blocks
        of the colliding signatures."""
        data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
                ('id2', 'Brian', 'Hsu', 'Burwood')]
        config = {
            "blocking-features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 1.0,
                "min": 0.0,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 1,
                "bf-len": 1,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 1}
                ]
            ]

        }
        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data)
        assert len(reversed_index) == 1
        assert set(next(iter(reversed_index.values()))) == {'id1', 'id2'}

    def test_build_reversed_index(self):
        """Test build revert index."""
        global data
        config = {
            "blocking-features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 1}
                ]
            ]
        }
        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data, verbose=True)
        bf_set = tuple(flip_bloom_filter("0_Fred", config['blocking-filter']['bf-len'],
                                         config['blocking-filter']['number-hash-functions']))
        assert reversed_index == {str(bf_set): ['id4', 'id5']}

    def test_build_reversed_index_feature_name(self):
        """Test build revert index."""
        global data
        header = ['ID', 'firstname', 'lastname', 'suburb']
        config = {
            "blocking-features": ['firstname'],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 'firstname'}
                ]
            ]

        }

        psig = PPRLIndexPSignature(config)
        reversed_index = psig.build_reversed_index(data, verbose=True, header=header)
        bf_set = tuple(flip_bloom_filter("0_Fred", config['blocking-filter']['bf-len'],
                                         config['blocking-filter']['number-hash-functions']))
        assert reversed_index == {str(bf_set): ['id4', 'id5']}

        # test if results with column name and column index are the same
        config_index = {
            "blocking-features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 1}
                ]
            ]
        }
        psig_col_index = PPRLIndexPSignature(config_index)
        reversed_index_col_index = psig_col_index.build_reversed_index(data, verbose=True, header=header)
        assert reversed_index == reversed_index_col_index

    def test_inconsistent_header(self):
        """Test when header dimension is not consistent with data dimension."""
        global data
        header = ['ID', 'firstname', 'lastname', 'suburb', 'postcode']  # extra feature - postcode
        config = {
            "blocking-features": ['firstname'],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 'firstname'}
                ]
            ]
        }
        psig = PPRLIndexPSignature(config)
        with self.assertRaises(AssertionError):
            psig.build_reversed_index(data, verbose=True, header=header)

    def test_header_with_feature_type(self):
        """Test different combination of header and feature column type."""
        global data
        header = ['ID', 'firstname', 'lastname', 'suburb']
        config_name = {
            "blocking-features": ['firstname'],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 'firstname'}
                ]
            ]
        }
        config_index = {
            "blocking-features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 1}
                ]
            ]
        }
        psig_index = PPRLIndexPSignature(config_index)
        psig_name = PPRLIndexPSignature(config_name)
        # case1 header is given and feature type is column names
        reversed_index1 = psig_name.build_reversed_index(data, verbose=True, header=header)
        # case2 header is given and feature type is index
        reversed_index2 = psig_index.build_reversed_index(data, verbose=True, header=header)
        # case3 header is not given and feature type is index
        reversed_index3 = psig_index.build_reversed_index(data, verbose=True, header=None)

        # above 3 cases should give exactly same results
        assert reversed_index1 == reversed_index2
        assert reversed_index2 == reversed_index3

