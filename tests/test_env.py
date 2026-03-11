"""Test for env.py"""

import pytest

from src.env import check_token

tokens = [
    ("", False),
    ("test123", False),
    ("12345678:abcdefghijklmnopqrstuvwxyz01_345-78", True),
]


@pytest.mark.parametrize("token, validation", tokens)
def test_check_token(token: str, validation: bool):
    """test if a token is in a valid format"""
    assert check_token(token) == validation
