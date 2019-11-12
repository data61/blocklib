import unittest
from blocklib import generate_blocks
from blocklib import PPRLIndexLambdaFold


class TestBlocksGenerator(unittest.TestCase):

    def test_lambdafold(self):
        """Test block generator for PPRLLambdaFold method."""
        config = {
            "blocking-features": [1, 2],
            "Lambda": 5,
            "bf-len": 2000,
            "num-hash-funcs": 500,
            "K": 30,
            "random_state": 0
        }
        blocking_config = {'type': 'lambda-fold',
                           'config': config}
        # party Alice
        records_alice = [[1, "Joyce", "Wang"],
                         [2, "Fred", "Yu"]]
        lambdafold_alice = PPRLIndexLambdaFold(config)
        reversed_index_alice = lambdafold_alice.build_inverted_index(records_alice, 0)

        # party Bob
        records_bob = [[3, "Joyce", "Wang"],
                       [4, "Lindsay", "Lin"]]
        lambda_bob = PPRLIndexLambdaFold(config)
        reversed_index_bob = lambda_bob.build_inverted_index(records_bob, 0)

        print("Number of keys in common={}".format(len(set(reversed_index_alice.keys()).intersection(set(reversed_index_bob.keys())))))

        # blocks generator
        filtered_records = generate_blocks([reversed_index_alice, reversed_index_bob], blocking_config)
        filtered_alice = filtered_records[0]
        filtered_bob = filtered_records[1]
        assert list(filtered_alice.values()) == [[1], [1], [1], [1], [1]]
        assert list(filtered_bob.values()) == [[3], [3], [3], [3], [3]]



