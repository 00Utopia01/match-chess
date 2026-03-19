"""
This module handles MySQL database calls
"""

import mysql.connector
from mysql.connector import errorcode
import chess
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
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                log.critical("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                log.critical("Database does not exist")
            else:
                log.critical(f"Cannot connect to database: {err}")

            raise Exception

    def close(self):
        """close connection with the server"""
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
                log.error(f"Duplicate entry {user_id}")
            else:
                log.error(f"Database raised an exception during isertion, {err}")

            return False

    def del_user(self, user_id: str) -> bool:
        sql = "DELETE FROM User WHERE ID_User = %s;"
        self.cursor.execute(sql, (user_id,))
        self.db.commit()

        affected_rows = self.cursor.rowcount
        if affected_rows != 0:
            log.debug(f"Deleted user:{user_id}, affected rows: {affected_rows}")
            return True
        else:
            log.debug(f"User:{user_id} does not exist, affected rows: {affected_rows}")

    def get_username(self, user_id: str) -> str:
        """get the username with user_id"""
        query = "SELECT username FROM User WHERE ID_User = %s"
        self.cursor.execute(query, (user_id,))

        record = self.cursor.fetchone()
        if record is None:
            log.error(f"User_id:{user_id} not found")
            return None

        username = record[0]
        return username

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
                log.error(f"No such table {table_name}")
            else:
                log.error(f"Database raised an exception while querying, {err}")

            return

    def start_match(self, ID_white1: str, ID_black2: str) -> bool:
        """insert a match record into UserMatch"""

        if not ID_white1 or not ID_black2:
            log.error(f"Invalid parameters: {ID_white1}, {ID_black2}")
            return False

        sql = """
            INSERT INTO UserMatch (white_user1, black_user2,time_start,time_stop,chessboard_fen)
            VALUES (%s, %s, NOW(), NULL, %s)"""

        chessboard = chess.Board()

        ongoing_match_id = self.get_active_match(ID_white1, ID_black2)
        log.debug(f"Start_match.ongoing_match = {ongoing_match_id}")

        # check there is not an active game between the two players
        if ongoing_match_id is None:
            values = (ID_white1, ID_black2, chessboard.fen())
            self.cursor.execute(sql, values)
            self.db.commit()
            log.debug(f"Match started between {ID_white1} and {ID_black2}")
            return True
        else:
            log.error(
                f"There is already an ongoing match between the two players: {ID_white1} and {ID_black2}"
            )
            return False

    def stop_match(self, ID_white1: str, ID_black2: str) -> bool:
        """stop a match record into UserMatch with updating the time_top attribute to the current time"""

        if not ID_white1 or not ID_black2:
            log.error(f"Invalid parameters: {ID_white1}, {ID_black2}")
            return False

        sql = """UPDATE UserMatch UM SET time_stop = NOW() WHERE ID_Match = %s"""

        ongoing_match_id = self.get_active_match(ID_white1, ID_black2)
        log.debug(f"Start_match.ongoing_match = {ongoing_match_id}")

        # check there is not an active game between the two players
        if ongoing_match_id is not None:
            self.cursor.execute(sql, (ongoing_match_id,))
            self.db.commit()
            log.debug(f"Match stopped between {ID_white1} and {ID_black2}")
            return True
        else:
            log.error(
                f"There is not an ongoing match between the two players: {ID_white1} and {ID_black2}"
            )
            return False

    def get_match_chessboard(self, match_id: str) -> str | None:
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
            log.error(f"Match not found: {match_id}")
            return None

        return chessboard_fen[0]

    def add_move(self, match_id: str, move_uci: str) -> bool:
        """update chessboard attribute in the match with match_id to make a move"""

        if not match_id:
            log.error("Match_id and move_uci cannot be empty")
            return False

        chessboard_fen = self.get_match_chessboard(match_id)

        if chessboard_fen is None:
            log.error(
                f"Cannot query chessboard_fen from: the match does not exist: {match_id}"
            )
            return

        try:
            chessboard = chess.Board(fen=chessboard_fen)
            chessboard.push_uci(move_uci)
        except Exception as err:
            log.error(f"Cannot update chessboard: {err}")
            return False

        update = "UPDATE UserMatch UM SET chessboard_fen = %s WHERE ID_Match = %s;"

        try:
            self.cursor.execute(update, (chessboard.fen(), match_id))
            self.db.commit()
            log.error(f"Match with ID:{match_id} updated successfully")
            return True
        except mysql.connector.Error as err:
            log.error(f"Cannot update chessboard: {err}")
            return False

    def get_active_match(self, ID_user1: str, ID_user2: str) -> str | None:
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

        self.cursor.execute(query, (ID_user1, ID_user2, ID_user2, ID_user1))
        result = self.cursor.fetchone()

        if result is None:
            log.error(
                f"No active match found between the specified users: {ID_user1}, {ID_user2}"
            )
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
            try:
                self.cursor.execute(table[0])
            except mysql.connector.Error as err:
                log.error(f"Cannot drop table {table[0]}: {err}")
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
            log.error(f"Cannot setup database: {err}")
            return False
