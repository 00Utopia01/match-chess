"""Function to either accept or refuse eula policies in order to use the bot"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,
    ContextTypes,
)


async def eula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function creates an interface and shows the user the EULA paragraph"""

    if not update.effective_chat or not update.effective_user:
        return

    accept_button = InlineKeyboardButton("I accept", callback_data="accepted")
    refuse_button = InlineKeyboardButton("I refuse", callback_data="refused")

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


async def eula_output(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """This function lets the user accept or refuse eula via interface"""

    if not update.effective_chat or not update.effective_user:
        return

    eula_query = update.callback_query

    if not eula_query:
        return

    await eula_query.answer()

    if eula_query.data == "accepted":
        await eula_query.edit_message_text("You succesfully accepted EULA!")

    elif eula_query.data == "refused":
        # here goes the logic that removes the user from the database
        await eula_query.edit_message_text(
            "You refused EULA!\n Unfortunately you cannot utilize this bot",
        )
