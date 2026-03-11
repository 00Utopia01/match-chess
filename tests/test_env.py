"""Test for env.py"""

import pytest
from pytest_mock import MockerFixture

from src import env

tokens = [
    ("", False),
    ("test123", False),
    ("12345678:abcdefghijklmnopqrstuvwxyz01_345-78", True),
]


@pytest.mark.parametrize("token, validation", tokens)
def test_check_token(token: str, validation: bool):
    """test if a token is in a valid format"""
    assert env.check_token(token) == validation


def test_get_token_success(mocker: MockerFixture, monkeypatch):
    """see if this function takes the token in the environment"""
    # fake the environment variable
    monkeypatch.setenv("TELEGRAM-TOKEN", "test-token")

    mocker.patch.object(env, "load_dotenv", return_value=True)
    assert env.get_token("test-path") == "test-token"


def test_get_token_failure(mocker: MockerFixture, monkeypatch):
    """assure that if the token is missing it returns empty string"""
    # assure that there is no token
    monkeypatch.delenv("TELEGRAM-TOKEN", "test-token")

    mocker.patch.object(env, "load_dotenv", return_value=True)
    assert env.get_token("test-path") == ""


def test_set_path_exists(mocker: MockerFixture):
    """if the .env exists is returned"""
    mocker.patch("os.path.exists", return_value=True)

    path = env.set_path()

    assert path == ".env"


def test_set_path_not_exists(mocker):
    """if .env doens't exist the user inputs a wrong path, then user inputs a correct path"""
    mocker.patch("os.path.exists", return_value=False)

    mock_input = mocker.patch(
        "builtins.input", side_effect=["wrong-file", "correct-path/.env"]
    )
    mock_print = mocker.patch("builtins.print")

    result = env.set_path()

    # Assertions
    assert result == "correct-path/.env"
    assert mock_input.call_count == 2
    mock_print.assert_any_call(
        "The specified path does not end with a .env file, retry"
    )
