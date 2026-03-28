"""
Test db creation and functionalities
"""

import mysql.connector
import pytest
from mysql.connector import Error, errorcode
from pytest_mock import MockerFixture

from src.db_manager import MatchesDB


def test_contructor(mocker: MockerFixture):
    """Test errors occurring in the init method"""
    err = Error("some error")
    mocker.patch("mysql.connector.connect", side_effect=err)
    mock_handle_error = mocker.patch.object(MatchesDB, "_handle_error")

    with pytest.raises(mysql.connector.Error):
        MatchesDB(
            user="user",
            host="host",
            password="password",
            database="database",
        )

    mock_handle_error.assert_called_once_with(err)


errors = [
    {
        "errorcode": errorcode.ER_ACCESS_DENIED_ERROR,
        "log_response": "Auth failure: check username/password",
    },
    {"errorcode": errorcode.ER_BAD_DB_ERROR, "log_response": "Database does not exist"},
]

# pylint: disable=protected-access


@pytest.mark.parametrize("error", errors)
def test_handle_error(empty_db, error, mocker: MockerFixture):
    """Testing the handling of errors in the init method"""
    mock_log = mocker.patch("src.db_manager.log")
    err = Error()
    err.errno = error["errorcode"]

    empty_db._handle_error(err)

    mock_log.critical.assert_called_once_with(error["log_response"])


def test_close_connection(empty_db, mocker: MockerFixture):
    """Test if the close method is being called"""
    mock_close = mocker.patch.object(empty_db.db, "close")

    empty_db.close_connection()

    mock_close.assert_called_once()


def test_ensure_connection(empty_db, mocker: MockerFixture):
    """Test if ensure_connection calls db.reconnect if the connection is down"""
    mocker.patch.object(empty_db.db, "is_connected", return_value=False)
    mock_reconnect = mocker.patch.object(empty_db.db, "reconnect")

    empty_db.ensure_connection()

    mock_reconnect.assert_called_once()


def test_insert_and_get_user(empty_db):
    """Test insertion of a user and retreiving it's data"""
    # Test insertion
    assert empty_db.insert_user("123", "test_username") is True

    # Test retrieval
    username = empty_db.get_username("123")
    assert username == "test_username"


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
    """Handle the error raised cursor.execute during insertion"""
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


def test_del_user_success(empty_db, mocker: MockerFixture):
    """Test the deletion of an existent user"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "test_username")

    assert empty_db.del_user("123") is True
    mock_log.debug.assert_called_once()


def test_del_user_fail(empty_db, mocker: MockerFixture):
    """Test the deletion of a non existent user"""
    mock_log = mocker.patch("src.db_manager.log")

    assert empty_db.del_user("123") is False
    mock_log.error.assert_called_once()


def test_get_username(empty_db, mocker: MockerFixture):
    """Retreival of a user that doesn't exist"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "test_username")
    user_id1 = "123"
    user_id2 = "99999"

    username1 = empty_db.get_username(user_id1)
    username2 = empty_db.get_username(user_id2)

    assert username1 == "test_username"
    # Test retrieval of an non existent user
    assert username2 is None
    mock_log.error.assert_called_once_with(
        "User_id: %s not found in database", user_id2
    )


def test_get_username_wrong_type(empty_db, mocker: MockerFixture):
    """Test the retrieval of the id of a user, but the database returns a dict instead of tuple"""
    mock_log = mocker.patch("src.db_manager.log")
    # Make cursor.fetchone return a dict instead of a tuple
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {"test_key": "val"}
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    user_id = empty_db.get_username("123")

    assert user_id is None
    mock_log.error.assert_called_once_with(
        "Some error occurred while fetching: %s", "123"
    )


def test_get_user_id_success(empty_db):
    """Test the retrieval of the id of an existent user"""
    empty_db.insert_user("123", "test_username")

    user_id = empty_db.get_user_id("test_username")

    assert user_id == "123"


def test_get_user_id_fail(empty_db, mocker: MockerFixture):
    """Test the retrieval of the id of a non existent user"""
    mock_log = mocker.patch("src.db_manager.log")

    user_id = empty_db.get_user_id("test_username")

    assert user_id is None
    mock_log.error.assert_called_once_with(
        "Username: %s not found in database", "test_username"
    )


