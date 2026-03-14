"""
This module handles the main Telegram bot logic for Match-Chess.
"""

import sys

from telegram.error import InvalidToken, NetworkError
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from command.debug.caps import caps
from command.debug.echo import echo
from command.eula import eula
from command.help import command_list as help_command
from command.play import play
from command.start import start
from src import env
from src.logger import LOGGER as log

if __name__ == "__main__":

    log.info("------------------- Fresh Start -------------------")

    # Token setup >--------------------------------

    log.info("Loading Token...")

    TOKEN = env.get_token()
    if TOKEN is None or not env.check_token(TOKEN):
        sys.exit(1)
    else:
        log.info("Setting telegram bot token...")

    # Bot Application setup >--------------------------------

    log.info("Starting...")

    application = ApplicationBuilder().token(TOKEN).build()

    # Bot Commands >----------------------------------
    commands_list_handler = CommandHandler("commands", help_command)
    start_handler = CommandHandler("start", start)
    challenge_handler = CommandHandler("challenge", play)
    eula_handler = CommandHandler("eula", eula)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler("caps", caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(challenge_handler)
    application.add_handler(commands_list_handler)
    application.add_handler(eula_handler)

    # Running >--------------------------------
    try:
        application.run_polling()
    except InvalidToken:
        log.critical("The token was rejected by the server")
        sys.exit(1)
    except NetworkError:
        log.critical("Network error found")
        sys.exit(1)
