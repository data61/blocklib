from typing import Optional

from pydantic import Field

from .shared_blocking_config import BlockingConfigBase


class LambdaConfig(BlockingConfigBase):
    Lambda: int = Field(..., description='the degree of redundancy')
    bloom_filter_length: int = Field(..., alias='bf-len')
    number_of_hash_functions: int = Field(..., alias='num-hash-funcs')
    K: int
    block_encodings: bool = Field(...,
                                  alias='input-clks',
                                  description='Input data is CLK rather than PII')
    random_state: int

    #random_state: Optional[int] = Field(None, alias='random-state')