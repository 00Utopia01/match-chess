"""
This module hendle the logger logic
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup() -> logging.Logger:
    """create, setup and configure a logger"""
    pattern = "%(asctime)s | %(filename)s > %(levelname)s: %(message)s"
    dateformat = "%d/%m/%Y %H:%M:%S"
    formatter = logging.Formatter(pattern, dateformat)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    if not os.path.exists("./log"):
        os.makedirs("./log")

    file_handler = RotatingFileHandler(
        filename="log/bot.log", maxBytes=2000000, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
