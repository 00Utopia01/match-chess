"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import sys

from telegram import Update
from telegram.error import InvalidToken, NetworkError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src import env
from src.logger import LOGGER as log

log.info("------------------- Fresh Start -------------------")



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

    # Token setup >--------------------------------

    log.info("Loading Token...")


    TOKEN = env.get_token()
    if TOKEN == "" or not env.check_token(TOKEN):
        sys.exit(1)
    else:
        log.info("Setting telegram bot token...")

    # Bot Application setup >--------------------------------

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
