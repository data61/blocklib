from enum import Enum
from typing import cast, Union, List, Optional

from typing_extensions import Literal
from pydantic import BaseModel, Field

from .constrained_types import UnitFloat, PositiveInt
from .shared_blocking_config import BlockingConfigBase


class PSigFilterConfigBase(BaseModel):
    type: str


class PSigFilterRatioConfig(PSigFilterConfigBase):
    type: Literal['ratio']
    max: UnitFloat
    min: UnitFloat = cast(UnitFloat, 0.0)


class PSigFilterCountConfig(PSigFilterConfigBase):
    type: Literal['count']
    max: PositiveInt
    min: PositiveInt


class PSigBlockingBFFilterConfig(BaseModel):
    type: Literal['bloom filter']
    number_of_hash_functions: int = Field(..., alias='number-hash-functions')
    bloom_filter_length: int = Field(..., alias='bf-len')
    compress_block_key: Optional[bool] = Field(False, alias='compress-block-key')


class PSigSignatureTypes(str, Enum):
    chars_at = 'characters-at'
    feature_value = 'feature-value'
    metaphone = 'metaphone'


class PSigSignatureSpecBase(BaseModel):
    type: str
    feature: Union[int, str]


class PSigCharsAtSignatureConfig(BaseModel):
    pos: List[Union[PositiveInt, str]]


class PSigCharsAtSignatureSpec(PSigSignatureSpecBase):
    type: Literal[PSigSignatureTypes.chars_at] = Field(..., name='type', alias='type')
    config: PSigCharsAtSignatureConfig


class PSigMetaphoneSignatureSpec(PSigSignatureSpecBase):
    type: Literal[PSigSignatureTypes.metaphone]


class PSigFeatureValueSignatureSpec(PSigSignatureSpecBase):
    type: Literal[PSigSignatureTypes.feature_value] = Field(..., name='type', alias='type')


PSigSignatureModel = List[Union[
    PSigCharsAtSignatureSpec,
    PSigMetaphoneSignatureSpec,
    PSigFeatureValueSignatureSpec
]]


class PSigConfig(BlockingConfigBase):
    filter: Union[PSigFilterRatioConfig, PSigFilterCountConfig]
    blocking_filter: PSigBlockingBFFilterConfig = Field(..., alias='blocking-filter')
    signatures: List[PSigSignatureModel] = Field(..., alias='signatureSpecs')
