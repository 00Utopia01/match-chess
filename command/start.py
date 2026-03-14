from telegram import Update
from telegram.ext import \
    ContextTypes  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,

# from telegram.error import BadRequest, InvalidToken, NetworkError, TelegramError


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """function to be activated whenever the "/start" command is sent"""
    if not update.effective_chat or not update.effective_user:
        return

    username = update.effective_user.first_name
    userid = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Welcome {username} to the Chess bot!\n"
            f"Your ID is {userid}, share it with your friends to play togheter"
        ),
    )
