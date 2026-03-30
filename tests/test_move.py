"""Test methods regarding /move command"""

import chess
import pytest

from command import move
from command.move import MoveOutcome

test_moves = [
    {
        "chessboard_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move": "e2e4",
        "expected_outcome": MoveOutcome.SUCCESS,
    },
    {
        "chessboard_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move": "1234",
        "expected_outcome": MoveOutcome.INVALID_FORMAT,
    },
    {
        "chessboard_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move": "",
        "expected_outcome": MoveOutcome.INVALID_FORMAT,
    },
    {
        "chessboard_fen": "rnbqk1nr/pppp1ppp/4p3/8/1b2P3/3P4/PPP2PPP/RNBQKBNR w KQkq - 1 3",
        "move": "a2a3",
        "expected_outcome": MoveOutcome.ILLEGAL_CHECK,
    },
    {
        "chessboard_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move": "a2a6",
        "expected_outcome": MoveOutcome.ILLEGAL_GENERIC,
    },
    {
        "chessboard_fen": "rnbqkbnr/pppp1ppp/8/4p3/5PP1/8/PPPPP2P/RNBQKBNR b KQkq - 0 2",
        "move": "d8h4",
        "expected_outcome": MoveOutcome.CHECKMATE,
    },
    {
        "chessboard_fen": "7k/8/8/6Q1/8/8/8/K7 w - - 0 1",
        "move": "g5g6",
        "expected_outcome": MoveOutcome.STALEMATE,
    },
]


@pytest.mark.parametrize("test_move", test_moves)
def test_get_move_outcome(test_move):
    """Test different moves in differend scenarios (chessboard dispositions),
    and assert the return value of get_move_outcome()"""
    chessboard = chess.Board(fen=test_move["chessboard_fen"])
    assert (
        move.get_move_outcome(chessboard, test_move["move"])
        == test_move["expected_outcome"]
    )
