import sys

from typing import Dict, Sequence, Tuple, Type, List, Optional, TextIO
from .pprlindex import PPRLIndex, ReversedIndexResult
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .validation import validate_blocking_schema


PPRLSTATES = {
    "p-sig": PPRLIndexPSignature,
    "lambda-fold": PPRLIndexLambdaFold,
}  # type: Dict[str, Type[PPRLIndex]]


class CandidateBlockingResult:
    """Object for holding candidate blocking results.

    :ivar blocks: a dictionary that contains a mapping from the block ID to the record IDs in that block.
    :ivar state: A PPRLIndex state that contains the configuration of blocking
    :ivar stats: a dictionary containing the summary statistics of the generated blocks"""

    def __init__(self, blocking_result: ReversedIndexResult, state: PPRLIndex):
        """
        Initialise a blocking result object.
        :param blocking_result: A ReversedIndexResult object, containing the blocks and corresponding statistics
        :param state: A PPRLIndex state that contains configuration of blocking
        """
        self.blocks = blocking_result.reversed_index
        self.state = state
        self.stats = blocking_result.stats

    def print_summary_statistics(self, output: TextIO = sys.stdout, round_ndigits: int = 4):
        """
        Print the summary statistics of this candidate blocking result to 'output'.
        :param output: a file like object to write to. Defaults to sys.stdout
        :param round_ndigits: round floating point numbers to ndigits precision. Defaults to 4.
        """
        def print_stats(stats: Dict, out: TextIO):
            out.write('\tNumber of Blocks:   {}\n'.format(stats['num_of_blocks']))
            out.write('\tMinimum Block Size: {}\n'.format(stats['min_size']))
            out.write('\tMaximum Block Size: {}\n'.format(stats['max_size']))
            out.write('\tAverage Block Size: {}\n'.format(round(stats['avg_size'], round_ndigits)))
            out.write('\tMedian Block Size:  {}\n'.format(stats['med_size']))
            out.write('\tStandard Deviation of Block Size:  {}\n'.format(round(stats['std_size'], round_ndigits)))
            if 'coverage' in stats:
                out.write('\tCoverage:           {}%\n'.format(round(stats['coverage'] * 100, 2)))

        output.write('Statistics for the generated blocks:\n')
        print_stats(self.stats, output)
        if 'statistics_per_strategy' in self.stats:
            output.write('Individual statistics for each strategy:\n')
            for stat in self.stats['statistics_per_strategy']:
                output.write('Strategy: {}\n'.format(stat['strategy_idx']))
                print_stats(stat, output)


def generate_candidate_blocks(data: Sequence[Tuple[str, ...]],
                              blocking_schema: Dict,
                              header: Optional[List[str]] = None) -> CandidateBlockingResult:
    """
    :param data: list of tuples E.g. ('0', 'Kenneth Bain', '1964/06/17', 'M')
    :param blocking_schema:
        A description of how the signatures should be generated.
        See :ref:`blocking-schema`
    :param header: column names (optional)
        Program should throw exception if block features are string but header is None

    :return: A 2-tuple containing
        A list of "signatures" per record in data.
        Internal state object from the signature generation (or None).
    """
    blocking_model = validate_blocking_schema(blocking_schema)

    # extract algorithm and its config
    algorithm = blocking_model.type.value
    config = blocking_model.config

    # check if blocking features are column index or feature name
    blocking_features = config.blocking_features
    feature_type = type(blocking_features[0])
    error_msg = 'All feature types should be the same - either feature name or feature index'
    assert all(type(x) == feature_type for x in blocking_features[1:]), error_msg

    # header should not be None if blocking features are string
    if feature_type == str:
        assert header, 'Header must not be None if blocking features are string'

    if algorithm in PPRLSTATES:
        state = PPRLSTATES[algorithm](config)
        reversed_index_result = state.build_reversed_index(data, header)
        candidate_block_obj = CandidateBlockingResult(reversed_index_result, state)

    else:
        raise NotImplementedError('The algorithm {} is not supported yet'.format(algorithm))

    return candidate_block_obj
