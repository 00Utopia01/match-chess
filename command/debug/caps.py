"""Function that rewrites a given string in CAPS format"""

from telegram import Update
from telegram.ext import (  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,
    ContextTypes,
)

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """command to turn into upcase a given text"""
    if not update.effective_chat:
        return

    text_caps = " ".join(context.args or []).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
