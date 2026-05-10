"""This module handles callback query"""

from typing import cast

import chess
from chess import Board
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

# from src.chess_logic import get_board
from command.move import get_chessboard_keyboard, get_move_outcome, MoveOutcome, process_move, process_game_over
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
    if not update.effective_user:
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
    keyboard = get_chessboard_keyboard(match_id, board)

    await query.delete_message()

    msg_p1 = await context.bot.send_message(
        chat_id=p1_id,
        text=(
            f"<b>Game Vs {p2_name}</b>\n"
            "Your challenge request has been accepted\n\n"
            f"<i>Match number: {match_id}</i>"
        ),
        parse_mode="HTML",
        reply_markup=keyboard,
    )

    msg_p2 = await context.bot.send_message(
        chat_id=p2_id,
        text=(
            f"<b>Game Vs {p1_name}</b>\n"
            "You have accepted the challenge request\n\n"
            f"<i>Match number: {match_id}</i>"
        ),
        parse_mode="HTML",
        reply_markup=keyboard,
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


async def handle_square_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle square selection for making moves via buttons."""
    if not update.effective_user or not context.match:
        return

    query = update.callback_query
    if not query or not query.message:
        return

    await query.answer()

    match_id = context.match.group(1)
    square = context.match.group(2)
    user_id = str(update.effective_user.id)

    match_data = db.get_match_data(match_id)
    if not match_data or match_data["time_stop"]:
        await query.answer("Match not found or ended")
        return

    from command.move import get_active_player_id
    if get_active_player_id(match_data) != update.effective_user.id:
        await query.answer("Not your turn")
        return

    app_chat_data = cast(dict, context.application.chat_data)
    user_data = app_chat_data.get(int(user_id), {})

    selected = user_data.get("selected_square")

    if selected:
        # Attempt move
        from_square = selected
        to_square = square
        board = Board(match_data["chessboard_fen"])
        move = chess.Move(chess.parse_square(from_square), chess.parse_square(to_square))
        # Auto-promote to queen if pawn reaches last rank
        if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.PAWN:
            if (board.turn == chess.WHITE and move.to_square // 8 == 7) or (board.turn == chess.BLACK and move.to_square // 8 == 0):
                move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)
        move_uci = move.uci()

        outcome = get_move_outcome(board, move_uci)
        if outcome == MoveOutcome.SUCCESS:
            # Clear selected
            user_data.pop("selected_square", None)
            await process_move(move_uci, match_data, user_id, query.message.message_id, context)
        elif outcome in (MoveOutcome.CHECKMATE, MoveOutcome.STALEMATE):
            # Handle game over
            user_data.pop("selected_square", None)
            await process_game_over(move_uci, match_data, user_id, query.message.message_id, context)
        else:
            user_data.pop("selected_square", None)
            await query.answer("Invalid move")
    else:
        # Select square if has piece
        board = Board(match_data["chessboard_fen"])
        piece = board.piece_at(chess.parse_square(square))
        if piece and piece.color == board.turn:
            user_data["selected_square"] = square
            await query.answer(f"Selected {square}")
        else:
            await query.answer("No piece to select")
