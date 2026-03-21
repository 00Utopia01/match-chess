"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking

# from telegram.error import BadRequest, TelegramError


def get_username(user_id: str) -> str | None:  # TEMP
    """get the username of a specified user"""
    if user_id:
        return "username"
    return None


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


async def self_match_msg(update: Update):
    """message sent when self_match error occur"""

    if update.message is None:
        return

    await update.message.reply_text("You can't challenge yourself!")
    return


async def no_user_db_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def match_request_msg(
    p1_id: str,
    p2_id: str,
    mode: int,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """message sent to request a match"""
    if update.effective_user is None:
        return

    accept_button = InlineKeyboardButton(
        "I accept", callback_data=f"usr:accept_match_{p1_id}"
    )
    refuse_button = InlineKeyboardButton(
        "I refuse", callback_data=f"usr:refuse_match_{p1_id}"
    )

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


async def play_matchmaking(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if context.args is None:
        await play_matchmaking(update, context)
        return

    if len(context.args) >= 1:
        await challenge_user(update, context)
        return

    return


async def challenge_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """make a player (p1) send a challenge request to the user with the specified id (p2)
    the challenged user will receive a message with an identifier of the user who sent the challenge
    and two buttons to accept/decline the request

    Syntax: /challenge_user <user_id> [-w | -W | -b | -B]

    Args:
        user_id : the number associated with each player when they send /start
        [-w | -W] (optional): send a request where you play as white
        [-b | -B] (optional): send a request where you play as black

    Note:
        If the user doesn't specifies [-w | -W | -b | -B] a random side is chosen
    """

    if context.args is None or update.effective_user is None:
        return

    if update.message is None or update.effective_chat is None:
        return

    p2_id = context.args[0]

    if p2_id == update.effective_user.name:
        await self_match_msg(update)
        return

    p2_username = get_username(context.args[0])

    # If the user to challenge is not found in the database send error message
    if not p2_username:
        await no_user_db_msg(update, context)
        return

    # Decide which player starts with white pieces
    p1_is_white = bool(randint(0, 1))

    if len(context.args) > 2 and context.args[1] == ("-w" or "-W"):
        p1_is_white = True
    elif len(context.args) > 2 and context.args[1] == ("-b" or "-B"):
        p1_is_white = False

    mode = 1 if p1_is_white else 2

    await match_request_msg(
        p1_id=str(update.effective_user.id),
        p2_id=p2_id,
        mode=mode,
        update=update,
        context=context,
    )

    return None
