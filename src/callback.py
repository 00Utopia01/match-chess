"""This module handle callback query"""

from chess import Board
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from src.chess_logic import create_board, show_board

# from src.db_manager import MatchesDB


def query1(temp: Board):  # TEMP
    """placeholder of a query"""
    if temp:
        return
    return


def query2(temp):  # TEMP
    """placeholder of a query"""
    if temp:
        return 1234
    return 1234


def query3(temp):  # TEMP
    """placeholder of a query"""
    if temp:
        return "TEMP"
    return "TEMP"


# Message >----------------------------


async def euela_accept(query: CallbackQuery):
    """positive response to euela query"""
    await query.edit_message_text("You succesfully accepted EULA!")
    return


async def euela_decline(query: CallbackQuery):
    """negative response to euela query"""
    # here goes the logic that removes the user from the database
    await query.edit_message_text(
        "You refused EULA!\n Unfortunately you cannot utilize this bot",
    )
    return


# Logic >---------------------------


async def match_accept(
    query: CallbackQuery, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """accept the request and send data to db"""

    if update.effective_user is None or query.message is None:
        return

    await query.edit_message_text("loading...")
    board = create_board()
    query1(board)

    img = show_board(board)
    p2_id = query2(update.effective_user.id)
    p2_name = query3(p2_id)
    await context.bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )

    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=img,
        caption=f"La partita contro {p2_name} è cominciata, tu sei il bianco",
    )
    return


async def match_decline(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE):
    """decline the invite and delite data from db"""
    if query.message is None:
        return
    # here goes the logic that removes the user from the database
    await context.bot.delete_message(
        chat_id=query.message.chat.id, message_id=query.message.message_id
    )
    return


async def callback_finder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """decide what callback to use"""

    if context is None:  # for Pylint check
        return

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    match query.data:
        case "euela accepted":
            await euela_accept(query)
        case "euela declined":
            await euela_decline(query)
        case "match accepted":
            await match_accept(query, update, context)
        case "match declined":
            await match_decline(query, context)
