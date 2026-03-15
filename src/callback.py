"""This module handle callback query"""

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes


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


# async def match_accept(query: CallbackQuery):
#     print("WIP")
#     return


# async def match_decline(query: CallbackQuery):
#     print("WIP")
#     return


async def callback_finder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """check what callplay to use"""

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
        # case "match accepted":
        #     await match_accept(query)
        # case "match declined":
        #     await match_decline(query)
