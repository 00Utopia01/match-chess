"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telegram import Update
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
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(filename="log/bot.log", maxBytes=2000000, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Token setup >--------------------------------

logger.debug("Loading Token...")

if not load_dotenv():
    logger.critical("No '.env' file found")
    exit(1)

TOKEN = os.getenv("TELEGRAM-TOKEN")
if TOKEN is None:
    logger.critical("No TOKEN found in environment variables")
    exit(1)



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


if __name__ == "__main__":
    # create an application with a bot TOKEN
    application = ApplicationBuilder().token(TOKEN).build()

    # tells the created application to listen to the "/start" command
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    application.run_polling()
