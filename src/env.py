"""
This module hendle .env loading and reading
"""

import os
import re

from dotenv import load_dotenv

from src.logger import LOGGER as log


def set_path() -> str:
    """return the path for .env file"""

    path = ".env"
    if not os.path.exists(path):
        log.warning("No '.env' file found in default path. OVERRIDE with custom path")
        while True:
            print("direct path to file: ", end="")
            path = input()
            if path[-4:] == ".env":
                log.debug('custom path is "%s"', path)
                break

            print("The specified path does not end with a .env file, retry")
    return path


def get_token(path: str) -> str:
    """get token from .env file"""

    if not load_dotenv(dotenv_path=path):
        log.critical("No '.env' file found in custom path (could be empty)")
        return ""

    token = os.getenv("TELEGRAM-TOKEN")
    if token is None:
        log.critical("No TELEGRAM-TOKEN found in environment variables")
        return ""

    return token


def check_token(token: str) -> bool:
    """chek token format"""

    regex_const = "^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$"

    if re.fullmatch(regex_const, token) is None:
        log.critical("Invalid token formatting")
        return False

    return True
