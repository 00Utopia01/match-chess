"""Welcoming function"""

from telegram import Update
from telegram.ext import ContextTypes

from src.db_manager import DB as db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat or not update.effective_user:
        return

    username = update.effective_user.username
    userid = str(update.effective_user.id)

    if not db.insert_user(user_id=userid, username=username):
        await context.bot.send_message(
            chat_id=userid,
            text=(
                "You are already logged.\n" "If you want to delete your info use /eula"
            ),
        )
    else:
        await context.bot.send_message(
            chat_id=userid,
            text=(
                f"Welcome <b>{update.effective_user.full_name}</b> to Match Chess!\n"
                "In order to use this bot, we need to gather some information about your account.\n"
                "<i>To know more or delete your's information use /eula</i>"
            ),
            parse_mode="HTML",
        )
