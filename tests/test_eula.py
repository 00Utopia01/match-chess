"""Test for eula.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from telegram import InlineKeyboardMarkup

from command import eula


def test_create_button():
    """Test to create a button"""
    result = eula.create_button()
    assert isinstance(result, InlineKeyboardMarkup) is True


@pytest.mark.asyncio
async def test_eula_without_chat():
    """Test if the message is sent when we havo no effective_chat"""
    update = MagicMock()
    update.effective_chat = None

    context = AsyncMock()

    await eula.eula(update, context)

    context.bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_eula_succes(mocker: MockerFixture):
    """Test if the message is sent with correct info"""
    update = MagicMock()
    update.effective_chat.id = 123

    context = AsyncMock()

    markup = MagicMock()
    mocker.patch("command.eula.create_button", return_value=markup)

    await eula.eula(update, context)

    context.bot.send_message.assert_called_once_with(
        chat_id=123, text=mocker.ANY, parse_mode=mocker.ANY, reply_markup=markup
    )
