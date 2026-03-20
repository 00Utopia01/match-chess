"""
This module handles MySQL database calls
"""

import chess
import mysql.connector
from mysql.connector import errorcode

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
            self.cursor = self.db.cursor()
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

    def close(self):
        """Closes connection to the server"""
        self.cursor.close()
        self.db.close()

    def insert_user(self, user_id: str, username: str) -> bool:
        """insert a user in User table with specified data"""

        # parameter validation
        if not user_id or not username:
            log.error("Invalid user_id or username")
            return False

        try:
            sql = "INSERT INTO User (ID_User, username) VALUES (%s, %s)"
            values = (user_id, username)
            self.cursor.execute(sql, values)
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                log.error("Duplicate entry %s", user_id)
            else:
                log.error("Database raised an exception during isertion, %s", err)

            return False

    def del_user(self, user_id: str) -> bool:
        """Deletes the user with the given ID"""
        sql = "DELETE FROM User WHERE ID_User = %s;"
        self.cursor.execute(sql, (user_id,))
        self.db.commit()

        affected_rows = self.cursor.rowcount
        if affected_rows != 0:
            log.debug("Deleted user:%s, affected rows: %s", user_id, affected_rows)
            return True

        log.debug("User:%s does not exist, affected rows: %s", user_id, affected_rows)
        return False

    def get_username(self, user_id: str) -> str | None:
        """Fetches the username for a given user_id from the database."""
        query = "SELECT username FROM User WHERE ID_User = %s"

        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()

        # Check that the database doesn't return a dict instead of a RowType
        if not isinstance(result, tuple):
            log.error("Some error occurred while fetching: %s", user_id)
            return None

        if result:
            # result is typically a tuple like ('JohnDoe',)
            return str(result[0])
        log.warning("User_id: %s not found in database", user_id)
        return None

    def show_table(self, table_name: str):
        """select * on a specified table"""

        print(f"Printing table {table_name}...")
        if not table_name:
            log.error("Tablename is empty")
            return

        query = f"SELECT * FROM {table_name}"

        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            for record in records:
                print(record)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_NO_SUCH_TABLE:
                log.error("No such table %s", table_name)
            else:
                log.error("Database raised an exception while querying, %s", err)

            return

    def start_match(self, id_white: str, id_black: str) -> bool:
        """insert a match record into UserMatch"""

        if not id_white or not id_black:
            log.error("Invalid parameters: %s, %s", id_white, id_black)
            return False

        sql = """
            INSERT INTO UserMatch (white_user1, black_user2,time_start,time_stop,chessboard_fen)
            VALUES (%s, %s, NOW(), NULL, %s)"""

        chessboard = chess.Board()

        ongoing_match_id = self.get_active_match(id_white, id_black)
        log.debug("Start_match.ongoing_match = %s", ongoing_match_id)

        # check there is not an active game between the two players
        if ongoing_match_id is None:
            values = (id_white, id_black, chessboard.fen())
            self.cursor.execute(sql, values)
            self.db.commit()
            log.debug("Match started between %s and %s", id_white, id_black)
            return True

        log.error(
            """There is already an ongoing match between the two players: %s and %s""",
            id_white,
            id_black,
        )
        return False

    def stop_match(self, id_white: str, id_black: str) -> bool:
        """stop a match record into UserMatch
        by updating the time_top attribute to the current time"""

        if not id_white or not id_black:
            log.error("Invalid parameters: %s, %s", id_white, id_black)
            return False

        sql = """UPDATE UserMatch UM SET time_stop = NOW() WHERE ID_Match = %s"""

        ongoing_match_id = self.get_active_match(id_white, id_black)
        log.debug("Start_match.ongoing_match = %s", ongoing_match_id)

        # check there is not an active game between the two players
        if ongoing_match_id is not None:
            self.cursor.execute(sql, (ongoing_match_id,))
            self.db.commit()
            log.debug("Match stopped between %s and %s", id_white, id_black)
            return True
        log.error(
            "There is not an ongoing match between the two players: %s and %s",
            id_white,
            id_black,
        )
        return False

    def get_match_chessboard(self, match_id: str) -> str | None:
        """Get the chessboard fen string stored in a UserMatch record"""
        if not match_id:
            log.error("Match_id cannot be empty")
            return None

        # this query never returns an error in mysql
        query = (
            "SELECT chessboard_fen FROM UserMatch UM WHERE UM.ID_Match = %s LIMIT 1;"
        )
        self.cursor.execute(query, (match_id,))
        chessboard_fen = self.cursor.fetchone()

        if not chessboard_fen:
            log.error("Match not found: %s", match_id)
            return None

        # Check that the database doesn't return a dict instead of a RowType
        if not isinstance(chessboard_fen, tuple):
            log.error("Some error occurred while fetching: chessboard_fen")
            return None

        return str(chessboard_fen[0])

    def add_move(self, match_id: str, move_uci: str) -> bool:
        """update chessboard attribute in the match with match_id to make a move"""

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
            self.cursor.execute(update, (chessboard.fen(), match_id))
            self.db.commit()
            log.error("Match with ID:%s updated successfully", match_id)
            return True
        except mysql.connector.Error as err:
            log.error("Cannot update chessboard: %s", err)
            return False

    def get_active_match(self, id_user1: str, id_user2: str) -> str | None:
        """gets the active match between two users, if one exists.
        Only one ongoing match (time_stop==NULL) should exist between two users"""

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

        self.cursor.execute(query, (id_user1, id_user2, id_user2, id_user1))
        result = self.cursor.fetchone()

        if result is None:
            log.error(
                "No active match found between the specified users: %s, %s",
                id_user1,
                id_user2,
            )
            return None

        if not isinstance(result, tuple):
            log.error("Some error occurred while fetching: active_match")
            return None

        return str(result[0])

    def drop_all_tables(self) -> bool:
        """drop all tables on the database"""

        # query to get all the table names on the database
        query = """
        SELECT concat('DROP TABLE IF EXISTS `', table_name, '`;')
        FROM information_schema.tables
        WHERE table_schema = 'Matches';
        """

        self.cursor.execute(query)
        tables = self.cursor.fetchall()

        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for table in tables:

            # Check that the database doesn't return a dict instead of a RowType
            if not isinstance(table, tuple):
                log.error("Some error occurred while fetching: chessboard_fen")
                return False

            try:
                self.cursor.execute(str(table[0]))
            except mysql.connector.Error as err:
                log.error("Cannot drop table %s: %s", str(table[0]), err)
                return False

        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        return True

    def setup(self) -> bool:
        """automatically create tables on the database"""

        user_table = """
            CREATE TABLE User (
                ID_User INT PRIMARY KEY,
                username VARCHAR(20) UNIQUE NOT NULL
            );
        """

        user_match_table = """
            CREATE TABLE UserMatch (
            ID_Match INT AUTO_INCREMENT PRIMARY KEY,
            white_user1 INT NOT NULL,
            black_user2 INT NOT NULL,
            time_start DATETIME,
            time_stop DATETIME,
            chessboard_fen VARCHAR(90),
            FOREIGN KEY (white_user1) REFERENCES User(ID_User) ON DELETE CASCADE,
            FOREIGN KEY (black_user2) REFERENCES User(ID_User) ON DELETE CASCADE,
            CHECK (white_user1 <> black_user2)
        );
        """
        try:
            self.cursor.execute(user_table)
            self.cursor.execute(user_match_table)
            return True
        except mysql.connector.Error as err:
            log.error("Cannot setup database: %s", err)
            return False
