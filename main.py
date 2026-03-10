"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import logging
import os

from dotenv import load_dotenv
from telegram.error import BadRequest, TelegramError
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
    if not update.effective_chat or not update.effective_user:
        return

    username = update.effective_user.first_name
    userid = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text= (
            f"Welcome {username} to the Chess bot!\n"
            f"Your ID is {userid}, share it with your friends to play togheter"
        )
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
    #Here should go the logic that connects the 2 users via database
    try:
        await update.message.reply_text("Challenge Sent")
        await context.bot.send_message(chat_id=challengeduser_id,
        text=f"{sender_username} (ID = {sender_id}) has sent you an invite!"
        )
    except BadRequest:
        await update.message.reply_text(
            "Error delivering the challenge. ID code may be invalid or non-existent."
        )
    except TelegramError:
        await update.message.reply_text("An unexpected error occurred while sending the challenge.")


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
    challenge_handler = CommandHandler("challenge", challenge)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(challenge_handler)

    application.run_polling()
