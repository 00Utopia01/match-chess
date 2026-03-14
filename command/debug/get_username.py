"""Debug/utility function to return the user's username"""

from telegram import Update


def get_username(update: Update):

    if update.effective_user:
        return update.effective_user.first_name

    return None
