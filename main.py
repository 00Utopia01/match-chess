"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
token = os.getenv("TELEGRAM-TOKEN")
if token is None:
    raise ValueError("No TOKEN found in environment variables")

LOGGING_PATTERN = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_PATTERN, level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat:
        return

    username = update.effective_user.first_name
    userid = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text= (
            f"Welcome {username} to the Chess bot!\n"
            f"Your ID is {userid}, share it with your friends to play togheter"
        )
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
    # create an application with a bot token
    application = ApplicationBuilder().token(token).build()

    # tells the created application to listen to the "/start" command
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    application.run_polling()
