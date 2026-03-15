import chess

QUEUE: list[int] = []


def create_game(id1: int, id2: int) -> chess.Board:
    if id1 == 1:  # TEMP
        return chess.Board()
    if id2 == 1:  # TEMP
        return chess.Board()

    return chess.Board()


def move(move: str | None = None):
    if move is None:
        return


def matchmaking(id: int):
    QUEUE.append(id)

    if len(QUEUE) >= 2:
        create_game(QUEUE[0], QUEUE[1])
        QUEUE.pop(0)
        QUEUE.pop(0)
