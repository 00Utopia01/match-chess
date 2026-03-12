"""
This module hendle .env loading and reading
"""

import os
import re

from dotenv import load_dotenv

from src.logger import LOGGER as log


def take_path_input():
    return input("direct path to file: ")


def set_path() -> str:
    """return the path for .env file"""

    while True:
        path = take_path_input()
        if path[-4:] == ".env":
            log.debug('custom path is "%s"', path)
            break

        print("The specified path does not end with a .env file, retry")
    return path


def get_token() -> str:
    """get token from .env file"""

    token = os.getenv("TELEGRAM_TOKEN")

    if token is not None:
        return token

    # log.error("TELEGRAM_TOKEN variable not found or empty")

    # try to find .env file
    if not load_dotenv():
        log.error(
            "No .env file in default path (could be empty), overriding with custom path "
        )
        # if .env cannot be found, ask the user to input .env path
        if not load_dotenv(dotenv_path=set_path()):
            log.critical("No '.env' file found in custom path (could be empty)")
            return ""

    token = os.getenv("TELEGRAM_TOKEN")
    return token


def check_token(token: str) -> bool:
    """chek if token is None or in a wrong format"""
    regex_const = "^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$"

    if re.fullmatch(regex_const, token) is None or token is None:
        log.critical("Invalid token formatting")
        return False

    return True
