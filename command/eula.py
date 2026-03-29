"""Function to either accept or refuse eula policies in order to use the bot"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from command.optout import optout
from command.register import register
from src.logger import LOGGER as log

# Text and Button >--------------------------------------


def create_button() -> InlineKeyboardMarkup:
    """Create button markup for /eula"""
    refuse_button = InlineKeyboardButton(
        "optout", callback_data="usr:del_and_start_optout"
    )
    accept_button = InlineKeyboardButton(
        "register", callback_data="usr:del_and_start_register"
    )
    options_layout = [[refuse_button, accept_button]]
    return InlineKeyboardMarkup(options_layout)


# Command >------------------------------------------


async def eula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function creates an interface and shows the user the EULA paragraph"""
    if not update.effective_chat:
        log.error("No effective_chat in eula()")
        return

    button_interface = create_button()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "By starting and using this Telegram Bot,"
            " you agree to the following terms and conditions.\n"
            "we need to collect and store some basic information from your Telegram profile.\n"
            "\n<b>What we collect?</b>\n"
            "We only collect your Telegram <i>user_id</i> and your <i>username</i>.\n"
            "This data is strictly used to identify you in our database, "
            "pair you with other players for matchmaking and maintain leaderboards.\n"
            "We do not sell, rent, or share your personal data with any third parties. "
            "Your data remains within the bot's secure database."
        ),
        parse_mode="HTML",
        reply_markup=button_interface,
    )


# Callback >-------------------------------------


async def del_message_and_optout_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle callback of 'optout' button of /eula"""
    if update.effective_user is None:
        log.error("No effective_user in del_message_and_optout_callback()")
        return

    query = update.callback_query

    if query is None or query.message is None:
        log.error("No query or query.message in del_message_and_optout_callback()")
        return

    await context.bot.delete_message(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
    )
    await optout(update, context)


async def del_message_and_register_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle callback of 'register' button of /eula"""
    if update.effective_user is None:
        log.error("No effective_user in del_message_and_register_callback()")
        return
    query = update.callback_query

    if query is None or query.message is None:
        log.error("No query or query.message in del_message_and_register_callback()")
        return

    await context.bot.delete_message(
        chat_id=update.effective_user.id,
        message_id=query.message.message_id,
    )
    await register(update, context)
