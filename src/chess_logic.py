"""This module contains the chess logic"""

import io

import cairosvg  # type: ignore
import chess
import chess.svg
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes

QUEUE: list[int] = []


def create_board():
    """creates a new game"""
    board = chess.Board()
    return board


def move(board: chess.Board, string: str):
    """Moves a piece along the board"""

    try:
        parsed_move = chess.Move.from_uci(string)
    except chess.InvalidMoveError:
        return 1  # invalid UCI format or non existent string

    if parsed_move in board.legal_moves:
        board.push(parsed_move)
        return 2  # success!

    if board.is_check():
        return 3  # Invalid move (player under check)

    return 4  # Generic Invalid move


def get_board(board: chess.Board):
    """Function that converts the board to WEBP format"""
    svg_string = chess.svg.board(board, size=325)
    png_bytes = cairosvg.svg2png(bytestring=svg_string.encode("utf-8"))

    img = Image.open(io.BytesIO(png_bytes))

    webp_buffer = io.BytesIO()
    img.save(webp_buffer, format="WEBP", quality=80)

    webp_buffer.seek(0)
    webp_buffer.name = "Board.webp"

    return webp_buffer  # Returns board's WEBP ready to be sent via BOT


def matchmaking(user_id: int):
    """Matchmaking function"""
    QUEUE.append(user_id)

    if len(QUEUE) >= 2:
        # create_board(QUEUE[0], QUEUE[1])
        QUEUE.pop(0)
        QUEUE.pop(0)


async def show_board(
    update: Update, context: ContextTypes.DEFAULT_TYPE, img: io.BytesIO
):
    """Function that makes the bot reply with the board WEBP"""
    if not update.message or not update.effective_chat:
        return

    if update.message.reply_to_message:
        await update.message.reply_to_message.delete()

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)


async def board_updater(
    update: Update, context: ContextTypes.DEFAULT_TYPE, board: chess.Board
):
    """Function that handles the chess logic"""

    if not update.message or not update.effective_chat or not update.message.text:
        return

    if not update.message.reply_to_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You must use the /move command as a reply to the board!",
        )
        return

    string = update.message.text.replace("/move", "").strip()
    # This function cleans the string, without it UCI won't effectively parse the string

    match move(board, string):
        case 1:
            move_outcome = "invalid UCI format or non existent string"
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=move_outcome
            )
        case 2:
            move_outcome = get_board(board)
            await show_board(update, context, move_outcome)
        case 3:
            move_outcome = "Invalid move, you are under check!"
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=move_outcome
            )
        case 4:
            move_outcome = "Invalid move!"
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=move_outcome
            )
