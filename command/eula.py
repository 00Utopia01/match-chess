"""Function to either accept or refuse eula policies in order to use the bot"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

# from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


async def eula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function creates an interface and shows the user the EULA paragraph"""

    if not update.effective_chat or not update.effective_user:
        return

    accept_button = InlineKeyboardButton("I accept", callback_data="usr:accept_eula")
    refuse_button = InlineKeyboardButton("I decline", callback_data="usr:decline_teula")

    options_layout = [[accept_button, refuse_button]]

    button_interface = InlineKeyboardMarkup(options_layout)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "By starting and using this Telegram Bot,"
            " you agree to the following terms and conditions.\n"
            "we need to collect and store some basic information from your Telegram profile.\n"
            "\nWhat we collect?\n"
            "We only collect your Telegram user_id and your username.\n"
            "This data is strictly used to identify you in our database, "
            "pair you with other players for matchmaking and maintain leaderboards.\n"
            "We do not sell, rent, or share your personal data with any third parties. "
            " Your data remains within the bot's secure database."
        ),
        reply_markup=button_interface,
    )
