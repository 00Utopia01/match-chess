"""Debug/utility function to return the user's id"""
from telegram import Update

def get_user_id(update: Update):
    if not update.effective_user:
        return
    else:
        return update.effective_user.id