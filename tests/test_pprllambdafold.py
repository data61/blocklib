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
        bloom_filter = lambdafold.__record_to_bf__(record, config['blocking-features'])
        assert sum(bloom_filter) == 6

    def test_build_reversed_index(self):
        """Test building the inverted index."""
        config_index = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "record-id-col": 0,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": False
        }
        lambdafold = PPRLIndexLambdaFold(config_index)
        data = [[1, 'Xu', 'Li'],
                [2, 'Fred', 'Yu']]
        reversed_index_result = lambdafold.build_reversed_index(data)
        assert len(reversed_index_result.reversed_index) == 5 * 2
        assert all([len(k) == 31 for k in reversed_index_result.reversed_index])
        assert all([len(v) == 1 for v in reversed_index_result.reversed_index.values()])
        stats = reversed_index_result.stats
        assert stats['num_of_blocks'] == 10
        assert stats['min_size'] == 1
        assert stats['max_size'] == 1
        assert len(stats) >= 7

        # build with row index
        del config_index['record-id-col']
        lambdafold = PPRLIndexLambdaFold(config_index)
        reversed_index_result = lambdafold.build_reversed_index(data)
        assert len(reversed_index_result.reversed_index) == 5 * 2
        assert all([len(k) == 31 for k in reversed_index_result.reversed_index])
        assert all([len(v) == 1 for v in reversed_index_result.reversed_index.values()])

        # build given headers
        config_name = {
            "blocking-features": ['firstname', 'lastname'],
            "Lambda": 5,
            "bf-len": 2000,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": False
        }
        header = ['ID', 'firstname', 'lastname']
        lambdafold_use_colname = PPRLIndexLambdaFold(config_name)
        reversed_index_result_use_colname = lambdafold_use_colname.build_reversed_index(data, header=header)
        assert len(reversed_index_result_use_colname.reversed_index) == 5 * 2
        assert all([len(k) == 31 for k in reversed_index_result_use_colname.reversed_index])
        assert all([len(v) == 1 for v in reversed_index_result_use_colname.reversed_index.values()])
        assert reversed_index_result == reversed_index_result_use_colname

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
        with clk_filepath.open() as f:
            data = json.load(f)['clks']\

        reversed_index_result = lambdafold.build_reversed_index(data)
        assert len(reversed_index_result.reversed_index) == 5 * 4
        assert all([len(k) == 31 for k in reversed_index_result.reversed_index])

    def test_header_with_feature_type(self):
        """Test different combination of header and feature column type."""
        data = [('id1', 'Joyce', 'Wang', 'Ashfield'),
                ('id2', 'Joyce', 'Hsu', 'Burwood'),
                ('id3', 'Joyce', 'Shan', 'Lewishm'),
                ('id4', 'Fred', 'Yu', 'Strathfield'),
                ('id5', 'Fred', 'Zhang', 'Chippendale'),
                ('id6', 'Lindsay', 'Jone', 'Narwee')]
        header = ['ID', 'firstname', 'lastname', 'suburb']
        config_name = {
            "blocking-features": ['firstname', 'lastname'],
            "Lambda": 5,
            "bf-len": 2000,
            "record-id-col": 0,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": False
        }
        config_index = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "record-id-col": 0,
            "num-hash-funcs": 1000,
            "K": 30,
            "random_state": 0,
            "input-clks": False
        }
        lambda_fold_index = PPRLIndexLambdaFold(config_index)
        lambda_fold_name = PPRLIndexLambdaFold(config_name)
        # case1 header is given and feature type is column names
        reversed_index1 = lambda_fold_name.build_reversed_index(data, verbose=True, header=header)
        # case2 header is given and feature type is index
        reversed_index2 = lambda_fold_index.build_reversed_index(data, verbose=True, header=header)
        # case3 header is not given and feature type is index
        reversed_index3 = lambda_fold_index.build_reversed_index(data, verbose=True, header=None)

        # above 3 cases should give exactly same results
        assert reversed_index1 == reversed_index2
        assert reversed_index2 == reversed_index3