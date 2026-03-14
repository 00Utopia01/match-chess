"""Welcoming function"""

from telegram import Update
from telegram.ext import (  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,
    ContextTypes,
)

from command.debug.get_id import get_user_id

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat or not update.effective_user:
        return

    username = update.effective_user.first_name
    userid = get_user_id(update)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Welcome {username} to the Chess bot!\n"
            f"Your ID is {userid}, share it with your friends to play togheter"
        ),
    )
