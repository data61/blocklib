import unittest
import pytest
from blocklib import validate_signature_config


class TestValidation(unittest.TestCase):

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