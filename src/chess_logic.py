"""This module contains the chess logic"""

from telegram import Update
from telegram.ext import ContextTypes
import chess

QUEUE: list[int] = []


def create_game(id1: int, id2: int):
    board = chess.Board()

    if id1 == 1:  # TEMP
        return board
    if id2 == 1:  # TEMP
        return board

    return board


async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.effective_user:
        return

    if context.args:
        user_move = context.args[0]
        user_move = user_move.lower()
        user_move = user_move.replace(" ", "")
        try:
            user_move = chess.Move.from_uci(user_move)
            await update.message.reply_text("[DEBUG] : INSERTED CORRECT FORMAT")
        except:
            await update.message.reply_text("Inserted move is not in UCI format!")
            return
    else:
        await update.message.reply_text("The inserted move is invalid or non existent!")
        return
    
    # board = context.chat_data.get('board') 
    # line 39 needs to be complemented with the line"board = context.chat_data['board']"


    # if user_move in board.legal_moves:
        # board.push(user_move)
    # else:
        # if board.is_check():
            # print("You can't do this move when you are under check")
        # else:
            # print("Invalid or non-existent move!")


def matchmaking(id: int):
    QUEUE.append(id)

    if len(QUEUE) >= 2:
        create_game(QUEUE[0], QUEUE[1])
        QUEUE.pop(0)
        QUEUE.pop(0)