def test_get_user_id_wrong_type(empty_db, mocker: MockerFixture):
    """Test the retrieval of the id of a user, but the database returns a dict instead of tuple"""
    mock_log = mocker.patch("src.db_manager.log")
    # Make cursor.fetchone return a dict instead of a tuple
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {"test_key": "val"}
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    user_id = empty_db.get_user_id("test_username")

    assert user_id is None
    mock_log.error.assert_called_once_with(
        "Some error occurred while fetching: %s", "test_username"
    )


def test_show_table_success(empty_db):
    """Test show_table"""
    result = empty_db.show_table("User")

    assert result is True


def test_show_table_empty_tablename(empty_db, mocker: MockerFixture):
    """Try to pass an empty string to show_table"""
    mock_log = mocker.patch("src.db_manager.log")

    result = empty_db.show_table("")

    assert result is False
    mock_log.error.assert_called_once_with("Tablename is empty")


def test_show_table_no_table(empty_db, mocker: MockerFixture):
    """Try to show a non existent table"""
    mock_log = mocker.patch("src.db_manager.log")

    result = empty_db.show_table("Test_table")

    assert result is False
    mock_log.error.assert_called_once_with("No such table %s", "Test_table")


parameters = [
    {"id_white": "", "id_black": "", "expected_val": False},
    {"id_white": "g45g65", "id_black": "56h65g", "expected_val": False},
    {"id_white": "4564563", "id_black": "745734", "expected_val": True},
]


@pytest.mark.parametrize("param", parameters)
def test_start_match_parameters(empty_db, param):
    """Pass wrong parameters to start_match"""
    # Insert the users in User to avoid the foreing key constraint on UserMatch
    empty_db.insert_user(param["id_white"], "usr1")
    empty_db.insert_user(param["id_black"], "usr2")

    assert (
        empty_db.start_match(param["id_white"], param["id_black"])
        is param["expected_val"]
    )


def test_start_match_ongoing_match(empty_db, mocker: MockerFixture):
    """Try to start a match when there is already an ongoing match"""
    mock_log = mocker.patch("src.db_manager.log")

    # Start an active match between two users
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")

    result1 = empty_db.start_match("123", "1234")
    result2 = empty_db.start_match("123", "1234")

    assert result1 is True
    assert result2 is False
    mock_log.error.assert_called_with(
        """There is already an ongoing match between the two players: %s and %s""",
        "123",
        "1234",
    )


def test_start_match_error(empty_db, mocker: MockerFixture):
    """Raise an error while starting a match"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")

    mock_log = mocker.patch("src.db_manager.log")

    mocker.patch.object(empty_db, "get_active_match", return_value=None)

    err = Error("Some error")
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    result = empty_db.start_match("123", "1234")

    assert result is False
    mock_log.error.assert_called_once_with(
        "A database error occurred while starting match: %s", err
    )


def test_get_matches(empty_db):
    """Query two matches between two users"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    empty_db.insert_user("12345", "usr3")
    empty_db.start_match("123", "12345")

    matches_list = empty_db.get_matches("123", "1234")

    assert str(matches_list[0][1]) == "123"
    assert str(matches_list[0][2]) == "1234"
    assert str(matches_list[1][1]) == "123"
    assert str(matches_list[1][2]) == "12345"


def test_get_matches_wrong_type(empty_db, mocker: MockerFixture):
    """Handle dict return type"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    # Make cursor.fetchone return a dict instead of a tuple
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {"test_key": "val"}
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    matches_list = empty_db.get_matches("123", "1234")

    assert matches_list is None
    mock_log.error.assert_called_with(
        "Some error occurred while fetching match: %s, %s", "123", "1234"
    )


def test_get_matches_error(empty_db, mocker: MockerFixture):
    """Raise an error while querying matches"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    err = Error()
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    matches_list = empty_db.get_matches("123", "1234")

    assert matches_list is None
    mock_log.error.assert_called_with(
        "A database error occurred while querying match data: %s", err
    )


