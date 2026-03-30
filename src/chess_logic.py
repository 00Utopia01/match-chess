"""This module contains the chess logic"""

QUEUE: list[int] = []


def matchmaking(user_id: int):
    """Matchmaking function"""
    QUEUE.append(user_id)

    if len(QUEUE) >= 2:
        # create_board(QUEUE[0], QUEUE[1])
        QUEUE.pop(0)
        QUEUE.pop(0)
