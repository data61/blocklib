import pytest
from blocklib import validate_signature_config
from blocklib.validation import load_schema, BlockingSchemaModel, BlockingSchemaTypes
import tempfile
import json


class TestValidation:

    def test_validate_signature_config(self):
        """Test validation on signature config."""
        config = {
            "type": "p-sig",
            "version": 1,
            "config": {
                "blocking-features": [1],
                "filter": {
                    "type": "ratio",
                    "max": 0.02,
                    "min": 0.00,
                },
                "blocking-filter": {
                    "type": "bloom filter",
                    "number-hash-functions": 4,
                    "bf-len": 2048,
                },
                "signatureSpecs": [
                    [
                        {"type": "characters-at", "config": {"pos": [0]}, "feature": 1},
                        {"type": "characters-at", "config": {"pos": [0]}, "feature": 2},
                    ],
                    [
                        {"type": "metaphone", "feature": 1},
                        {"type": "metaphone", "feature": 2},
                    ]
                ]
            }
        }

        validated_schema = validate_signature_config(config)
        assert isinstance(validated_schema, BlockingSchemaModel)

        # Check we can serialize the object
        validated_json_data = validated_schema.dict()
        # Note we use Python keys with underscores, rather than hyphens:
        assert 'blocking_features' in validated_json_data['config']
        assert 'blocking-features' not in validated_json_data['config']

        # Note the type values are enums:
        assert isinstance(validated_schema.type, BlockingSchemaTypes)
        assert validated_schema.type == BlockingSchemaTypes.psig

        # To get the original JSON keys use `by_alias=True`
        assert 'blocking-features' in validated_schema.config.dict(by_alias=True)

        # We can also export as json
        json_str = validated_schema.json(indent=2, by_alias=True)
        assert 'blocking-features' in json_str

    def test_validate_signature_assertion(self):
        """Test if validation will capture error and throw assertion."""
        config = {"type": "p-sig", "version": 1}
        with pytest.raises(ValueError):
            validate_signature_config(config)

    def test_load_schema(self):
        """Test exception with invalid schema."""
        tmp = tempfile.NamedTemporaryFile()
        wrong_schema = {
            "version": 3,
            "clkConfig": {
                "l": 1024,
                "kdf": {
                    "type": "HKDF",
                    "hash": "SHA256",
                    "info": "",
                    "keySize": 64
                }
            },
            "features": [
                {
                    "identifier": "INDEX",
                    "ignored": True
                },
                {
                    "identifier": "NAME freetext",
                    "format": {
                        "type": "string",
                        "encoding": "utf-8",
                        "case": "mixed",
                        "minLength": 3
                    },
                    "hashing": {
                        "comparison": {
                            "type": "mycompare",
                            "n": [2, 3]
                        },
                        "strategy": {
                            "bitsPerFeature": 100
                        },
                        "hash": {"type": "doubleHash"}
                    }
                }]
        }
        with open(tmp.name, 'w') as f:
            json.dump(wrong_schema, f)

        # corrupt the json file deliberately
        with open(tmp.name, 'a') as f:
            f.write('corrupt')

        with pytest.raises(ValueError) as e:
            load_schema(tmp.name)
            assert 'The signature config is not valid.' in e
