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
    PicklePersistence,
    filters,
)

from command.debug.caps import caps
from command.debug.echo import echo
from command.eula import (
    del_message_and_optout_callback,
    del_message_and_register_callback,
    eula,
)
from command.help import command_list as help_command
from command.move import move
from command.play import challenge_user, play
from command.register import register
from command.start import (
    start,
    start_eula_callback,
    start_optout_callback,
    start_register_callback,
)
from src.callback import (
    handle_accept_match,
    handle_refuse_match,
)
from src.env import ENV as env
from src.logger import LOGGER as log

if __name__ == "__main__":

    log.info("Starting...")

    persistence = PicklePersistence(filepath="application_persistance")
    app = application = (
        ApplicationBuilder().token(env.get_token()).persistence(persistence).build()
    )

    # Bot Commands >----------------------------------
    commands_list_handler = CommandHandler("help", help_command)
    start_handler = CommandHandler("start", start)
    play_handler = CommandHandler("play", play)
    challenge_handler = CommandHandler("challenge_user", challenge_user)
    eula_handler = CommandHandler("eula", eula)
    register_handler = CommandHandler("register", register)
    match_handler = CommandHandler("move", move)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    accept_match_handler = CallbackQueryHandler(
        handle_accept_match, pattern=r"^usr:accept_match_(\w+)_([12])_(\w+(\s*.*)*)$"
    )
    refuse_match_handler = CallbackQueryHandler(
        handle_refuse_match, pattern=r"^usr:refuse_match_(\w+)_([12])_(\w+(\s*.*)*)$"
    )
    start_optout_query_handler = CallbackQueryHandler(
        start_optout_callback, pattern=r"^usr:start_optout$"
    )
    start_eula_query_handler = CallbackQueryHandler(
        start_eula_callback, pattern=r"^usr:start_eula$"
    )
    start_register_query_handler = CallbackQueryHandler(
        start_register_callback, pattern=r"^usr:start_register$"
    )
    del_and_start_optout_query_handler = CallbackQueryHandler(
        del_message_and_optout_callback, pattern=r"^usr:del_and_start_optout$"
    )
    del_and_start_register_query_handler = CallbackQueryHandler(
        del_message_and_register_callback, pattern=r"^usr:del_and_start_register$"
    )

    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(play_handler)
    application.add_handler(match_handler)

    application.add_handler(challenge_handler)
    application.add_handler(commands_list_handler)

    application.add_handler(start_handler)
    application.add_handler(eula_handler)
    application.add_handler(register_handler)

    application.add_handler(accept_match_handler)
    application.add_handler(refuse_match_handler)

    application.add_handler(start_optout_query_handler)
    application.add_handler(start_eula_query_handler)
    application.add_handler(start_register_query_handler)

    application.add_handler(del_and_start_optout_query_handler)
    application.add_handler(del_and_start_register_query_handler)

    # Running >--------------------------------
    try:
        application.run_polling()
    except InvalidToken:
        log.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        log.critical("Network error found")
        sys.exit(1)
