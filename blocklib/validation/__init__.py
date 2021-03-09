import json
import pathlib
from enum import Enum
from typing import Dict, Union

from pydantic import BaseModel, Field, validator, ValidationError

from blocklib.validation.constrained_types import PositiveInt, UnitFloat
from blocklib.validation.lambda_fold_validation import LambdaConfig
from blocklib.validation.psig_validation import PSigConfig, PSigSignatureModel, PSigBlockingBFFilterConfig, \
    PSigCharsAtSignatureSpec, PSigMetaphoneSignatureSpec


class BlockingSchemaTypes(str, Enum):
    psig = 'p-sig'
    lambdafold = 'lambda-fold'


PPRLIndexConfig = Union[PSigConfig, LambdaConfig]


class BlockingSchemaBaseModel(BaseModel):
    version: int
    type: BlockingSchemaTypes = Field(..., description="Identifier of the blocking type")
    config: Dict


class BlockingSchemaModel(BaseModel):
    version: int
    type: BlockingSchemaTypes = Field(..., description="Identifier of the blocking type")
    config: Union[PSigConfig, LambdaConfig]

    @validator('config', pre=True, always=True, each_item=False)
    def validate_config(cls, config_to_validate, values):
        return cls.config_gen(config_to_validate, values)

    @classmethod
    def config_gen(cls, config_to_validate, values) -> Union[PSigConfig, LambdaConfig]:
        # TODO rework after https://github.com/samuelcolvin/pydantic/issues/619
        if not isinstance(config_to_validate, dict):
            raise ValueError(f'invalid blocking config, not dict')
        blocking_type = values.get('type')

        if blocking_type == BlockingSchemaTypes.psig:
            return PSigConfig(**config_to_validate)
        elif blocking_type == BlockingSchemaTypes.lambdafold:
            return LambdaConfig(**config_to_validate)
        else:
            raise ValueError("Unsupported blocking type")


def load_schema(file_name: str):
    path = pathlib.Path(__file__).parent / 'schemas' / file_name

    # schema_bytes = pkgutil.get_data('anonlinkclient', 'docs/schemas/{}'.format(file_name))
    with open(str(path.resolve()), 'rt') as schema_file:
        try:
            return json.load(schema_file)
        except json.decoder.JSONDecodeError as e:
            raise ValueError("Invalid schema") from e


def validate_signature_config(config: Dict) -> BlockingSchemaModel:
    # First we check the top level structure
    try:
        BlockingSchemaBaseModel.parse_obj(config)
    except ValidationError as e:
        raise ValueError('The signature config is not valid.\n\n' + str(e)) from e

    # Validate blocking schema with pydantic
    # Note we already know the config contains a type so we could
    # directly create a PSig or LambdaFold type
    return BlockingSchemaModel.parse_obj(config)
