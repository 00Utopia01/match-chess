"""Test for main.py (obsolete)"""

from unittest.mock import AsyncMock
import pytest
from pytest_mock import MockerFixture
from main import caps, echo, start


@pytest.mark.asyncio
async def test_start(mocker: MockerFixture):
    """ "Assert if the callback calls the send_message function"""
    # Arrange
    update = mocker.Mock()
    context = mocker.Mock()
    update.effective_chat.id = 12345
    context.bot.send_message = AsyncMock()
    # Act
    await start(update, context)
    # Assert
    context.bot.send_message.assert_called_once_with(
        chat_id=12345, text="I'm a bot, please talk to me!"
    )


@pytest.mark.asyncio
async def test_echo(mocker: MockerFixture):
    """Assert if the callback calls send_message"""
    # Arrange
    update = mocker.Mock()
    context = mocker.Mock()
    update.effective_chat.id = 12345
    update.message.text = "Hello World"
    context.bot.send_message = AsyncMock()
    # Act
    await echo(update, context)
    # Assert
    context.bot.send_message.assert_called_once_with(chat_id=12345, text="Hello World")


@pytest.mark.asyncio
async def test_caps(mocker: MockerFixture):
    """ "Assert if the callback calls send_message with the right output"""
    # Arrange
    update = mocker.Mock()
    context = mocker.Mock()
    update.effective_chat.id = 12345
    context.args = ["hello", "apple", "machine"]
    context.bot.send_message = AsyncMock()
    # Act
    await caps(update, context)
    # Assert
    context.bot.send_message.assert_called_once_with(
        chat_id=12345, text="HELLO APPLE MACHINE"
    )
