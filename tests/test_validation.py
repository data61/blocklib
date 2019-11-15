from blocklib import validate_signature_config


def test_validate_signature_config():
    """Test validation on signature config."""
    config = {"version": 1,
              "type": "p-sig",
              "config": {}}
    validate_signature_config(config)
