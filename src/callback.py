"""This module handles callback query"""

from typing import cast

from chess import Board
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

# from src.chess_logic import get_board
from command.move import get_chessboard_webp
from src.db_manager import DB as db
from src.logger import LOGGER as log

# Logic >---------------------------


async def match_decline(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """decline the invite and delite data from db"""
    if query.message is None:
        return
    # here goes the logic that removes the user from the database
    await context.bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    return


def _start_match(mode: int, p1_id: str, p2_id: str) -> str | None:
    """Start a match between two users with choosing their sides with the parameter mode:
    mode = 1: p1 starts as white
    mode = 2: p2 starts as white"""
    result = False
    if mode == 1:
        result = db.start_match(id_white=p1_id, id_black=p2_id)
    elif mode == 2:
        result = db.start_match(id_white=p2_id, id_black=p1_id)
    else:
        log.error("Invalid game mode")

    if not result:
        log.error("Database did not return True result")
        return None

    return db.get_active_match(p1_id, p2_id)


async def handle_accept_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle method for commands.play.challenge_user InlineQueryButton,
    where the user accepts the match request"""
    if not update.message or not update.effective_user:
        return

    if not context.match:
        log.error("Context doesn't have callback_data")
        return

    query = update.callback_query

    if query is None:
        log.error("No query")
        return

    await query.answer()

    # p2 = user that sends the request, p1 = user that accepts
    p1_id = context.match.group(1)
    p1_name = context.match.group(3)
    mode = int(context.match.group(2))
    p2_id = str(update.effective_user.id)
    p2_name = update.effective_user.full_name

    await query.edit_message_text(text="Loading...")

    match_id = _start_match(mode, p1_id, p2_id)

    if match_id is None:
        log.error("match_id is None")
        return

    chessboard_fen = db.get_match_chessboard(match_id)

    if chessboard_fen is None:
        log.error("chessboard_fen is None")
        return

    board = Board(chessboard_fen)
    img1 = get_chessboard_webp(chessboard=board)

    await query.delete_message()

    msg_p1 = await context.bot.send_photo(
        chat_id=p1_id,
        photo=img1,
        caption=(
            f"<b>Game Vs {p2_name}</b>\n"
            "Your challenge request has been accepted\n\n"
            f"<i>Match number: {match_id}</i>"
        ),
        parse_mode="HTML",
    )

    img1.seek(0)
    msg_p2 = await context.bot.send_photo(
        chat_id=p2_id,
        photo=img1,
        caption=(
            f"<b>Game Vs {p1_name}</b>\n"
            "You have  accepted the challenge request\n\n"
            f"<i>Match number: {match_id}</i>"
        ),
        parse_mode="HTML",
    )
    # Save p1 and p2's message id in chat data
    app_chat_data = cast(dict, context.application.chat_data)
    if int(p1_id) not in app_chat_data:
        app_chat_data[int(p1_id)] = {}
    if int(p2_id) not in app_chat_data:
        app_chat_data[int(p2_id)] = {}

    app_chat_data[int(p1_id)][f"msg_{match_id}"] = msg_p1.message_id
    app_chat_data[int(p2_id)][f"msg_{match_id}"] = msg_p2.message_id


async def handle_refuse_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle method for commands.play.challenge_user InlineQueryButton,
    where the user accepts the match request"""
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    if not context.match or not update.effective_user:
        return

    await query.edit_message_text(text="Match denied")

    p1_id = context.match.group(1)
    p1_name = context.match.group(3)

    await context.bot.send_message(
        chat_id=p1_id,
        text=(f"Your challenge request has been refused by {p1_name}!"),
    )
