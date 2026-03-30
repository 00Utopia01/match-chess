"""Handle /move command, to enable users to make a move by replying to a chessboard message"""

import io
import re
from enum import Enum

import cairosvg  # type: ignore
import chess
import chess.svg
from PIL import Image
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from src.db_manager import DB as db
from src.logger import LOGGER as log


# pylint: disable=too-many-return-statements
async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle move command, update chessboard on the db, send messages to the two users"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return

    # The /move command can be done only by replying to the chessboard bot's message
    if not update.message.reply_to_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You must use the /move command as a reply to the board!",
        )
        return

    if not context.args:
        # Send message "must input a move"
        log.error("Cannot execute /move without move_uci")
        return

    caption = update.message.reply_to_message.caption
    if not caption or not isinstance(caption, str):
        log.error("Message caption is not valid")
        return

    match_id = caption_get_match_id(caption)

    match_data = db.get_match_data(match_id)
    if not match_data:
        log.error("Query error on get_match_data")
        return

    # Check if the match in wich we are trying to make a move is still ongoing
    if match_data["time_stop"]:
        # Send message to the user to inform that the match has ended
        log.error("Tryed to move on a finished match: %s", match_id)
        return

    # Check if it's the user's turn to make a move
    if get_active_player_id(match_data) != update.effective_user.id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You have to wait your turn to use /move!",
        )
        return

    move_uci = context.args[0]

    await move_send_messages(move_uci, match_data, update, context)


# pylint: enable=too-many-return-statements


