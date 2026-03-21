"""
This module hendle .env loading and reading
"""

import os
import re
import sys

from dotenv import load_dotenv

from src.logger import LOGGER as log

class Env:
    def __initi__(self):
        self.TG_TOKEN:str | None = None
        self.DB_USER:str | None = None
        self.DB_HOST:str | None = None
        self.DB_PASSWORD:str | None = None
        self.DB_DATABASE:str | None= None


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

    env = Env()
    is_bootable = True

    log.info("Loading env variables...")

    if not load_dotenv():
        log.critical("No .env file found (could be in a sub directory)")
        sys.exit(1)


    env.TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
    env.DB_USER = os.getenv("DB_USER")
    env.DB_HOST = os.getenv("DB_HOST")
    env.DB_PASSWORD = os.getenv("DB_PASSWORD")
    env.DB_DATABASE = os.getenv("DB_DATABASE")

    if not check_token(env.TG_TOKEN):
        is_bootable = False

    if env.DB_USER is None:
        log.critical("No DB_USER found in env variables (could be empty)")
        is_bootable = False

    if env.DB_HOST is None:
        log.critical("No DB_HOST found in env variables (could be empty)")
        is_bootable = False

    if env.DB_PASSWORD is None:
        log.critical("No DB_PASSWORD found in env variables (could be empty)")
        is_bootable = False

    if env.DB_DATABASE is None:
        log.critical("No DB_DATABASE found in env variables (could be empty)")
        is_bootable = False

    if not is_bootable:
        del env
        sys.exit(1)
    return env

ENV = setup()
