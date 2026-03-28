"""Test for env.py"""

import pytest
from pytest_mock import MockerFixture

from src import env

test_tokens = [
    (None, False),
    ("", False),
    ("test123", False),
    ("12345678:abcdefghijklmnopqrstuvwxyz01_345-78", True),
]


@pytest.mark.parametrize("token, validation", test_tokens)
def test_check_token(token: str, validation: bool):
    """test if a token is None or in a valid format"""
    assert env.check_token(token) == validation


def test_setup_file_missing(mocker: MockerFixture):
    """test if setup() cannot find a .env file"""

    mocker.patch("src.env.load_dotenv", return_value=False)
    mocker.patch("os.getenv", return_value=None)

    env_result = None

    with pytest.raises(SystemExit) as exitinfo:
        env_result = env.setup()

    assert exitinfo.value.code == 1
    assert env_result is None


test_variable = [
    (["token", None, None, None, None], True),
    ([None, "user", None, None, None], True),
    ([None, None, "host", None, None], True),
    ([None, None, None, "psw", None], True),
    ([None, None, None, None, "name"], True),
    (["token", None, None, None, None], False),
    ([None, "user", None, None, None], False),
    ([None, None, "host", None, None], False),
    ([None, None, None, "psw", None], False),
    ([None, None, None, None, "name"], False),
]


@pytest.mark.parametrize("_env, is_correct", test_variable)
def test_setup_missing_variables(
    _env: list[str | None],
    is_correct: bool,
    mocker: MockerFixture,
):
    """test if setup() cannot find DB variable"""
    mocker.patch("src.env.load_dotenv", return_value=True)
    mocker.patch("src.env.check_token", return_value=is_correct)

    mocker.patch("os.getenv", side_effect=_env)

    env_result = None
    with pytest.raises(SystemExit) as exitinfo:
        env_result = env.setup()

    assert exitinfo.value.code == 1
    assert env_result is None


test_env = ["token", "user", "host", "psw", "name"]


def test_setup_succes(mocker: MockerFixture):
    """test setup() with correct parameters"""

    mocker.patch("src.env.load_dotenv", return_value=True)
    mocker.patch("src.env.check_token", return_value=True)

    mocker.patch("os.getenv", side_effect=test_env)

    env_result = None
    env_result = env.setup()

    assert env_result.get_token() == "token"
    assert env_result.get_user() == "user"
    assert env_result.get_host() == "host"
    assert env_result.get_password() == "psw"
    assert env_result.get_database() == "name"
