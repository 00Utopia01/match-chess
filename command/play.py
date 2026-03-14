from telegram import Update
from telegram.error import BadRequest, TelegramError  # ,InvalidToken, NetworkError
from telegram.ext import \
    ContextTypes  # ApplicationBuilder,; CommandHandler,; MessageHandler,; filters,


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends an invite to an user with the corresponding ID"""
    if not update.message or not update.effective_user:
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Non-existent or invalid ID code given")
        return

    sender_id = update.effective_user.id
    sender_username = update.effective_user.first_name

    if sender_id == int(context.args[0]):
        await update.message.reply_text("You can't challenge yourself!")
        return

    challengeduser_id = int(context.args[0])

    # Here should go the logic that connects the 2 users via database

    try:
        await update.message.reply_text("Challenge Sent")
        await context.bot.send_message(
            chat_id=challengeduser_id,
            text=f"{sender_username} (ID = {sender_id}) has sent you an invite!",
        )
    except BadRequest:
        await update.message.reply_text(
            "Error delivering the challenge. ID code may be invalid or non-existent."
        )
    except TelegramError:
        await update.message.reply_text(
            "An unexpected error occurred while sending the challenge."
        )
