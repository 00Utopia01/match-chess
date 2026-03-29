"""Function that delete the user from the DataBase"""  # WIP

from telegram import Update
from telegram.ext import ContextTypes

from src.logger import LOGGER as log

# Command >----------------------------


async def optout(update: Update, context: ContextTypes.DEFAULT_TYPE):  # WIP
    """Delete user from DataBsase"""
    if update.effective_user is None:
        log.error("No effective_user in optout()")
        return
    await context.bot.send_message(chat_id=update.effective_user.id, text="WIP")
