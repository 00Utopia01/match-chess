"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking

# from chess import Board
# from telegram.error import InvalidToken, NetworkError
# from telegam.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


# from src.Chess import create_game


# class DB:
#    """ Simulate our DB"""
#    def __init__(_id:int|None=None,_P1:int|None=None,_P2:int|None=None,_board:Board|None=None):
#        game_id = _id
#        P1 = _P1
#        P2 = _P2
#        board = _board


def query1(temp: str):  # TEMP
    """placeholder of a query"""
    if temp:
        return True
    return False


def query2(temp: str):  # TEMP
    """placeholder of a query"""
    if temp:
        return 1234
    return 1234


def query3(temp: str):  # TEMP
    """placeholder of a query"""
    if temp:
        return 7584929619
    return 4321


async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """cerca player online"""
    if not context:  # TEMP
        return  # TEMP

    user_id: int
    if update.effective_user is not None:
        user_id = update.effective_user.id
    matchmaking(user_id)

    if update.message is not None:
        await update.message.reply_text("WIP")

    return


async def custom_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """cerca l'utente specifico"""

    if context.args is None or update.effective_user is None:
        return

    if update.message is None or update.effective_chat is None:
        return

    if context.args[0] == update.effective_user.name:
        await update.message.reply_text("You can't challenge yourself!")
        return

    if not query1(context.args[0]):  # TEMP
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

    p2_id = query3(context.args[0])  # TEMP
    p1_is_white = bool(randint(0, 1))

    if len(context.args) > 2 and context.args[1] == ("-w" or "-W"):
        p1_is_white = True
    elif len(context.args) > 2 and context.args[1] == ("-b" or "-B"):
        p1_is_white = False

    accept_button = InlineKeyboardButton("I accept", callback_data="match accepted")
    refuse_button = InlineKeyboardButton("I refuse", callback_data="match declined")

    options_layout = [[accept_button, refuse_button]]

    button_interface = InlineKeyboardMarkup(options_layout)

    await context.bot.send_message(
        chat_id=p2_id,
        text=f"{update.effective_user.full_name} invited you tu a match",
        reply_markup=button_interface,
    )

    print("godo")

    if p1_is_white:  # TEMP
        return

    return None


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends an invite to an user with the corresponding ID"""

    if not update.message or not update.effective_user:
        return

    if not context.args:
        await online(update, context)
        return

    if len(context.args) >= 1:
        await custom_match(update, context)
        return

    sender_id = update.effective_user.id
    sender_username = update.effective_user.first_name

    if sender_id == int(context.args[0]):
        await update.message.reply_text("You can't challenge yourself!")
        return

    challengeduser_id = int(context.args[0])

    # Here should go the logic that connects the 2 users via database

    try:
        await update.message.reply_text("Challenge Sent")
        await context.bot.send_message(
            chat_id=challengeduser_id,
            text=f"{sender_username} (ID = {sender_id}) has sent you an invite!",
        )
    except BadRequest:
        await update.message.reply_text(
            "Error delivering the challenge. ID code may be invalid or non-existent."
        )
    except TelegramError:
        await update.message.reply_text(
            "An unexpected error occurred while sending the challenge."
        )
