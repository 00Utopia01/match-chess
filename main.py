"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import os
import re
import sys

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

from src import logger

# Logger config >-------------------------------

log = logger.setup()


# Token setup >--------------------------------


def get_dotenv() -> str:
    """return the path for .env file"""
    path = ".env"
    if not os.path.exists(path):
        log.warning("No '.env' file found in defoult path. OVERRIDE with custom path")
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


log.info("Loading Token...")


TOKEN = get_token(get_dotenv())
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
    log.info("Starting...")

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
        log.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        log.critical("Network error found")
        sys.exit(1)
