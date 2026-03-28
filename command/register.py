"""Function that regeister the user in the DataBase"""

from telegram import Update
from telegram.ext import ContextTypes

from src.db_manager import DB as db
from src.logger import LOGGER as log

# Text and Button >--------------------------


async def already_logged_mes_err(message_id: int, user_id: str, context: ContextTypes.DEFAULT_TYPE):
    """send 'alreday logged' message error"""
    await context.bot.edit_message_text(
        message_id=message_id,
        chat_id=user_id,
        text="You are already logged in"
    )


async def registration_complete_mes(message_id: int, user_id: str, context: ContextTypes.DEFAULT_TYPE):
    """send 'registration Complete' message"""
    await context.bot.edit_message_text(
            message_id=message_id,
            chat_id=user_id,
            text="Registration completed   <i>Good luck</i>",
            parse_mode="HTML",
        )


async def generic_db_mes_err(message_id: int, user_id: str, context: ContextTypes.DEFAULT_TYPE):
    """send 'Generic' message error"""
    await context.bot.edit_message_text(
            message_id=message_id,
            chat_id=user_id,
            text="Something went wrong",
            )

# Command >------------------------------------


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register a user in the Database"""
    if update.effective_user is None:
        log.error("No effective_user in register()")
        return

    user_id = str(update.effective_user.id)
    username = update.effective_user.username

    if username is None:
        log.debug(f"No username found for {user_id}, overriding")
    message = await context.bot.send_message(chat_id=user_id, text="Loading...")

    if isinstance(db.get_username(user_id), str):
        log.warning(f"{user_id} is already logged")
        await already_logged_mes_err(message.id, user_id, context)
        return

    if db.insert_user(user_id, username):
        await registration_complete_mes(message.id, user_id, context)
    else:
        log.error("Something went wrong during db.insert_user() in register()")
        await generic_db_mes_err(message.id, user_id, context)
    return
