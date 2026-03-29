"""Welcoming function"""

# pylint: disable=duplicate-code

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from command.eula import eula
from command.optout import optout
from command.register import register
from src.logger import LOGGER as log

# Text and Button >------------------------------------------


def create_button() -> InlineKeyboardMarkup:
    """Create button markup"""
    optout_button = InlineKeyboardButton("optout", callback_data="usr:start_optout")
    eula_button = InlineKeyboardButton("eula", callback_data="usr:start_eula")
    register_button = InlineKeyboardButton(
        "register", callback_data="usr:start_register"
    )

    options_layout = [[optout_button, eula_button, register_button]]

    return InlineKeyboardMarkup(options_layout)


# Command >------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat or not update.effective_user:
        log.error("No effective_chat or effective_user in start()")
        return

    userid = str(update.effective_user.id)

    markup = create_button()
    await context.bot.send_message(
        chat_id=userid,
        text=(
            f"Welcome <b>{update.effective_user.first_name}</b> to Match Chess!\n"
            "You can use this bot to play with your friends locally, in a group or in DM\n\n"
            "For some online features"
            "we need to gather some information about your account.\n\n"
            "<i>To know more, use /eula or use the button below.</i>"
        ),
        parse_mode="HTML",
        reply_markup=markup,
    )


# CallBack >------------------------------------------------------------


async def start_optout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback of 'optout' button of /start"""
    if update.effective_user is None:
        log.error("No effective_user foud in start_optout_callback()")
        return

    query = update.callback_query
    if query is None or query.message is None:
        log.error("No query foud in start_optout_callback()")
        return

    await query.answer()
    await context.bot.delete_message(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
    )
    await optout(update, context)


async def start_eula_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback of 'eula' button of /start"""
    if update.effective_user is None:
        log.error("No effective_user foud in start_eula_callback()")
        return

    query = update.callback_query
    if query is None or query.message is None:
        log.error("No query or query.message foud in start_eula_callback()")
        return

    await query.answer()
    await context.bot.delete_message(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
    )

    await eula(update, context)


async def start_register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback of 'register' button of /start"""
    if update.effective_user is None:
        log.error("No effective_user foud in start_register_callback()")
        return

    query = update.callback_query

    if query is None or query.message is None:
        log.error("No query or query.message foud in start_register_callback()")
        return

    await query.answer()
    await context.bot.delete_message(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
    )

    await register(update, context)
