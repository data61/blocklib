import pytest
from blocklib import validate_signature_config
from blocklib.validation import load_schema
import tempfile
import json


class TestValidation:

    def test_validate_signature_config(self):
        """Test validation on signature config."""
        config = {"version": 1,
                  "type": "p-sig",
                  "config": {}}
        validate_signature_config(config)

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
