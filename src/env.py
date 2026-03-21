"""
This module hendle .env loading and reading
"""

import os
import re
import sys

from dotenv import load_dotenv

from src.logger import LOGGER as log


class Env:
    """Basic class to store .env variables"""

    # pylint: disable=too-many-arguments
    def __init__(self, *, token: str, user: str, host: str, psw: str, db: str):
        self.__token: str = token
        self.__db_user: str = user
        self.__db_host: str = host
        self.__db_password: str = psw
        self.__db_database: str = db

    def get_token(self) -> str:
        """get telegram token"""
        return self.__token

    def get_user(self) -> str:
        """get database user"""
        return self.__db_user

    def get_host(self) -> str:
        """get database host"""
        return self.__db_host

    def get_password(self) -> str:
        """get database password"""
        return self.__db_password

    def get_database(self) -> str:
        """get database name"""
        return self.__db_database


def check_token(token: str | None) -> bool:
    """chek if token is None or in a wrong format"""
    regex_const = "^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$"

    if token is None:
        log.critical("No TOKEN found in env variables (could be empty)")
        return False

    if re.fullmatch(regex_const, token) is None:
        log.critical("Invalid TOKEN formatting")
        return False

    return True


def setup() -> Env:
    """Load all env variables"""
    is_bootable = True

    log.info("Loading env variables...")

    if not load_dotenv():
        log.critical("No .env file found (could be in a sub directory)")
        sys.exit(1)

    _token = os.getenv("TELEGRAM_TOKEN")
    _user = os.getenv("DB_USER")
    _host = os.getenv("DB_HOST")
    _password = os.getenv("DB_PASSWORD")
    _database = os.getenv("DB_DATABASE")

    if not check_token(_token):
        is_bootable = False

    if _user is None:
        log.critical("No DB_USER found in env variables (could be empty)")
        is_bootable = False

    if _host is None:
        log.critical("No DB_HOST found in env variables (could be empty)")
        is_bootable = False

    if _password is None:
        log.critical("No DB_PASSWORD found in env variables (could be empty)")
        is_bootable = False

    if _database is None:
        log.critical("No DB_DATABASE found in env variables (could be empty)")
        is_bootable = False

    if not is_bootable:
        sys.exit(1)

    env = Env(
        token=str(_token),
        user=str(_user),
        host=str(_host),
        psw=str(_password),
        db=str(_database),
    )
    return env


ENV = setup()
