"""Test for env.py"""

import pytest

from src.env import check_token


@pytest.mark.parametrize(
    "token, validation",
    [
        ("", False),
        ("test123", False),
        ("12345678:abcdefghijklmnopqrstuvwxyz01_345-78", True),
    ],
)
def test_check_token(token, validation):
    """test for check_token()"""
    assert check_token(token) == validation
