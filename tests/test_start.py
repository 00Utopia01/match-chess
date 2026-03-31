"""Tests for start.py"""

# pylint: disable=duplicate-code

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from command import start

# Text and Button >-------------------------------------------


def test_create_button():
    """Test to check if create_button() work"""
    result = start.create_button()

    assert result.inline_keyboard[0][0].text == "optout"
    assert result.inline_keyboard[0][0].callback_data == "usr:start_optout"
    assert result.inline_keyboard[0][1].text == "eula"
    assert result.inline_keyboard[0][1].callback_data == "usr:start_eula"
    assert result.inline_keyboard[0][2].text == "register"
    assert result.inline_keyboard[0][2].callback_data == "usr:start_register"


# Command >---------------------------------------------------

update_setup = [
    [None, MagicMock()],
    [MagicMock, None],
]


@pytest.mark.asyncio
@pytest.mark.parametrize("chat, user", update_setup)
async def test_start_no_effective_chat_or_user(chat, user):
    """Test if start() work without effective_char or user"""
    update = MagicMock()
    update.effective_chat = chat
    update.effective_user = user

    context = AsyncMock()

    await start.start(update, context)

    context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_start_correct():
    """Test if start() work with correct input"""
    update = MagicMock()
    context = AsyncMock()

    await start.start(update, context)

    context.bot.send_message.assert_called_once()


# CallBack >------------------------------------------------------------


# --------------- { test start_optout_callback() } ---------------#


@pytest.mark.asyncio
async def test_start_optout_callback_no_user(mocker: MockerFixture):
    """Test if start_optout_callback()work without effective_user"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    optout_mocker = mocker.patch("command.start.optout", new_callable=AsyncMock)

    await start.start_optout_callback(update, context)

    context.bot.delete_message.assert_not_called()
    optout_mocker.assert_not_called()


query_input = [
    [None, None],
    [MagicMock(), None],
]


@pytest.mark.asyncio
@pytest.mark.parametrize("query, message", query_input)
async def test_start_optout_callback_no_quey(query, message, mocker: MockerFixture):
    """Test if the message is sent without query and query.message"""
    update = MagicMock()
    update.callback_query = query
    if update.callback_query is not None:
        update.callback_query.message = message

    context = AsyncMock()
    optout_mocker = mocker.patch("command.start.optout", new_callable=AsyncMock)

    await start.start_optout_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    optout_mocker.assert_not_awaited()


@pytest.mark.asyncio
async def test_start_optout_callback_correct(mocker: MockerFixture):
    """Test if the message is sent with correct input"""
    update = MagicMock()
    update.callback_query = AsyncMock()

    context = AsyncMock()
    optout_mocker = mocker.patch("command.start.optout", new_callable=AsyncMock)

    await start.start_optout_callback(update, context)

    context.bot.delete_message.assert_called_once()
    optout_mocker.assert_called_once()


# --------------- { test start_eula_callback() } ---------------#


@pytest.mark.asyncio
async def test_start_eula_callback_no_user(mocker: MockerFixture):
    """Test if the message is sent without effective_user"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    eula_mocker = mocker.patch("command.start.eula", new_callable=AsyncMock)

    await start.start_eula_callback(update, context)

    context.bot.delete_message.assert_not_called()
    eula_mocker.assert_not_called()


# get query_imput from line 80


@pytest.mark.asyncio
@pytest.mark.parametrize("query, message", query_input)
async def test_start_eula_callback_no_quey(query, message, mocker: MockerFixture):
    """Test if the message is sent without query and query.message"""
    update = MagicMock()
    update.callback_query = query
    if update.callback_query is not None:
        update.callback_query.message = message

    context = AsyncMock()
    eula_mocker = mocker.patch("command.start.eula", new_callable=AsyncMock)

    await start.start_eula_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    eula_mocker.assert_not_awaited()


@pytest.mark.asyncio
async def test_start_eula_callback_correct(mocker: MockerFixture):
    """Test if the message is sent with correct input"""
    update = MagicMock()
    update.callback_query = AsyncMock()

    context = AsyncMock()
    eula_mocker = mocker.patch("command.start.eula", new_callable=AsyncMock)

    await start.start_eula_callback(update, context)

    context.bot.delete_message.assert_called_once()
    eula_mocker.assert_called_once()


# --------------- { test start_register_callback() } ---------------#


@pytest.mark.asyncio
async def test_start_register_callback_no_user(mocker: MockerFixture):
    """Test if the message is sent without effective_user"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    register_mocker = mocker.patch("command.start.register", new_callable=AsyncMock)

    await start.start_register_callback(update, context)

    context.bot.delete_message.assert_not_called()
    register_mocker.assert_not_called()


# get query_input from line 80


@pytest.mark.asyncio
@pytest.mark.parametrize("query, message", query_input)
async def test_start_register_callback_no_quey(query, message, mocker: MockerFixture):
    """Test if the message is sent without query and query.message"""
    update = MagicMock()
    update.callback_query = query
    if update.callback_query is not None:
        update.callback_query.message = message

    context = AsyncMock()
    register_mocker = mocker.patch("command.start.register", new_callable=AsyncMock)

    await start.start_register_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    register_mocker.assert_not_awaited()


@pytest.mark.asyncio
async def test_start_register_callback_correct(mocker: MockerFixture):
    """Test if the message is sent with correct input"""
    update = MagicMock()
    update.callback_query = AsyncMock()

    context = AsyncMock()
    register_mocker = mocker.patch("command.start.register", new_callable=AsyncMock)

    await start.start_register_callback(update, context)

    context.bot.delete_message.assert_called_once()
    register_mocker.assert_called_once()
