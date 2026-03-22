"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import sys

from telegram.error import InvalidToken, NetworkError
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from command.debug.caps import caps
from command.debug.echo import echo
from command.eula import eula
from command.help import command_list as help_command
from command.play import challenge_user, play
from command.start import start
from src.callback import (
    handle_accept_match,
    handle_euela_accept,
    handle_euela_decline,
    handle_refuse_match,
)
from src.env import ENV as env
from src.logger import LOGGER as log

if __name__ == "__main__":

    log.info("Starting...")

    application = ApplicationBuilder().token(env.get_token()).build()

    # Bot Commands >----------------------------------
    commands_list_handler = CommandHandler("help", help_command)
    start_handler = CommandHandler("start", start)
    play_handler = CommandHandler("play", play)
    challenge_handler = CommandHandler("challenge_user", challenge_user)
    eula_handler = CommandHandler("eula", eula)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    accept_eula_handler = CallbackQueryHandler(
        handle_euela_accept, pattern=r"^usr:accept_eula$"
    )
    decline_eula_handler = CallbackQueryHandler(
        handle_euela_decline, pattern=r"^usr:decline_eula$"
    )
    accept_match_handler = CallbackQueryHandler(
        handle_accept_match, pattern=r"^usr:accept_match_(\w+)_([12])_(\w+)$"
    )
    refuse_match_handler = CallbackQueryHandler(
        handle_refuse_match, pattern=r"^usr:refuse_match_(\w+)_([12])_(\w+)$"
    )

    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(play_handler)

    application.add_handler(challenge_handler)
    application.add_handler(commands_list_handler)

    application.add_handler(start_handler)
    application.add_handler(eula_handler)

    # application.add_handler(CallbackQueryHandler(callback_finder))
    application.add_handler(accept_eula_handler)
    application.add_handler(decline_eula_handler)
    application.add_handler(accept_match_handler)
    application.add_handler(refuse_match_handler)

    # Running >--------------------------------
    try:
        application.run_polling()
    except InvalidToken:
        log.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        log.critical("Network error found")
        sys.exit(1)
