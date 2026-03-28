"""This module handle callback query"""

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from src.chess_logic import create_board, get_board
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


async def handle_accept_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle method for commands.play.challenge_user InlineQueryButton,
    where the user accepts the match request"""
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    if not context.match or not update.effective_user:
        return

    p1_id = context.match.group(1)
    p1_name = context.match.group(3)
    mode = int(context.match.group(2))
    p2_id = str(update.effective_user.id)
    p2_name = update.effective_user.full_name

    await query.edit_message_text(text="Loading...")

    result = False
    if mode == 1:
        result = db.start_match(id_white=p1_id, id_black=p2_id)
    elif mode == 2:
        result = db.start_match(id_white=p2_id, id_black=p1_id)
    else:
        log.error("Invalid game mode")

    if not result:
        log.error("Database did not return True result")
        return

    id_match = db.get_active_match(p1_id, p2_id)

    if id_match is None:
        log.error("id_match is None")
        return

    board_fen = db.get_match_chessboard(id_match)

    if board_fen is None:
        log.error("board_fen is None")
        return

    board = create_board(board_fen)
    img1 = get_board(board=board)
    img2 = get_board(board=board)

    await query.delete_message()

    await context.bot.send_photo(
        chat_id=p1_id,
        photo=img1,
        caption=(
            f"<b>Game Vs {p2_name}</b>\n"
            "Your challenge request has been accepted\n\n"
            f"<i>Match number: {id_match}</i>"
        ),
        parse_mode="HTML",
    )

    await context.bot.send_photo(
        chat_id=p2_id,
        photo=img2,
        caption=(
            f"<b>Game Vs {p1_name}</b>\n"
            "You have  accepted the challenge request\n\n"
            f"<i>Match number: {id_match}</i>"
        ),
        parse_mode="HTML",
    )


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
