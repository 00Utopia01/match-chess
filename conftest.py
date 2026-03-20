"""Setup fixtures to test database connection and functionalities"""

import os

import dotenv
import pytest

from src.db_manager import MatchesDB

dotenv.load_dotenv()


@pytest.fixture(scope="module")
def db_conn():
    """Simulate a database connection to the mysql server
    where users and matches are stored."""
    db = MatchesDB(
        user=os.getenv("DB_USER"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
    )

    # Setup the database with table structure
    db.setup()

    yield db

    # Close the connection to the server
    db.close()


# pylint: disable=redefined-outer-name


@pytest.fixture(scope="function")
def empty_db(db_conn):
    """Setup the database in order to execute tests on it by dropping every record"""
    db_conn.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    db_conn.cursor.execute("TRUNCATE TABLE UserMatch")
    db_conn.cursor.execute("TRUNCATE TABLE User")
    db_conn.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    return db_conn
