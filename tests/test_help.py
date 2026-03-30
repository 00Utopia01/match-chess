"""Test for help.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from command import help as help_cmd


@pytest.mark.asyncio
async def test_command_list_without_chat():
    """Test if the message is sent when we havo no effective_chat"""
    update = MagicMock()
    update.effective_chat = None

    context = AsyncMock()

    await help_cmd.command_list(update, context)

    context.bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_command_list_succes(mocker):
    """Test if the message is sent with correct info"""
    update = MagicMock()
    update.effective_chat.id = 123

    context = AsyncMock()

    await help_cmd.command_list(update, context)

    context.bot.send_message.assert_called_once_with(
        chat_id=123, text=mocker.ANY, parse_mode=mocker.ANY
    )
