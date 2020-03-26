import unittest
import json
from pathlib import Path

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
                "K": 30,
                "random_state": 0,
                "input-clks": False
        }
        lambdafold = PPRLIndexLambdaFold(config)
        record = [1, 'Xu', 'Li']
        bloom_filter = lambdafold.__record_to_bf__(record)
        assert sum(bloom_filter) == 6

    def test_build_reversed_index(self):
        """Test building the inverted index."""
        config = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "record-id-col": 0,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": False
        }
        lambdafold = PPRLIndexLambdaFold(config)
        data = [[1, 'Xu', 'Li'],
                [2, 'Fred', 'Yu']]
        reversed_index = lambdafold.build_reversed_index(data)
        assert len(reversed_index) == 5 * 2
        assert all([len(k) == 31 for k in reversed_index])
        assert all([len(v) == 1 for v in reversed_index.values()])

        # build with row index
        del config['record-id-col']
        lambdafold = PPRLIndexLambdaFold(config)
        reversed_index = lambdafold.build_reversed_index(data)
        assert len(reversed_index) == 5 * 2
        assert all([len(k) == 31 for k in reversed_index])
        assert all([len(v) == 1 for v in reversed_index.values()])

    def test_build_reversed_index_clks(self):
        """Test building the inverted index with CLKs input."""
        config = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "record-id-col": 0,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": True
        }
        lambdafold = PPRLIndexLambdaFold(config)
        clk_filepath = Path(__file__).parent / 'data' / 'small_clk.json'
        with open(clk_filepath, 'r') as f:
            data = json.load(f)['clks']
        reversed_index = lambdafold.build_reversed_index(data)
        assert len(reversed_index) == 5 * 4
        assert all([len(k) == 31 for k in reversed_index])