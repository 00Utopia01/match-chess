"""Function to inizialize a match between 2 players"""

from random import randint

from telegram import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.chess_logic import matchmaking
from src.db_manager import DB as db
from src.logger import LOGGER as log

# Messages >---------------------------------


async def self_match_msg(update: Update):
    """Message sent when a player tryies to challenge himself"""
    if update.message is None:
        return

    await update.message.reply_text("You can't challenge yourself!")
    return


async def no_user_db_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message sent when fetching the opponent user fails"""

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
    p1_id: str, mode: str, p1_firstname: str
) -> InlineKeyboardMarkup | None:
    """Create button layout for match_request_msg()"""

    if not p1_id.isdigit():
        log.debug("Invalid P1_ID in create_button()")
        return None

    if mode not in ("white", "black"):
        log.error("Invalid mode cannot be setted into callback: %s", mode)
        return None

    # 1 = p1_id starts as white, 2 = 1 = p1_id starts as black
    mode_setting = 1 if mode == "white" else 2

    accept_button = InlineKeyboardButton(
        "I accept",
        callback_data=f"usr:accept_match_{p1_id}_{mode_setting}_{p1_firstname}",
    )
    refuse_button = InlineKeyboardButton(
        "I refuse",
        callback_data=f"usr:refuse_match_{p1_id}_{mode_setting}_{p1_firstname}",
    )

    options_layout = [[accept_button, refuse_button]]

    return InlineKeyboardMarkup(options_layout)


# pylint: disable=too-many-arguments
async def match_request_msg(
    *,
    p1_id: str,
    p2_id: str,
    mode: str,
    p1_firstname: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """message sent to request a match"""
    if update.effective_user is None:
        return

    if mode not in ("white", "black"):
        log.error("Invalid mode cannot be sent: %s", mode)

    opponents_mode = "black" if mode == "white" else "white"
    message = f"{p1_firstname} invited you to a match, where you are {opponents_mode}"

    button_interface = create_button(p1_id, mode, p1_firstname)

    if button_interface is None:
        return

    await context.bot.send_message(
        chat_id=p2_id,
        text=message,
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

    Syntax: /challenge_user <user_id | username> [-w | -W | -b | -B]

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

    p1_firstname = update.effective_user.first_name
    target_player = context.args[0]

    sender_id = str(update.effective_user.id)
    receiver_id = (
        target_player
        if target_player.isdigit()
        else db.get_user_id(target_player.removeprefix("@"))
    )

    if not receiver_id:
        await no_user_db_msg(update, context)
        log.error("Failed to fetch opponent's id, : %s", receiver_id)
        return

    if db.get_active_match(sender_id, receiver_id):
        log.error(
            "Cannot send match request when a match already exists between the two users: %s, %s",
            sender_id,
            receiver_id,
        )
        # Send a message to inform that an ongoing match exists
        return

    if sender_id == receiver_id:
        await self_match_msg(update)
        log.error("User:%s tried to challenge himself", sender_id)
        return

    # Set the required mode if it's part of the argouments
    if len(context.args) >= 2:
        required_mode = str(context.args[1]).lower()
        if required_mode not in ("-w", "-b"):
            log.error("Invalid mode format: %s", required_mode)
            # Send message to inform that mode must be in the right format
            return
        mode = "white" if required_mode == "-w" else "black"
    else:  # Set a randomic mode if it's not explicitly set
        mode = "white" if randint(0, 1) else "black"

    await match_request_msg(
        p1_id=sender_id,
        p2_id=receiver_id,
        mode=mode,
        p1_firstname=p1_firstname,
        update=update,
        context=context,
    )
