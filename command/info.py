"""Module that handles the /info command"""

from telegram import Update
from telegram.ext import ContextTypes

from src.db_manager import DB as db


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the user a list of useful information about his account relative to the bot"""
    if not update.effective_chat:
        return
    if not update.effective_user or not update.effective_user.id:
        return
    if not update.effective_user.username or not update.effective_chat.id:
        return

    if isinstance(db.get_username(str(update.effective_user.id)), str):
        txt = "You are logged into the server!"
    else:
        txt = "You are not logged into the server!"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "<b>Here is a list of information about you:</b>\n"
            f"<i>Username: {update.effective_user.username}</i>\n"
            f"<i>First username : {update.effective_user.first_name}</i>\n"
            f"<i>Chat id:<tg-spoiler> {update.effective_chat.id} </tg-spoiler> </i>\n"
            f"<i>User id:<tg-spoiler> {update.effective_user.id} </tg-spoiler> </i>\n"
            f"<i>{txt}</i>\n"
        ),
        parse_mode="HTML",
    )
