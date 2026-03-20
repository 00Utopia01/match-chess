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


async def handle_euela_accept(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """positive response to euela query"""
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    await query.edit_message_text("You succesfully accepted EULA!")


async def handle_euela_decline(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """negative response to euela query"""
    # here goes the logic that removes the user from the database

    query = update.callback_query

    if query is None:
        return

    await query.answer()

    await query.edit_message_text(
        "You refused EULA!\n Unfortunately you cannot utilize this bot",
    )


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

    img = await show_board(update, context, board)
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


async def handle_accept_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle method for commands.play.challenge_user InlineQueryButton,
    where the user accepts the match request"""
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    if not context.match:
        return

    if not update.effective_user:
        return

    p1_id = context.match.group(1)
    p2_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=p1_id,
        text=(f"Your challenge request has been refused by user: {p2_id}!"),
    )


async def handle_refuse_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """handle method for commands.play.challenge_user InlineQueryButton,
    where the user accepts the match request"""
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    if not context.match:
        return

    if not update.effective_user:
        return

    p1_id = context.match.group(1)
    p2_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=p1_id,
        text=(f"Your challenge request has been refused by user: {p2_id}!"),
    )
