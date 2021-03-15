import pkg_resources
from .pprlindex import PPRLIndex
from .pprlpsig import PPRLIndexPSignature
from .pprllambdafold import PPRLIndexLambdaFold
from .signature_generator import generate_signatures
from .blocks_generator import generate_blocks, generate_reverse_blocks
from .validation import validate_blocking_schema
from .candidate_blocks_generator import generate_candidate_blocks
from .encoding import generate_bloom_filter, flip_bloom_filter
from .evaluation import assess_blocks_2party


__version__ = pkg_resources.get_distribution('blocklib').version
