from typing import List

import pytest
from pydantic import ValidationError
from pydantic.tools import parse_obj_as

from blocklib import generate_signatures
from blocklib.validation import PSigSignatureModel
from blocklib.validation.psig_validation import PSigCharsAtSignatureSpec, PSigMetaphoneSignatureSpec, \
    PSigFeatureValueSignatureSpec


class TestPSig:

    def test_feature_value(self):
        """Test signatures generated by feature-value."""
        dtuple = ('Joyce', 'Wang', 2134)
        signatures = [
            parse_obj_as(PSigSignatureModel,
                [
                    {'type': 'feature-value', 'feature': 0},
                    {'type': 'feature-value', 'feature': 1},
                ]
            )
        ]
        signatures = generate_signatures(signatures, dtuple)
        assert signatures == ["0_Joyce_Wang"]

    def test_char_at(self):
        """Test signatures generated by characters-at."""
        dtuple = ('Joyce', 'Wang', 2134)
        # test start_ind: end_ind
        signatures = [
            parse_obj_as(PSigSignatureModel, [
                {'type': 'characters-at', 'feature': 0, 'config': {'pos': ["1:4"]}},
                {'type': 'characters-at', 'feature': 1, 'config': {'pos': ["1:4"]}}
            ])
        ]

        print(signatures)

        signatures = generate_signatures(signatures, dtuple)
        assert signatures == ["0_oyc_ang"]

        # test :end_ind
        strategy = [
            [
                PSigCharsAtSignatureSpec(**{'type': 'characters-at', 'feature': 0, 'config': {'pos': [':2', '-2:', 2, '2']}})
            ]
        ]
        signature = generate_signatures(strategy, dtuple)
        assert signature == ["0_Joceyy"]

        res = generate_signatures(strategy, ('', ''))
        assert res == ['0_']

        invalid_strategy = [
            [
                PSigCharsAtSignatureSpec(**{'type': 'characters-at', 'feature': 0, 'config': {'pos': ['1-2', '-2:', 2, '2']}})
            ]
        ]
        with pytest.raises(ValueError) as e:
            generate_signatures(invalid_strategy, dtuple)
            assert e == 'Invalid pos argument: 1-2'

    def test_metaphone(self):
        """Test signatures generated by metaphone."""
        dtuple = ('Smith', 'Schmidt', 2134)
        signature_strategies = [
            [
                PSigMetaphoneSignatureSpec(type='metaphone', feature=0)
            ]
        ]
        signatures = generate_signatures(signature_strategies, dtuple)
        assert signatures == ["0_SM0XMT"]

    def test_generate_signatures(self):
        """Test a multi-strategy signatures."""
        dtuple = ('Joyce', 'Wang', 2134)
        signatures = parse_obj_as(
            List[PSigSignatureModel],
            [
                [
                    {'type': 'feature-value', 'feature': 0},
                    {'type': 'feature-value', 'feature': 1},
                ],
                [
                    {'type': 'metaphone', 'feature': 0},
                    {'type': 'metaphone', 'feature': 1},
                ]
            ]
        )
        signatures = generate_signatures(signatures, dtuple, "")
        assert signatures == ["0_Joyce_Wang", "1_JSAS_ANKFNK"]

    def test_generate_signatures_with_null(self):
        signatures = parse_obj_as(
            List[PSigSignatureModel],
            [
                [
                    {'type': 'feature-value', 'feature': 0},
                    {'type': 'feature-value', 'feature': 1},
                ],
                [
                    {'type': 'metaphone', 'feature': 0},
                    {'type': 'metaphone', 'feature': 1},
                ]
            ]
        )
        dtuple = ('Joyce', '', 2134)
        signatures = generate_signatures(signatures, dtuple, "")
        assert signatures == []
        dtuple = ('N/A', 'Wang', 2134)
        signatures = generate_signatures(signatures, dtuple, "N/A")
        assert signatures == []

    def test_invalid_signature_type(self):
        with pytest.raises(ValidationError) as e:
            parse_obj_as(
                PSigSignatureModel,
                [
                    {'type': 'fuzzy matching'}
                ]
            )

    def test_invalid_feature_to_index(self):
        dtuple = ('Joyce', 'Wang', 2134)
        signatures = [
            [
                PSigFeatureValueSignatureSpec(type='feature-value', feature='firstname')
            ]
        ]
        with pytest.raises(AssertionError) as e:
            generate_signatures(signatures, dtuple)
            assert e == 'Missing information to map from feature name to index'

        with pytest.raises(ValueError) as e:
            feature_to_index = {'name': 0}
            generate_signatures(signatures, dtuple, feature_to_index)
            assert e == 'Feature name is not in the dataset'
