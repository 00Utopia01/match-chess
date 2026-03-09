"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telegram import Update
from telegram.error import InvalidToken, NetworkError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logger config >-------------------------------

LOGGING_PATTERN = "%(asctime)s | %(filename)s > %(levelname)s: %(message)s"
LOGGING_DATEFORMAT = "%d/%m/%Y %H:%M:%S"
formatter = logging.Formatter(LOGGING_PATTERN, LOGGING_DATEFORMAT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(
    filename="log/bot.log", maxBytes=2000000, backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


# Token setup >--------------------------------


def get_token() -> str:
    """get token from .env file"""

    if not load_dotenv():
        logger.critical("No '.env' file found")
        return ""

    token = os.getenv("TELEGRAM-TOKEN")
    if token is None:
        logger.critical("No TOKEN found in environment variables")
        return ""

    return token


def check_token(token: str) -> bool:
    """chek token format"""

    regex_const = "^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$"

    if re.fullmatch(regex_const, token) is None:
        logger.critical("Invalid token formatting")
        return False

    return True


logger.info("Loading Token...")
TOKEN = get_token()
if TOKEN == "" or not check_token(TOKEN):
    sys.exit(1)

# Bot Commands >------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """this re-prints the message sent to the bot"""
    if not update.effective_chat or not update.message or not update.message.text:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """command to turn into upcase a given text"""
    if not update.effective_chat:
        return

    text_caps = " ".join(context.args or []).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


# Bot Configuration >-------------------------------------

if __name__ == "__main__":
    logger.info("Starting...")

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    try:
        application.run_polling()
    except InvalidToken:
        logger.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        logger.critical("Network error found")
        sys.exit(1)
