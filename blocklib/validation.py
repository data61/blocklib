import json
from typing import Dict
import jsonschema
import pathlib


def load_schema(file_name: str):
    path = pathlib.Path(__file__).parent / 'schemas' / file_name

    # schema_bytes = pkgutil.get_data('anonlinkclient', 'docs/schemas/{}'.format(file_name))
    with open(str(path.resolve()), 'rt') as schema_file:
        try:
            return json.load(schema_file)
        except json.decoder.JSONDecodeError as e:
            raise ValueError("Invalid schema") from e



def validate_signature_config(config: Dict):
    schema = load_schema('signature-config-schema.json')
    try:
        jsonschema.validate(config, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ValueError('The signature config is not valid.\n\n' + str(e)) from e
