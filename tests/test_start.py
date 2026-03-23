"""Tests for start.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from command import start

start_input = ([None, None], [True, None], [None, True])


@pytest.mark.asyncio
@pytest.mark.parametrize("chat, user", start_input)
async def test_eula_without_chat_and_user(chat, user):
    """Test when effective_user and effective_chat are None"""
    update = MagicMock()
    update.effective_chat = chat
    update.effective_user = user

    context = MagicMock()

    await start.start(update=update, context=context)

    context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_eula_without_username():
    """Thest when username is None"""
    update = MagicMock()
    update.effective_user.username = None

    context = MagicMock()

    await start.start(update=update, context=context)

    context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_eula_with_no_user_in_db(mocker: MockerFixture):
    """Test when no user found in db"""
    update = MagicMock()
    update.effective_user.username = "username"
    update.effective_user.id = 123

    context = AsyncMock()

    mocker.patch("command.start.db.insert_user", return_value=False)

    await start.start(update=update, context=context)

    context.bot.send_message.assert_called_once_with(chat_id="123", text=mocker.ANY)


@pytest.mark.asyncio
async def test_eula_with_user_in_db(mocker: MockerFixture):
    """Test if user is in db"""
    update = MagicMock()
    update.effective_user.username = "username"
    update.effective_user.id = 123

    context = AsyncMock()

    mocker.patch("command.start.db.insert_user", return_value=True)

    await start.start(update=update, context=context)

    context.bot.send_message.assert_called_once_with(
        chat_id="123", text=mocker.ANY, parse_mode="HTML"
    )
