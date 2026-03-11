"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import sys

from telegram import Update
from telegram.error import (
    InvalidToken,
    NetworkError,
    BadRequest,
    TelegramError,
)
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

# Token setup >--------------------------------

log.info("Loading Token...")


TOKEN = env.get_token(env.set_path())
if TOKEN == "" or not env.check_token(TOKEN):
    sys.exit(1)

# Bot Commands >------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat or not update.effective_user:
        return

    username = update.effective_user.first_name
    userid = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Welcome {username} to the Chess bot!\n"
            f"Your ID is {userid}, share it with your friends to play togheter"
        ),
    )


async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends an invite to an user with the corresponding ID"""
    if not update.message or not update.effective_user:
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Non-existent or invalid ID code given")
        return

    sender_id = update.effective_user.id
    sender_username = update.effective_user.first_name

    if sender_id == int(context.args[0]):
        await update.message.reply_text("You can't challenge yourself!")
        return

    challengeduser_id = int(context.args[0])

    # Here should go the logic that connects the 2 users via database

    try:
        await update.message.reply_text("Challenge Sent")
        await context.bot.send_message(
            chat_id=challengeduser_id,
            text=f"{sender_username} (ID = {sender_id}) has sent you an invite!",
        )
    except BadRequest:
        await update.message.reply_text(
            "Error delivering the challenge. ID code may be invalid or non-existent."
        )
    except TelegramError:
        await update.message.reply_text(
            "An unexpected error occurred while sending the challenge."
        )


async def commands_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the user a list of all commands"""
    if not update.message or not update.effective_user:
        return

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=(
            "List of available commands:\n" "/start\n" "/challenge"
        ),  # Accept and deny commands to be added
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

    # tells the created application to listen to the varius commands
    commands_list_handler = CommandHandler("commands", commands_list)
    start_handler = CommandHandler("start", start)
    challenge_handler = CommandHandler("challenge", challenge)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(challenge_handler)
    application.add_handler(commands_list_handler)

    try:
        application.run_polling()
    except InvalidToken:
        log.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        log.critical("Network error found")
        sys.exit(1)