def test_get_match_data_success(empty_db):
    """Fetch a dict with get_match_data containing all the data"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    active_match_id = empty_db.get_active_match("123", "1234")

    match_data = empty_db.get_match_data(active_match_id)

    assert match_data is not None
    assert str(match_data["ID_Match"]) == active_match_id
    assert str(match_data["white_user1"]) == "123"
    assert str(match_data["black_user2"]) == "1234"
    assert "chessboard_fen" in match_data
    assert match_data["time_stop"] is None


def test_get_match_data_not_found(empty_db):
    """Try to input wrong match_id"""
    match_data = empty_db.get_match_data("999")

    assert match_data is None


def test_get_match_data_invalid_input(empty_db):
    """Test get_match_data with invalid inputs"""
    assert empty_db.get_match_data("invalid string") is None
    assert empty_db.get_match_data(None) is None


def test_stop_match_by_ids(empty_db):
    """Stop match between two users using user's ids"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    active_match_id1 = empty_db.get_active_match("123", "1234")
    empty_db.stop_match(id_white="123", id_black="1234")

    active_match_id2 = empty_db.get_active_match("123", "1234")

    assert active_match_id1 is not None
    assert active_match_id2 is None


def test_stop_match_by_match_id(empty_db):
    """Test stop_match using match_id"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    active_match_id1 = empty_db.get_active_match("123", "1234")
    empty_db.stop_match(match_id=active_match_id1)
    active_match_id2 = empty_db.get_active_match("123", "1234")

    assert active_match_id2 is None


params = [
    {"match_id": None, "id_white": None, "id_black": None, "expected_val": False},
    {"match_id": "1", "id_white": None, "id_black": None, "expected_val": True},
    {"match_id": None, "id_white": "123", "id_black": "1234", "expected_val": True},
    {"match_id": None, "id_white": "999", "id_black": "999", "expected_val": False},
    {"match_id": "999", "id_white": None, "id_black": None, "expected_val": False},
]


@pytest.mark.parametrize("param", params)
def test_stop_match_param(empty_db, param):
    """Pass various parameters to stop_match"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    result = empty_db.stop_match(
        match_id=param["match_id"],
        id_white=param["id_white"],
        id_black=param["id_black"],
    )

    assert result is param["expected_val"]


def test_stop_match_error(empty_db, mocker: MockerFixture):
    """Raise an error while stopping a match"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    err = Error("Some error")
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    result = empty_db.stop_match("123", "1234")

    assert result is False
    mock_log.error.assert_called_with(
        "A database error occurred while stopping match: %s", err
    )


def test_get_match_chessboard_success(empty_db):
    """Get chessboard fen stored in a match"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    match_id = empty_db.get_active_match("123", "1234")
    chessboard = empty_db.get_match_chessboard(match_id)

    assert chessboard == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_get_match_chessboard_no_match_id(empty_db, mocker: MockerFixture):
    """Try to get_match_chessboard without any match_id"""
    mock_log = mocker.patch("src.db_manager.log")
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")

    chessboard = empty_db.get_match_chessboard(None)

    assert chessboard is None
    mock_log.error.assert_called_with("Match_id cannot be None")


def test_get_match_chessboard_empty_chessboard(empty_db, mocker: MockerFixture):
    """Make the db return an empty chessboard"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    match_id = empty_db.get_active_match("123", "1234")

    # Make cursor.fetchone return None
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    chessboard = empty_db.get_match_chessboard(match_id)

    assert chessboard is None
    mock_log.error.assert_called_with("Match not found: %s", match_id)


def test_get_match_chessboard_wrong_type(empty_db, mocker: MockerFixture):
    """Make the db return a dict instead of a tuple"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    match_id = empty_db.get_active_match("123", "1234")

    # Make cursor.fetchone return None
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {"key": "value"}
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    chessboard = empty_db.get_match_chessboard(match_id)

    assert chessboard is None
    mock_log.error.assert_called_with(
        "Some error occurred while fetching: chessboard_fen"
    )


def test_get_match_chessboard_error(empty_db, mocker: MockerFixture):
    """Raise an error while querying a chessboard from a match"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")
    empty_db.start_match("123", "1234")
    match_id = empty_db.get_active_match("123", "1234")

    err = Error("Some error")
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    chessboard = empty_db.get_match_chessboard(match_id)

    assert chessboard is None
    mock_log.error.assert_called_with(
        "A database error occurred while querying chessboard, match_id: %s, err: %s",
        match_id,
        err,
    )


def test_add_move_success(empty_db, mocker: MockerFixture):
    """Add a move successfully"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("1", "p1")
    empty_db.insert_user("2", "p2")
    empty_db.start_match("1", "2")
    match_id = empty_db.get_active_match("1", "2")

    result = empty_db.add_move(match_id, "e2e4")

    assert result is True
    mock_log.debug.assert_any_call("Match with ID:%s updated successfully", match_id)

    # Verify db actually updated
    new_fen = empty_db.get_match_chessboard(match_id)
    assert (
        new_fen == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    )  # Simple check that FEN changed


