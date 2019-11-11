import unittest
from blocklib import PPRLIndexLambdaFold


class TestLambdaFold(unittest.TestCase):

    def test_config(self):
        """Test lambda-fold configuration."""
        with self.assertRaises(ValueError):
            config = {
                "blocking-features": [1, 2],
                "Lambda": 38,
                "bf-len": 2000,
                "K": 30
            }
            PPRLIndexLambdaFold(config)

    def test_record_to_bf(self):
        """Test creating a bloom filter from one record."""
        config = {
                "blocking-features": [1, 2],
                "Lambda": 38,
                "bf-len": 2000,
                "num-hash-funcs": 2,
                "K": 30
        }
        lambdafold = PPRLIndexLambdaFold(config)
        record = [1, 'Xu', 'Li']
        bloom_filter = lambdafold.__record_to_bf__(record)
        assert sum(bloom_filter) == 6

    def test_build_inverted_index(self):
        """Test building the inverted index."""
        config = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "num-hash-funcs": 1000,
            "K": 30
        }
        lambdafold = PPRLIndexLambdaFold(config)
        data = [[1, 'Xu', 'Li'],
                [2, 'Fred', 'Yu']]
        invert_index = lambdafold.build_inverted_index(data, 0)
        assert len(invert_index) == 5 * 2
        assert all([len(k) == 30 for k in invert_index])
        assert all([len(v) == 1 for v in invert_index.values()])

        # build with row index
        invert_index = lambdafold.build_inverted_index(data)
        assert len(invert_index) == 5 * 2
        assert all([len(k) == 30 for k in invert_index])
        assert all([len(v) == 1 for v in invert_index.values()])
