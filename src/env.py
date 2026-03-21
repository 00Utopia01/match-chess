"""
This module hendle .env loading and reading
"""

import os
import re
import sys

from dotenv import load_dotenv

from src.logger import LOGGER as log


TG_TOKEN = None
DB_USER = None
DB_HOST = None
DB_PASSWORD = None
DB_DATABASE = None

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


def setup():
    """Load all env variables"""

    global TG_TOKEN, DB_USER, DB_HOST, DB_PASSWORD, DB_DATABASE
    is_bootable = True

    log.info("Loading env variables...")

    if not load_dotenv():
        log.critical("No .env file found (could be in a sub directory)")
        sys.exit(1)


    TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DB_USER = os.getenv("DB_USER")
    DB_HOST = os.getenv("DB_HOST")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DATABASE = os.getenv("DB_DATABASE")

    if not check_token(TG_TOKEN):
        is_bootable = False
    
    if DB_USER is None:
        log.critical("No DB_USER found in env variables (could be empty)")
        is_bootable = False

    if DB_HOST is None:
        log.critical("No DB_HOST found in env variables (could be empty)")
        is_bootable = False
    
    if DB_PASSWORD is None:
        log.critical("No DB_PASSWORD found in env variables (could be empty)")
        is_bootable = False
    
    if DB_DATABASE is None:
        log.critical("No DB_DATABASE found in env variables (could be empty)")
        is_bootable = False
    
    if not is_bootable:
        sys.exit(1)

setup()
