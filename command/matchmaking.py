"""Add /matchmaking command, which allows any user to look for other users to play with"""

from random import randint
from typing import cast

import chess
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes, PicklePersistence

from command.move import get_chessboard_webp
from src.db_manager import DB as db
from src.env import ENV as env
from src.logger import LOGGER as log


async def matchmaking(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    matchmaking_queue: MatchMakingQueue,
):
    """Implement /matchmaking command: add user to queue and send messages"""
    if not update.effective_user:
        return

    user_id = str(update.effective_user.id)

    outcome: bool = await matchmaking_queue.add_user(user_id)
    if not outcome:
        await context.bot.send_message(
            chat_id=update.effective_user.id, text="You are already in queue."
        )
        return

    await _waiting_player_msg(update, context)


async def _waiting_player_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the message to inform the user that he is looking for a match.
    This message contains a button to cancel the matchmaking process"""
    if not update.effective_user:
        return

    user_id = str(update.effective_user.id)

    cancel_matchmaking_button = InlineKeyboardButton(
        "Cancel matchmaking", callback_data="usr:cancel_matchmaking"
    )

    options_layout = [[cancel_matchmaking_button]]

    markup = InlineKeyboardMarkup(options_layout)

    msg = await context.bot.send_message(
        chat_id=user_id,
        text="Waiting for other players...",
        reply_markup=markup,
    )

    return msg.id


async def cancel_matchmaking(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    matchmaking_queue: MatchMakingQueue,
):
    """Callback function to cancel matchmaking process when the user pesses 'cancel matchmaking'"""
    if update.effective_user is None:
        log.error("No effective_user in cancel_matchmaking()")
        return

    query = update.callback_query

    if query is None or query.message is None:
        log.error("No query or query.message in cancel_matchmaking()")
        return

    await query.answer()

    user_id = str(update.effective_user.id)

    remove_outcome = matchmaking_queue.remove_user(user_id)
    if not remove_outcome:
        await context.bot.send_message(
            chat_id=user_id, text="You are not currently in queue."
        )

    await context.bot.delete_message(
        chat_id=user_id, message_id=int(query.message.message_id)
    )


class MatchMakingQueue:
    """This class represents the matchmaking queue"""

    def __init__(self, persistence: PicklePersistence):
        self.user_queue: list[str] = []
        self.persistence: PicklePersistence = persistence
        self.bot = telegram.Bot(token=env.get_token())

    async def add_user(self, user_id: str) -> bool:
        """
        Adds a player to the queue.
        Returns False if the user is already in the queue,
        True otherwise
        """
        # Check if user is already in queue
        if user_id in self.user_queue:
            log.error("This user is already in queue: %s", user_id)
            return False

        # Make a match if possible
        if self.user_queue:
            await self.match_users(user_id, str(self.user_queue.pop(0)))
            return True

        # Append the user to the queue
        self.user_queue.append(user_id)
        return True

    async def match_users(self, p1_id: str, p2_id: str):
        """Creates a match between two users waiting in queue"""

        if not p1_id or not p2_id:
            log.error("The given id's are None")
            return

        # Choose random sides for both players
        white_id: str = p1_id if randint(0, 1) else p2_id
        black_id: str = p2_id if p1_id == white_id else p1_id

        # Start a match on the db, and get it's id
        db.start_match(white_id, black_id)
        match_id = db.get_active_match(white_id, black_id)

        if not match_id:
            log.error("match_id cannot be None")
            return

        msg_white, msg_black = await self._send_chessboard_msgs(
            white_id, black_id, match_id
        )

        await self._save_chat_data(msg_white, msg_black, white_id, black_id, match_id)

    async def _send_chessboard_msgs(self, white_id, black_id, match_id):
        """Send chessboard messages to both users when a match is found"""

        # Fetch user_data from the db in order to obtain user fullname
        white_user_data = db.get_user_data(str(white_id))
        black_user_data = db.get_user_data(str(black_id))

        if not isinstance(white_user_data, dict) or not isinstance(
            black_user_data, dict
        ):
            log.error(
                "Invalid white_user_data or black_user_data: %s, %s",
                str(white_id),
                str(black_id),
            )
            return

        chessboard = chess.Board()
        img = get_chessboard_webp(chessboard)

        msg_white = await self.bot.send_photo(
            chat_id=white_id,
            photo=img,
            caption=(
                f"<b>Game Vs {black_user_data["fullname"]}</b>\n"
                "You found an opponent!\n\n"
                f"<i>Match number: {match_id}</i>"
            ),
            parse_mode="HTML",
        )
        img.seek(0)
        msg_black = await self.bot.send_photo(
            chat_id=black_id,
            photo=img,
            caption=(
                f"<b>Game Vs {white_user_data["fullname"]}</b>\n"
                "You found an opponent!\n\n"
                f"<i>Match number: {match_id}</i>"
            ),
            parse_mode="HTML",
        )

        return msg_white, msg_black

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments

    async def _save_chat_data(
        self,
        msg_white: Message,
        msg_black: Message,
        white_id: str,
        black_id: str,
        match_id: str,
    ):
        """Saves chat id's into chat_data"""
        app_chat_data = cast(dict, self.persistence.chat_data)
        if int(white_id) not in app_chat_data:
            app_chat_data[int(white_id)] = {}
        if int(black_id) not in app_chat_data:
            app_chat_data[int(black_id)] = {}

        app_chat_data[int(white_id)][f"msg_{match_id}"] = msg_white.message_id
        app_chat_data[int(black_id)][f"msg_{match_id}"] = msg_black.message_id

        await self.persistence.flush()

    def remove_user(self, user_id: str) -> bool:
        """Removes a player from the queue. Returns True if removed."""
        if user_id not in self.user_queue:
            log.error("Cannot remove user: %s. User is not in queue", user_id)
            return False
        try:
            self.user_queue.remove(user_id)
        except ValueError:
            log.error("Attempted to remove user from the queue: %s", user_id)
            return False

        return True
