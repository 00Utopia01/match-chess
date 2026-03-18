"""This module contains the chess logic"""

import io

import cairosvg  # type: ignore
import chess
import chess.svg
from PIL import Image

QUEUE: list[int] = []


def create_board():
    """creates a new game"""
    board = chess.Board()
    return board


def move(board: chess.Board, string: str):
    """Moves a piece along the board"""
    string = string.lower()
    string = string.replace(" ", "")
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


def show_board(board: chess.Board):
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
