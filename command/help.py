from telegram import Update
from telegram.ext import \
    ContextTypes  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the user a list of all commands"""
    if not update.message or not update.effective_user:
        return

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=(
            "List of available commands:\n" "/start\n" "/challenge"
        ),  # Accept and deny commands to be added
    )
