"""Debug/utility function to return the user's id"""

from telegram import Update


def get_user_id(update: Update):
    """Returns user id"""
    if update.effective_user:
        return update.effective_user.id

    return None
