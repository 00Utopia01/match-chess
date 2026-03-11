"""
This module hendle the logger logic
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup() -> logging.Logger:
    """create, setup and configure a logger"""
    pattern_const = "%(asctime)s | %(filename)s > %(levelname)s: %(message)s"
    dateformat_const = "%d/%m/%Y %H:%M:%S"
    formatter = logging.Formatter(pattern_const, dateformat_const)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    if not os.path.exists("./log"):
        os.makedirs("./log")

    file_handler = RotatingFileHandler(
        filename="log/bot.log", maxBytes=2000000, backupCount=5  # 2000000byte == 2MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


LOGGER = setup()
