"""Function that delete the user from the DataBase"""  # WIP

from telegram import Update
from telegram.ext import ContextTypes

from src.db_manager import DB

# Command >----------------------------


async def optout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete user from DataBsase"""
    if not update.effective_user or not update.effective_user.id:
        return
    if not update.effective_user.username or not update.effective_user.username:
        return

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="You have been successfully removed from the server!",
    )
    DB.del_user(str(update.effective_user.id))
