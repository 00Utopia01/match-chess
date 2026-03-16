"""This module contains the chess logic"""
import chess
import chess.svg
import cairosvg
import io

QUEUE: list[int] = []


def create_game(id1: int, id2: int):
    """creates a new game"""
    board = chess.Board()

    if id1 == 1:  # TEMP
        return board
    if id2 == 1:  # TEMP
        return board

    return board


def move(board: chess.Board, string: str):
    """Moves a piece along the board"""
    string = string.lower()
    string = string.replace(" ", "")
    
    try:
        string = chess.Move.from_uci(string)
    except:
        return 1# invalid UCI format or non existent string 
    
    if string in board.legal_moves:
        board.push(move)
    else:
        if board.is_check():
            return 2# Invalid move (player under check)
        else:
            return 3# Generic Invalid move


def show_board(board: chess.Board):
    """Function that converts the board to png"""
    svg_string = chess.svg.board(board,size = 400)
    png_bytes  = cairosvg.svg2png(bytestring=svg_string.encode('utf-8'))

    img = io.BytesIO(png_bytes)
    img.name = "scacchiera.png"

    return img # Returns board's png ready to be sent via BOT


def matchmaking(id: int):
    QUEUE.append(id)

    if len(QUEUE) >= 2:
        create_game(QUEUE[0], QUEUE[1])
        QUEUE.pop(0)
        QUEUE.pop(0)