async def move_send_messages(
    move_uci: str,
    match_data: dict,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Orchestrates the outcome of a move and sends messages to both players"""
    if (
        not update.message
        or not update.effective_user
        or not update.message.reply_to_message
    ):
        return

    white_id, black_id = match_data["white_user1"], match_data["black_user2"]
    chessboard = chess.Board(fen=match_data["chessboard_fen"])

    move_outcome = get_move_outcome(chessboard, move_uci)
    sender_id = update.effective_user.id
    receiver_id = black_id if sender_id == white_id else white_id

    match move_outcome:
        case MoveOutcome.STALEMATE | MoveOutcome.CHECKMATE:
            await _handle_game_over(move_outcome, match_data, chessboard, context)

        case MoveOutcome.SUCCESS:
            await _handle_successful_move(
                move_uci, match_data, receiver_id, update=update, context=context
            )

        case (
            MoveOutcome.INVALID_FORMAT
            | MoveOutcome.ILLEGAL_CHECK
            | MoveOutcome.ILLEGAL_GENERIC
        ):
            await context.bot.send_message(
                chat_id=sender_id, text="Please input a valid move in uci format"
            )


async def _handle_successful_move(
    move_uci,
    match_data,
    receiver_id,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Save the move in the db, deletes old chessboard messages, and sends new ones"""
    if (
        not update.message
        or not update.effective_user
        or not update.message.reply_to_message
    ):
        return

    # Update database's chessboard with the new move
    sender_id = update.effective_user.id
    chessboard = chess.Board(fen=match_data["chessboard_fen"])
    match_id = match_data["ID_Match"]
    chessboard.push(chess.Move.from_uci(move_uci))
    db.add_move(match_id, move_uci)

    img = get_chessboard_webp(chessboard)

    # Get user's fullname from the db
    sender_user_data = db.get_user_data(str(sender_id))
    receiver_user_data = db.get_user_data(str(receiver_id))

    if not isinstance(sender_user_data, dict) or not isinstance(
        receiver_user_data, dict
    ):
        log.error(
            "Invalid sender_user_data or receiver_user_data: %s, %s",
            str(sender_id),
            str(receiver_id),
        )
        return

    # Delete old chessboard messages
    await _delete_old_messages(
        match_id, str(sender_id), str(receiver_id), update, context
    )

    # Send messages
    sender_msg = await context.bot.send_photo(
        chat_id=sender_id,
        photo=img,
        caption=f"<b>Game Vs {receiver_user_data["fullname"]}</b>\n"
        f"Your move: {move_uci}\n\n"
        f"<i>Match number: {match_id}</i>",
        parse_mode="HTML",
    )
    img.seek(0)
    receiver_msg = await context.bot.send_photo(
        chat_id=receiver_id,
        photo=img,
        caption=f"<b>Game Vs {sender_user_data["fullname"]}</b>\n"
        f"Opponent's move: {move_uci}\n\n"
        f"<i>Match number: {match_id}</i>",
        parse_mode="HTML",
    )

    # Update chat_data on both chats
    _update_chat_data(context, match_id, sender_id, sender_msg.message_id)
    _update_chat_data(context, match_id, receiver_id, receiver_msg.message_id)


async def _delete_old_messages(
    match_id: str,
    sender_id: str,
    receiver_id: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Attempts to delete previous board messages"""
    if (
        not update.message
        or not update.effective_chat
        or not update.effective_user
        or not update.message.reply_to_message
    ):
        return

    app_chat_data = context.application.chat_data

    # Delete sender's last message (the one they replied to)
    try:
        await context.bot.delete_message(
            chat_id=sender_id, message_id=update.message.reply_to_message.message_id
        )
    except BadRequest:
        log.error("Failed to delete sender's last message (the one they replied to)")
        return

    # Delete receiver's last message from persistence.chat_data
    receiver_msg_id = app_chat_data.get(int(receiver_id), {}).get(f"msg_{match_id}")
    if receiver_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=receiver_id, message_id=receiver_msg_id
            )
        except BadRequest:
            log.error(
                "Failed to delete receiver's last message from persistence.chat_data"
            )
            return


async def _handle_game_over(
    outcome: MoveOutcome,
    match_data: dict,
    chessboard: chess.Board,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Ends the database match and notifies players"""

    match_id = match_data["ID_Match"]
    white_id, black_id = match_data["white_user1"], match_data["black_user2"]

    db.stop_match(match_id)

    img = get_chessboard_webp(chessboard)

    white_user_data = db.get_user_data(str(white_id))
    black_user_data = db.get_user_data(str(black_id))

    if not white_user_data or not black_user_data:
        log.error("Failed to fetch user_data")
        return

    if outcome == MoveOutcome.STALEMATE:
        text = MoveOutcome.STALEMATE.value
    else:
        winner = "Black" if chessboard.turn == chess.WHITE else "White"
        text = f"{winner} player has won the match by checkmate!"

    # Send messages
    await context.bot.send_photo(
        chat_id=white_id,
        photo=img,
        caption=f"<b>Game Vs {black_user_data["fullname"]}</b>\n"
        f"{text}\n\n"
        f"<i>Match number: {match_id}</i>",
        parse_mode="HTML",
    )
    img.seek(0)
    await context.bot.send_photo(
        chat_id=black_id,
        photo=img,
        caption=f"<b>Game Vs {white_user_data["fullname"]}</b>\n"
        f"{text}\n\n"
        f"<i>Match number: {match_id}</i>",
        parse_mode="HTML",
    )


def _update_chat_data(context, match_id, user_id, message_id):
    """Update chat_data of the specified user, add {"msg_match_id" : message_id}"""
    if int(user_id) not in context.application.chat_data:
        context.application.chat_data[int(user_id)] = {}
    context.application.chat_data[int(user_id)][f"msg_{match_id}"] = message_id


def get_active_player_id(match_data: dict) -> str:
    """Get the user_id of the active user in the specified match"""
    chessboard_fen = match_data["chessboard_fen"]
    active_player_id = (
        match_data["white_user1"]
        if is_white_turn(chessboard_fen)
        else match_data["black_user2"]
    )
    return active_player_id


def is_white_turn(chessboard_fen: str) -> bool:
    """Return true if it's white to move on the specified chessboard"""
    crop = chessboard_fen.split(" ")

    if len(crop) > 1:
        return crop[1] == "w"

    return False


class MoveOutcome(Enum):
    """Move outcomes dictionary"""

    INVALID_FORMAT = "Invalid UCI format"
    SUCCESS = "Valid move executed"
    ILLEGAL_CHECK = "Illegal move(check status)"
    ILLEGAL_GENERIC = "Generic Illegal move"
    CHECKMATE = "The player of this turn has won the match!"
    STALEMATE = "The game has ended on stalemate!"


def get_chessboard_webp(chessboard: chess.Board):
    """Function that converts the board to WEBP format"""
    svg_string = chess.svg.board(chessboard, size=325)
    png_bytes = cairosvg.svg2png(bytestring=svg_string.encode("utf-8"))

    img = Image.open(io.BytesIO(png_bytes))

    webp_buffer = io.BytesIO()
    img.save(webp_buffer, format="WEBP", quality=80)

    webp_buffer.seek(0)
    webp_buffer.name = "Board.webp"

    return webp_buffer  # Returns board's WEBP ready to be sent via BOT


async def check_player_turn(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    white_player: int,
    black_player: int,
    board_fen: str,
) -> bool:
    """This function verifies if the user has the current turn priority"""

    if not update.effective_user or not update.effective_chat:
        return False

    current_player = white_player if is_white_turn(board_fen) else black_player

    if update.effective_user.id != current_player:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You have to wait your turn to use /move !",
        )
        return False

    return True


def caption_get_match_id(caption: str) -> str:
    """Look for the match_id inside the chessboard message caption, and return match_id.
    The match_id must be a number at the ending of the caption"""
    cropped_caption = re.search(r"\d+$", caption)

    if not cropped_caption:
        log.error("Error on cropped caption")
        return ""

    match_id = cropped_caption.group()
    return match_id


def get_move_outcome(chessboard: chess.Board, move_uci: str):
    """Check if the move is valid on the specified chessboard
    and return it's outcome:
    (SUCCESS, INVALID_FORMAT, ILLEGAL_CHECK, ILLEGAL_GENERIC, CHECKMATE, STALEMATE)
    """
    chessboard_cpy: chess.Board = chessboard

    try:
        parsed_move = chess.Move.from_uci(move_uci)

    except chess.InvalidMoveError:
        return MoveOutcome.INVALID_FORMAT  # invalid UCI format or non existent move_uci

    if parsed_move not in chessboard_cpy.legal_moves:
        if chessboard_cpy.is_pseudo_legal(parsed_move):
            return MoveOutcome.ILLEGAL_CHECK  # Invalid move (player under check)
        return MoveOutcome.ILLEGAL_GENERIC  # Generic Invalid move

    chessboard_cpy.push(parsed_move)

    if chessboard_cpy.is_checkmate():
        return MoveOutcome.CHECKMATE
    if chessboard_cpy.is_stalemate():
        return MoveOutcome.STALEMATE

    return MoveOutcome.SUCCESS
