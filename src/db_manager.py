"""
This module handles MySQL database calls
"""

from typing import Any, cast

import chess
import mysql.connector
from mysql.connector import errorcode

from src.env import ENV as env
from src.logger import LOGGER as log


class MatchesDB:
    """class which handles all the requests to the database"""

    def __init__(self, user: str, host: str, password: str, database: str):
        config = {
            "user": user,
            "host": host,
            "password": password,
            "database": database,
        }

        try:
            self.db = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            self._handle_error(err)

            raise  # Raises the original error

    def _handle_error(self, err):
        """Handles connection errors in the init process"""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            log.critical("Auth failure: check username/password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            log.critical("Database does not exist")
        else:
            log.critical("Database error: %s", err)

    def close_connection(self):
        """Closes connection to the server"""
        self.db.close()

    def ensure_connection(self):
        """Re-enstablish db connection if it's down"""
        if not self.db.is_connected():
            self.db.reconnect()

    def insert_user(self, user_id: str, username: str | None, fullname: str) -> bool:
        """insert a user in User table with specified data"""

        # parameter validation
        if not user_id:
            log.error("Invalid user_id")
            return False

        if not isinstance(user_id, str):
            log.error("user_id must be a string")
            return False

        if not username or not isinstance(username, str):
            log.error("username must be a string")
            return False

        if not user_id.isdigit():
            log.error("Parameter:user_id must contain only digits")
            return False

        self.ensure_connection()

        try:
            with self.db.cursor() as cursor:
                if username:
                    sql = "INSERT INTO User (ID_User, username, fullname) VALUES (%s, %s, %s)"
                    values = (user_id, username, fullname)
                else:
                    sql = (
                        "INSERT INTO User (ID_User, username, fullname) "
                        "VALUES (%s, CONCAT('_anonymous_', %s, '_'), %s)"
                    )
                    values = (user_id, user_id, fullname)
                cursor.execute(sql, values)
                self.db.commit()
                return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                log.error("Duplicate entry %s", user_id)
            else:
                log.error("Database raised an exception during isertion, %s", err)
            self.db.rollback()

            return False

    def del_user(self, user_id: str) -> bool:
        """Deletes the user with the given ID"""
        self.ensure_connection()

        sql = "DELETE FROM User WHERE ID_User = %s;"

        with self.db.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            self.db.commit()

            affected_rows = cursor.rowcount
            if affected_rows != 0:
                log.debug("Deleted user:%s, affected rows: %s", user_id, affected_rows)
                return True

            log.error(
                "User:%s does not exist, affected rows: %s", user_id, affected_rows
            )
            return False

    def get_username(self, user_id: str) -> str | None:
        """Fetches the username for a given user_id on the database."""
        self.ensure_connection()

        query = "SELECT username FROM User WHERE ID_User = %s"

        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if not result:
                log.error("User_id: %s not found in database", user_id)
                return None

            # Check that the database doesn't return a dict instead of a RowType
            if not isinstance(result, tuple):
                log.error("Some error occurred while fetching: %s", user_id)
                return None

            return str(result[0])

    def get_user_id(self, username: str) -> str | None:
        """Fetches the user_id for a given username on the database."""
        self.ensure_connection()

        query = "SELECT ID_User FROM User WHERE username = %s"

        with self.db.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if not result:
                log.error("Username: %s not found in database", username)
                return None

            # Check that the database doesn't return a dict instead of a RowType
            if not isinstance(result, tuple):
                log.error("Some error occurred while fetching: %s", username)
                return None

            return str(result[0])

    def get_user_data(self, user_id: str) -> dict | None:
        """
        Fetches data from User table.
        Returns a dict if the record exists, None otherwise.
        {
            "ID_User": 1,
            "username": username,
            "fullname": Carlo Conti,
        }
        """
        self.ensure_connection()

        if not user_id or not str(user_id).isdigit():
            log.error("user_id is not valid: %s", user_id)
            return None

        query = """
            SELECT ID_User, username, fullname
            FROM User
            WHERE ID_User = %s
        """

        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                record = cursor.fetchone()

                if record is None:
                    log.error("User not found ID: %s", user_id)
                    return None

                log.debug("Fetched user from User %s", user_id)
                return cast(dict[str, Any], record)

        except mysql.connector.Error as err:
            log.error("Database error while executing get_user_data: %s", err)
            return None

    def show_table(self, table_name: str) -> bool:
        """select * on a specified table"""
        self.ensure_connection()

        print(f"Printing table {table_name}...")
        if not table_name:
            log.error("Tablename is empty")
            return False

        query = f"SELECT * FROM {table_name}"

        try:
            with self.db.cursor() as cursor:
                cursor.execute(query)
                records = cursor.fetchall()
                for record in records:
                    print(record)
                return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_NO_SUCH_TABLE:
                log.error("No such table %s", table_name)
            else:
                log.error("Database raised an exception while querying, %s", err)

            return False

    def start_match(self, id_white: str, id_black: str) -> bool:
        """insert a match record into UserMatch"""
        self.ensure_connection()

        if not id_white or not id_black:
            log.error("Invalid parameters: %s, %s", id_white, id_black)
            return False

        if not id_white.isdigit() or not id_black.isdigit():
            log.error("Invalid parameters: %s, %s", id_white, id_black)
            return False

        ongoing_match_id = self.get_active_match(id_white, id_black)
        log.debug("Start_match.ongoing_match = %s", ongoing_match_id)

        # check there is not an active game between the two players
        if ongoing_match_id is not None:
            log.error(
                """There is already an ongoing match between the two players: %s and %s""",
                id_white,
                id_black,
            )
            return False

        sql = """
            INSERT INTO UserMatch (white_user1, black_user2,time_start,time_stop,chessboard_fen)
            VALUES (%s, %s, NOW(), NULL, %s)"""

        chessboard = chess.Board()

        try:
            with self.db.cursor() as cursor:
                values = (id_white, id_black, chessboard.fen())
                cursor.execute(sql, values)
                self.db.commit()
                log.debug("Match started between %s and %s", id_white, id_black)
                return True
        except mysql.connector.Error as err:
            log.error("A database error occurred while starting match: %s", err)
            return False

    def get_matches(self, id_white: str, id_black: str) -> list | None:
        """Get a list containing all the match records between two
        users ordered from the latest to the oldest:
        (
        [
        ID_Match, white_user1, black_user2, time_start, time_stop, chessboard_fen
        ]
        )

        """

        query = """
        SELECT ID_Match, white_user1, black_user2, time_start, time_stop, chessboard_fen
        FROM UserMatch
        ORDER BY time_start DESC"""

        try:
            with self.db.cursor() as cursor:
                cursor.execute(query)
                records = cursor.fetchall()

                # Check that the database doesn't return a dict instead of a RowType
                if not isinstance(records, list):
                    log.error(
                        "Some error occurred while fetching match: %s, %s",
                        id_white,
                        id_black,
                    )
                    return None

                return records
        except mysql.connector.Error as err:
            log.error("A database error occurred while querying match data: %s", err)
            return None

    def get_match_data(self, match_id: str) -> dict | None:
        """
        Fetches data from UserMatch table.
        Returns a dict if the record exists, None otherwise.
        {
            "ID_Match": 1,
            "white_user1": 12345,
            "black_user2": 67890,
            "time_start": datetime(...),
            "time_stop": datetime(...),
            "chessboard_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        }
        """
        self.ensure_connection()

        if not match_id or not str(match_id).isdigit():
            log.error("ID_Match is not valid: %s", match_id)
            return None

        query = """
            SELECT ID_Match, white_user1, black_user2, time_start, time_stop, chessboard_fen
            FROM UserMatch
            WHERE ID_Match = %s
        """

        try:
            with self.db.cursor(dictionary=True) as cursor:
                cursor.execute(query, (match_id,))
                record = cursor.fetchone()

                if record is None:
                    log.error("Match not found ID: %s", match_id)
                    return None

                log.debug("Fetched match from UserMatch %s", match_id)
                return cast(dict[str, Any], record)

        except mysql.connector.Error as err:
            log.error("Database error while executing get_match_data: %s", err)
            return None

    def stop_match(
        self,
        match_id: str | None = None,
        id_white: str | None = None,
        id_black: str | None = None,
    ) -> bool:
        """
        Stops a match record by updating time_stop to NOW().
        Supports stopping by match_id OR by player IDs.
        """
        self.ensure_connection()
        target_id = match_id

        # Case 1: No match_id provided, try to find it via player IDs
        if not target_id:
            if id_white and id_black:
                target_id = self.get_active_match(id_white, id_black)
                if target_id is None:
                    log.debug(
                        "No ongoing match found between %s and %s", id_white, id_black
                    )
                    return False
            else:
                log.error(
                    "Invalid parameters: Provide either match_id OR both player IDs."
                )
                return False

        # Case 2: target_id (either passed in or found via players)
        sql = "UPDATE UserMatch SET time_stop = NOW() WHERE ID_Match = %s"

        try:
            with self.db.cursor() as cursor:
                cursor.execute(sql, (target_id,))
                self.db.commit()

                if cursor.rowcount == 0:
                    log.error("No match found with ID %s", target_id)
                    return False

                log.debug("Match %s successfully stopped.", target_id)
                return True
        except mysql.connector.Error as err:
            log.error("A database error occurred while stopping match: %s", err)
            return False

    def get_match_chessboard(self, match_id: str) -> str | None:
        """Get the chessboard fen string stored in a UserMatch record"""
        self.ensure_connection()

        if not match_id:
            log.error("Match_id cannot be None")
            return None

        # this query never returns an error in mysql
        query = (
            "SELECT chessboard_fen FROM UserMatch UM WHERE UM.ID_Match = %s LIMIT 1;"
        )
        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, (match_id,))
                chessboard_fen = cursor.fetchone()

                if not chessboard_fen:
                    log.error("Match not found: %s", match_id)
                    return None

                # Check that the database doesn't return a dict instead of a RowType
                if not isinstance(chessboard_fen, tuple):
                    log.error("Some error occurred while fetching: chessboard_fen")
                    return None

                return str(chessboard_fen[0])
        except mysql.connector.Error as err:
            log.error(
                "A database error occurred while querying chessboard, match_id: %s, err: %s",
                match_id,
                err,
            )
            return None

    def add_move(self, match_id: str, move_uci: str) -> bool:
        """update chessboard attribute in the match with match_id to make a move"""
        self.ensure_connection()

        if not match_id:
            log.error("Match_id and move_uci cannot be empty")
            return False

        chessboard_fen = self.get_match_chessboard(match_id)

        if chessboard_fen is None:
            log.error(
                "Cannot query chessboard_fen from: the match does not exist: %s",
                match_id,
            )
            return False

        try:
            chessboard = chess.Board(fen=chessboard_fen)
            chessboard.push_uci(move_uci)
        except (chess.InvalidMoveError, chess.IllegalMoveError) as err:
            log.error("Cannot update chessboard, the given move is invalid: %s ", err)
            return False
        except ValueError as err:
            log.error("Cannot update chessboard: %s", err)
            return False

        update = "UPDATE UserMatch UM SET chessboard_fen = %s WHERE ID_Match = %s;"

        try:
            with self.db.cursor() as cursor:
                cursor.execute(update, (chessboard.fen(), match_id))
                self.db.commit()
                log.debug("Match with ID:%s updated successfully", match_id)
                return True
        except mysql.connector.Error as err:
            log.error("Cannot update chessboard: %s", err)
            return False

    def get_active_match(self, id_user1: str, id_user2: str) -> str | None:
        """gets the active match between two users, if one exists.
        Only one ongoing match (time_stop==NULL) should exist between two users"""
        self.ensure_connection()

        query = """
            SELECT ID_Match
            FROM UserMatch UM
            WHERE
            (
                (white_user1 = %s AND black_user2 = %s)
                OR
                (white_user1 = %s AND black_user2 = %s)
            )
            AND UM.time_stop IS NULL;"""

        try:
            with self.db.cursor() as cursor:
                cursor.execute(query, (id_user1, id_user2, id_user2, id_user1))
                result = cursor.fetchone()

                if result is None:
                    log.debug(
                        "No active match found between the specified users: %s, %s",
                        id_user1,
                        id_user2,
                    )
                    return None

                if not isinstance(result, tuple):
                    log.error("Some error occurred while fetching: active_match")
                    return None

                return str(result[0])
        except mysql.connector.Error as err:
            log.error("A database error occurred while querying active match: %s", err)
            return None

    def drop_all_tables(self) -> bool:
        """drop all tables on the database"""
        self.ensure_connection()

        # query to get all the table names on the database
        query = """
        SELECT concat('DROP TABLE IF EXISTS `', table_name, '`;')
        FROM information_schema.tables
        WHERE table_schema = 'Matches';
        """

        with self.db.cursor() as cursor:
            cursor.execute(query)
            tables = cursor.fetchall()

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            for table in tables:

                # Check that the database doesn't return a dict instead of a RowType
                if not isinstance(table, tuple):
                    log.error("Some error occurred while fetching: chessboard_fen")
                    return False

                try:
                    cursor.execute(str(table[0]))
                except mysql.connector.Error as err:
                    log.error("Cannot drop table %s: %s", str(table[0]), err)
                    return False

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            return True

    def setup(self) -> bool:
        """automatically create tables on the database"""
        self.ensure_connection()

        user_table = """
            CREATE TABLE User (
                ID_User BIGINT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                fullname VARCHAR(50) NOT NULL
            );
        """

        user_match_table = """
            CREATE TABLE UserMatch (
            ID_Match INT AUTO_INCREMENT PRIMARY KEY,
            white_user1 BIGINT NOT NULL,
            black_user2 BIGINT NOT NULL,
            time_start DATETIME,
            time_stop DATETIME,
            chessboard_fen VARCHAR(90),
            FOREIGN KEY (white_user1) REFERENCES User(ID_User),
            FOREIGN KEY (black_user2) REFERENCES User(ID_User),
            CHECK (white_user1 <> black_user2)
        );
        """
        try:
            with self.db.cursor() as cursor:
                cursor.execute(user_table)
                cursor.execute(user_match_table)
                return True
        except mysql.connector.Error as err:
            log.error("Cannot setup database: %s", err)
            return False


DB = MatchesDB(
    user=env.get_user(),
    host=env.get_host(),
    password=env.get_password(),
    database=env.get_database(),
)
