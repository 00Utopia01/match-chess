"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update

# from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking

# from src.db_manager import DB


# QUERY TEMP >---------------------------


def query1(temp: str) -> bool:  # TEMP
    """placeholder of a query"""
    if temp:
        return True
    return False


def query2(temp: str) -> str:  # TEMP
    """placeholder of a query"""
    if temp:
        return "1234"
    return "1234"


def query3(temp: str):  # TEMP
    """placeholder of a query"""
    if temp:
        return "848994744"  # "7584929619"
    return "4321"


def query4(temp, temp2):  # TEMP
    """placeholder of a query"""
    if temp:
        if temp2:
            return
    return


# Messages >---------------------------------


async def self_match(update: Update):
    """message sent when self_match error occur"""

    if update.message is None:
        return

    await update.message.reply_text("You can't challenge yourself!")
    return


async def no_user_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """message sent when the user is not in the DB"""

    if update.effective_chat is None:
        return

    link_button = InlineKeyboardButton(
        "copy link", copy_text=CopyTextButton("https://t.me/mchessqd_bot")
    )

    markup = InlineKeyboardMarkup([[link_button]])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="No user found with this name, check if is correct or invite them with this link",
        reply_markup=markup,
    )
    return


async def match_request(
    p2_id: str, mode: int, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """message sent to request a match"""
    if update.effective_user is None:
        return

    accept_button = InlineKeyboardButton("I accept", callback_data="match accepted")
    refuse_button = InlineKeyboardButton("I refuse", callback_data="match declined")

    options_layout = [[accept_button, refuse_button]]

    button_interface = InlineKeyboardMarkup(options_layout)

    _text = f"{update.effective_user.full_name} invited you to a match"

    if mode == 1:
        _text = _text + " where you are black"

    if mode == 2:
        _text = _text + " where you are white"

    await context.bot.send_message(
        chat_id=p2_id,
        text=_text,
        reply_markup=button_interface,
    )


# Logic >-------------------------------------------


async def custom_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends an invite to an user with the corresponding ID"""

    if context.args is None or update.effective_user is None:
        return

    if update.message is None or update.effective_chat is None:
        return

    if context.args[0] == update.effective_user.name:
        await self_match(update)
        return

    if not query1(context.args[0]):  # TEMP
        await no_user_db(update, context)
        return

    p2_id = query3(context.args[0])  # TEMP

    p1_is_white = bool(randint(0, 1))
    mode = 0

    print(context.args)

    if len(context.args) == 2 and context.args[1] == ("-w" or "-W"):
        p1_is_white = True
        mode = 1
    elif len(context.args) == 2 and context.args[1] == ("-b" or "-B"):
        p1_is_white = False
        mode = 2
    else:
        return

    if p1_is_white:
        query4(update.effective_user.id, p2_id)
    else:
        query4(p2_id, update.effective_user.id)

        print(mode)

    await match_request(p2_id, mode, update, context)

    return


async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """create a match vs random player online"""
    if not context:  # TEMP
        return  # TEMP

    user_id: int
    if update.effective_user is not None:
        user_id = update.effective_user.id
    matchmaking(user_id)

    if update.message is not None:
        await update.message.reply_text("WIP")

    return


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Decode commands parameters"""

    if not update.message or not update.effective_user:
        return

    if context.args is None:  # check
        await online(update, context)
        return

    if len(context.args) >= 1:
        await custom_match(update, context)
        return

    return
