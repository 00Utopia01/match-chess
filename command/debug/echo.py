from telegram import Update
from telegram.ext import \
    ContextTypes  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """this re-prints the message sent to the bot"""
    if not update.effective_chat or not update.message or not update.message.text:
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )
