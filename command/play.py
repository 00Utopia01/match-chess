"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking
from src.db_manager import DB as db
from src.logger import LOGGER as log

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


def create_button(
    p1_id: str, mode: tuple[int, bool], p1_firstname: str
) -> InlineKeyboardMarkup | None:
    """create button layout for match_request_msg()"""

    if not p1_id.isdigit():
        log.debug("Invalid P1_ID in create_button()")
        return None
    if mode[0] != 1 and mode[0] != 2:
        log.debug("Invalid Mode in create_button()")
        return None

    accept_button = InlineKeyboardButton(
        "I accept", callback_data=f"usr:accept_match_{p1_id}_{mode[0]}_{p1_firstname}"
    )
    refuse_button = InlineKeyboardButton(
        "I refuse", callback_data=f"usr:refuse_match_{p1_id}_{mode[0]}_{p1_firstname}"
    )

    options_layout = [[accept_button, refuse_button]]

    return InlineKeyboardMarkup(options_layout)


def set_text(p1_firstname: str, mode: tuple[int, bool]) -> str:
    """create text for match_request_msg()"""
    _text = f"{p1_firstname} invited you to a match"

    if mode[0] != 1 and mode[0] != 2:
        log.debug("Invalid Mode Code in set_text()")
        return ""

    if mode[1]:
        if mode[0] == 1:
            _text = _text + " where you are black"
        else:
            _text = _text + " where you are white"

    return _text


# pylint: disable=too-many-arguments
async def match_request_msg(
    *,
    p1_id: str,
    p2_id: str,
    mode: tuple[int, bool],
    p1_firstname: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """message sent to request a match"""
    if update.effective_user is None:
        return

    text = set_text(p1_firstname, mode)

    if text == "":
        return

    button_interface = create_button(p1_id, mode, p1_firstname)

    if button_interface is None:
        return

    await context.bot.send_message(
        chat_id=p2_id,
        text=text,
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

    if username.isdigit():
        temp = db.get_username(username)
        if isinstance(temp, str):
            username = temp
        else:
            log.debug("No username found in db")
            return ""
    return username


def get_color(mode: str) -> tuple[int, bool]:
    """from a mode string get the color of p1"""
    is_forced = False
    match mode:
        case "-w":
            p1_is_white = int(1)
            is_forced = True
        case "-b":
            p1_is_white = int(0)
            is_forced = True
        case _:
            p1_is_white = randint(0, 1)
    return (p1_is_white, is_forced)


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
    if update.effective_user.username is None:
        return

    p1_firstname = update.effective_user.first_name

    p1_username = update.effective_user.username
    p2_username = edit_username(context.args[0])

    if p2_username == "":
        log.debug("no username faund with this id")
        return

    p2_id = get_p2_id(p2_username=p2_username, p1_username=p1_username)

    if p2_id == "Self Match":
        await self_match_msg(update)
        return
    if p2_id == "No User DB":
        await no_user_db_msg(update, context)
        return

    mode = get_color(get_mode(context.args))

    await match_request_msg(
        p1_id=str(update.effective_user.id),
        p2_id=p2_id,
        mode=mode,
        p1_firstname=p1_firstname,
        update=update,
        context=context,
    )
