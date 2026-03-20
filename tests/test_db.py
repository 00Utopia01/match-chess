def test_insert_and_get_user(empty_db):
    # Test insertion
    assert empty_db.insert_user("123", "test_username") is True

    # Test retrieval
    username = empty_db.get_username("123")
    assert username == "test_username"


def test_get_username(empty_db):
    empty_db.insert_user("123", "test_username")

    username = empty_db.get_username("123")
    assert username == "test_username"

    # Test retrieval of an non existent user
    username = empty_db.get_username("99999")
    assert username is None
