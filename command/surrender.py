"""Handle /surrender command that end by surrend an existing game"""

# pylint: disable=duplicate-code

from telegram import Update
from telegram.ext import ContextTypes

from command.move import caption_get_match_id
from src.db_manager import DB as db
from src.logger import LOGGER as log

# Command >--------------------------------------------------


async def surrender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """End the game with a surrend option"""
    if not update.message or not update.effective_chat or not update.effective_user:
        return

    if not update.message.reply_to_message:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You must use the /surrender command as a reply to the board!",
        )
        return

    caption = update.message.reply_to_message.caption
    if not caption or not isinstance(caption, str):
        log.warning("Message caption is not valid")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Unable to find the match ID",
        )
        return

    match_id = caption_get_match_id(caption=caption)
    game_data = db.get_match_data(match_id=match_id)

    if game_data is None:
        log.warning("Invalid Mathc_ID")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No able to found a match with that id",
        )
        return

    db.stop_match(match_id)

    if game_data["white_user1"] != update.effective_user.id:
        p2_id = game_data["white_user1"]
        is_p1_black = True
    else:
        p2_id = game_data["black_user2"]
        is_p1_black = False

    winner = "White" if is_p1_black else "Black"
    text = f"{winner} player has won the match by surrender!"

    await context.bot.send_message(chat_id=p2_id, text=text)

    await context.bot.send_message(chat_id=update.effective_user.id, text=text)
