"""Function that shows the list of all available commands"""

from telegram import Update
from telegram.ext import (  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,
    ContextTypes,
)

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the user a list of all commands"""
    if not update.message or not update.effective_user:
        return

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=(
            "<b>List of available commands:</b>\n"
            "<i>/start</i>\n"
            "<i>/commands</i>  (to see the commands list)\n"
            "<i>/eula</i>  (To read and accept/refuse the eula agreement)\n"
            "<i>/play [USER ID]</i>  (To start an online Chess match)"
        ),
        parse_mode="HTML",
    )
