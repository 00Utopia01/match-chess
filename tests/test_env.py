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

@pytest.fixture(autouse=True)
def clear_global():
    """reset all the global variable in .env to None"""
    env.TG_TOKEN = None
    env.DB_USER = None
    env.DB_HOST = None
    env.DB_PASSWORD = None
    env.DB_DATABASE = None
    yield

def test_setup_file_missing(mocker: MockerFixture):
    """test if setup() cannot find a .env file"""

    mocker.patch("src.env.load_dotenv", return_value=False)
    mocker.patch("os.getenv", return_value=None)

    with pytest.raises(SystemExit) as exit:
        env.setup()
    
    assert exit.value.code == 1
    assert env.TG_TOKEN == None
    assert env.DB_USER == None
    assert env.DB_HOST == None
    assert env.DB_PASSWORD == None
    assert env.DB_DATABASE == None

test_variable=[
    (["token", None, None, None, None], True),
    ([None, "user", None, None, None], True),
    ([None, None, "host", None, None], True),
    ([None, None, None, "psw", None], True),
    ([None, None, None, None, "name"], True),
    (["token", None, None, None, None], False),
    ([None, "user", None, None, None], False),
    ([None, None, "host", None, None], False),
    ([None, None, None, "psw", None], False),
    ([None, None, None, None, "name"], False)
]
@pytest.mark.parametrize("_env, is_correct", test_variable)
def test_setup_missing_variables(
    _env:list[str | None], 
    is_correct: bool,
    mocker: MockerFixture,
    ):
    """test if setup() cannot find DB variable"""
    mocker.patch("src.env.load_dotenv", return_value=True)
    mocker.patch("src.env.check_token", return_value=is_correct)

    mocker.patch("os.getenv", side_effect=_env)

    with pytest.raises(SystemExit) as exit:
        env.setup()
    
    assert exit.value.code == 1
    assert env.TG_TOKEN == _env[0]
    assert env.DB_USER == _env[1]
    assert env.DB_HOST == _env[2]
    assert env.DB_PASSWORD == _env[3]
    assert env.DB_DATABASE == _env[4]


test_env = ["token", "user", "host", "psw", "name"]
def test_setup_succes(mocker: MockerFixture):
    """test setup() with correct parameters"""

    mocker.patch("src.env.load_dotenv", return_value=True)
    mocker.patch("src.env.check_token", return_value=True)

    mocker.patch("os.getenv", side_effect=test_env)

    env.setup()

    assert env.TG_TOKEN == "token"
    assert env.DB_USER == "user"
    assert env.DB_HOST == "host"
    assert env.DB_PASSWORD == "psw"
    assert env.DB_DATABASE == "name"




