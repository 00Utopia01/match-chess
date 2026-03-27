"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking
from src.db_manager import DB as db

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


# pylint: disable=too-many-arguments
async def match_request_msg(
    *,
    p1_id: str,
    p2_id: str,
    mode: int,
    p1_username: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """message sent to request a match"""
    if update.effective_user is None:
        return

    accept_button = InlineKeyboardButton(
        "I accept", callback_data=f"usr:accept_match_{p1_id}_{mode}_{p1_username}"
    )
    refuse_button = InlineKeyboardButton(
        "I refuse", callback_data=f"usr:refuse_match_{p1_id}_{mode}_{p1_username}"
    )

    options_layout = [[accept_button, refuse_button]]

    button_interface = InlineKeyboardMarkup(options_layout)

    _text = f"{p1_username} invited you to a match"

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


def edit_username(username: str) -> str:
    """edit username args"""
    if username[0] == "@":
        username = username[1:]
    return username


def get_color(mode: str) -> int:
    """from a mode string get the color of p1"""
    match mode:
        case "-w":
            p1_is_white = int(1)
        case "-b":
            p1_is_white = int(0)
        case _:
            p1_is_white = randint(0, 1)
    return p1_is_white


def get_mode(args: list[str]) -> str:
    """get from args the mode string if is formated correctly"""
    mode = ""
    if len(args) >= 2 and args[1] == ("-w" or "-W"):
        mode = "-w"
    if len(args) >= 2 and args[1] == ("-b" or "-B"):
        mode = "-b"
    return mode


def get_p2_id(*, p1_username: str, p2_username: str) -> str:
    """get id 2 from db"""
    if p2_username == p1_username:
        return "Self Match"
    p2_id = db.get_user_id(p2_username)
    if p2_id is None:
        return "No User DB"
    return p2_id


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

    p1_username = update.effective_user.full_name
    p2_username = edit_username(context.args[0])

    p2_id = get_p2_id(p2_username=p2_username, p1_username=p1_username)

    if p2_id == "Self Match":
        await self_match_msg(update)
        return
    if p2_id == "No User DB":
        await no_user_db_msg(update, context)
        return

    p1_is_white = int(get_color(get_mode(context.args)))

    await match_request_msg(
        p1_id=str(update.effective_user.id),
        p2_id=p2_id,
        mode=p1_is_white,
        p1_username=p1_username,
        update=update,
        context=context,
    )