def test_add_move_no_match_id(empty_db, mocker: MockerFixture):
    """Try to add a move without providing match_id"""
    mock_log = mocker.patch("src.db_manager.log")

    result = empty_db.add_move(None, "e2e4")

    assert result is False
    mock_log.error.assert_called_with("Match_id and move_uci cannot be empty")


def test_add_move_match_not_found(empty_db, mocker: MockerFixture):
    """Try to add a move to a non existent match"""
    mock_log = mocker.patch("src.db_manager.log")

    # Provide an id that definitely doesn't exist
    result = empty_db.add_move("999-non-existent", "e2e4")

    assert result is False
    mock_log.error.assert_any_call(
        "Cannot query chessboard_fen from: the match does not exist: %s",
        "999-non-existent",
    )


def test_add_move_illegal_move(empty_db, mocker: MockerFixture):
    """Try to add an illegal move"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("1", "p1")
    empty_db.insert_user("2", "p2")
    empty_db.start_match("1", "2")
    match_id = empty_db.get_active_match("1", "2")

    # e2e5 is an illegal move for a pawn on the first turn
    result = empty_db.add_move(match_id, "e2e5")

    assert result is False
    # Check that it caught the IllegalMoveError
    pos_args, _ = mock_log.error.call_args
    assert "the given move is invalid" in pos_args[0]


def test_add_move_value_error(empty_db, mocker: MockerFixture):
    """Raise ValueError while adding a move"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("1", "p1")
    empty_db.insert_user("2", "p2")
    empty_db.start_match("1", "2")
    match_id = empty_db.get_active_match("1", "2")

    err = ValueError("val error")
    mock_push_uci = mocker.patch("chess.Board.push_uci")
    mock_push_uci.side_effect = err
    result = empty_db.add_move(match_id, "non-move")

    assert result is False
    mock_log.error.assert_called_with("Cannot update chessboard: %s", err)


def test_add_move_db_error(empty_db, mocker: MockerFixture):
    """Raise an error while adding a move"""
    mock_log = mocker.patch("src.db_manager.log")

    empty_db.insert_user("1", "p1")
    empty_db.insert_user("2", "p2")
    empty_db.start_match("1", "2")
    match_id = empty_db.get_active_match("1", "2")

    # Mock the cursor to raise a MySQL error when executing
    err = Error("Some error")
    test_chessboard = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    mocker.patch.object(empty_db, "get_match_chessboard", return_value=test_chessboard)
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    result = empty_db.add_move(match_id, "e2e4")

    assert result is False
    mock_log.error.assert_any_call("Cannot update chessboard: %s", err)


def test_get_active_match(empty_db):
    """Get the active match between two users"""
    empty_db.insert_user("123", "usr1")
    empty_db.insert_user("1234", "usr2")

    active_match_id1 = empty_db.get_active_match("123", "1234")

    empty_db.start_match("123", "1234")

    active_match_id2 = empty_db.get_active_match("123", "1234")

    assert active_match_id1 is None
    assert active_match_id2 is not None


def test_get_active_match_error(empty_db, mocker: MockerFixture):
    """Raise an error while querying active match"""
    mock_log = mocker.patch("src.db_manager.log")

    err = Error()
    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.execute.side_effect = err
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    active_match_id = empty_db.get_active_match("123", "1234")

    assert active_match_id is None
    mock_log.error.assert_called_with(
        "A database error occurred while querying active match: %s", err
    )


def test_get_active_match_wrong_type(empty_db, mocker: MockerFixture):
    """Raise an error while querying active match"""
    mock_log = mocker.patch("src.db_manager.log")

    mock_cursor_func = mocker.patch.object(empty_db.db, "cursor")
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.side_effect = {"key": "val"}
    mock_cursor_func.return_value.__enter__.return_value = mock_cursor

    active_match_id = empty_db.get_active_match("123", "1234")

    assert active_match_id is None
    mock_log.error.assert_called_with(
        "Some error occurred while fetching: active_match"
    )
