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
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    mocker.patch.object(env, "load_dotenv", return_value=True)

    assert env.get_token() == "test-token"


def test_get_token_failure(mocker: MockerFixture, monkeypatch):
    """assure that if the token is missing it returns empty string"""
    # assure that there is no token
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.delenv("TELEGRAM_TOKEN", "test-token")

    mocker.patch.object(env, "load_dotenv", return_value=True)
    assert env.get_token() == None


def test_set_path_exists(mocker: MockerFixture):
    """if the .env exists is returned"""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch.object(env, "take_path_input", return_value=".env" )

    path = env.set_path()

    assert path == ".env"


def test_set_path_not_exists_1(mocker: MockerFixture):
    """if .env doens't exist the user inputs a wrong path, then user inputs a correct path"""
    mocker.patch("os.path.exists", return_value=False)

    mocker.patch("builtins.print", return_value="correct-path/.env")
    mocker.patch.object(env, "take_path_input", side_effect=["wrongpath","correct-path/.env"] )
    mock_print = mocker.patch("builtins.print")

    result = env.set_path()

    # Assertions
    mock_print.assert_any_call(
        "The specified path does not end with a .env file, retry"
    )
    assert result == "correct-path/.env"

def test_take_path_input(mocker: MockerFixture):
    mocker.patch("builtins.input", return_value="test")
    assert env.take_path_input() == "test"