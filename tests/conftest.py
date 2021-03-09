import pytest


@pytest.fixture(scope="module")
def valid_psig_config():
    yield {
            "blocking-features": [1],
            "record-id-col": 0,
            "filter": {
                "type": "ratio",
                "max": 0.5,
                "min": 0.2,
            },
            "blocking-filter": {
                "type": "bloom filter",
                "number-hash-functions": 20,
                "bf-len": 2048,
            },
            "signatureSpecs": [
                [
                    {"type": "feature-value", "feature": 1}
                ]
            ]
        }