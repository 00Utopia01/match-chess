"""
Test db creation and functionalities
"""

import pytest
from mysql.connector import Error, errorcode
from pytest_mock import MockerFixture


def test_insert_and_get_user(empty_db):
    """Test insertion of a user and retreiving it's data"""
    # Test insertion
    assert empty_db.insert_user("123", "test_username") is True

    # Test retrieval
    username = empty_db.get_username("123")
    assert username == "test_username"


def test_get_username(empty_db):
    """Retreival of a user that doesn't exist"""
    empty_db.insert_user("123", "test_username")

    username = empty_db.get_username("123")
    assert username == "test_username"

    # Test retrieval of an non existent user
    username = empty_db.get_username("99999")
    assert username is None


params = [
    {"id": "", "username": "test_name", "expected_res": False},
    {"id": "456456", "username": "", "expected_res": False},
    {"id": "test_name", "username": "456456", "expected_res": False},
    {"id": "456456", "username": "test_name", "expected_res": True},
]


@pytest.mark.parametrize("param", params)
def test_insert_invalid_params(empty_db, param):
    """Pass params to the insert function and assert the return value"""
    assert empty_db.insert_user(param["id"], param["username"]) is param["expected_res"]


def test_insert_duplicate_entry(empty_db, mocker: MockerFixture):
    """Try to insert a duplicate user in User"""
    spy_rollback = mocker.spy(empty_db.db, "rollback")
    mock_log = mocker.patch("src.db_manager.log.error")

    insert1 = empty_db.insert_user("123", "test_username")
    insert2 = empty_db.insert_user("123", "test_username")

    assert insert1 is True
    assert insert2 is False
    spy_rollback.assert_called_once()
    mock_log.assert_called_once_with("Duplicate entry %s", "123")


def test_insert_other_error(empty_db, mocker: MockerFixture):
    """Handle the error raised cursor.execute"""
    mock_log = mocker.patch("src.db_manager.log")
    spy_rollback = mocker.spy(empty_db.db, "rollback")

    # Define error raised by cursor.execute
    db_error = Error()
    db_error.errno = errorcode.ER_ABORTING_CONNECTION

    # Replace the 'cursor' method with a Mock
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")

    mock_cursor = mocker.MagicMock()

    # Make the cursor() function return a context manager with the mocked cursor object
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    mock_cursor.execute.side_effect = db_error

    result = empty_db.insert_user("123", "test_username")

    assert result is False
    mock_log.error.assert_called_once()
    spy_rollback.assert_called_once()
