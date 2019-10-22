from unittest import TestCase

import pytest

from blocklib.configuration import get_config


class TestConfig(TestCase):
    def test_get_missing_config(self):
        with pytest.raises(ValueError):
            get_config({'a': 'A', 'b': "B"}, 'c')

    def test_get_config(self):
        assert "A" == get_config({'a': 'A', 'b': "B"}, 'a')

