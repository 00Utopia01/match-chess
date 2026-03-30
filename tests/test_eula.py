"""Test for eula.py"""

# pylint: disable=duplicate-code

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from command import eula

# Text and Button >---------------------------------------


def test_create_button():
    """Test to check if create_button() work"""
    result = eula.create_button()

    assert result.inline_keyboard[0][0].text == "optout"
    assert result.inline_keyboard[0][0].callback_data == "usr:del_and_start_optout"
    assert result.inline_keyboard[0][1].text == "register"
    assert result.inline_keyboard[0][1].callback_data == "usr:del_and_start_register"


# Command >-----------------------------------------------


@pytest.mark.asyncio
async def test_eula_without_chat():
    """Test if the message is sent without effective_chat"""
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


# Callback >---------------------------------------------


# --------------- { test del_message_and_optout_callback() } ---------------#


@pytest.mark.asyncio
async def test_del_message_and_optout_callback_no_user(mocker: MockerFixture):
    """Test if the message is sent without effective_chat"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    optout_mocker = mocker.patch("command.eula.optout", new_callable=AsyncMock)

    await eula.del_message_and_optout_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    optout_mocker.assert_not_awaited()


query_input = [
    [None, None],
    [MagicMock(), None],
]


@pytest.mark.asyncio
@pytest.mark.parametrize("query, message", query_input)
async def test_del_message_and_optout_callback_no_quey(query, message, mocker):
    """Test if the message is sent without query and query.message"""
    update = MagicMock()
    update.callback_query = query
    if update.callback_query is not None:
        update.callback_query.message = message

    context = AsyncMock()
    optout_mocker = mocker.patch("command.eula.optout", new_callable=AsyncMock)

    await eula.del_message_and_optout_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    optout_mocker.assert_not_awaited()


@pytest.mark.asyncio
async def test_del_message_and_optout_callback_correct(mocker: MockerFixture):
    """Test if the message is sent with correct input"""
    update = MagicMock()
    update.effective_user.id = 1234
    update.callback_query.message.message_id = 4321

    context = AsyncMock()
    optout_mocker = mocker.patch("command.eula.optout", new_callable=AsyncMock)

    await eula.del_message_and_optout_callback(update, context)

    context.bot.delete_message.assert_called_once_with(
        chat_id=1234,
        message_id=4321,
    )
    optout_mocker.assert_awaited_once()


# --------------- { test del_message_and_register_callback() } ---------------#


@pytest.mark.asyncio
async def test_del_message_and_register_callback_no_user(mocker: MockerFixture):
    """Test if the message is sent without effective_chat"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    register_mocker = mocker.patch("command.eula.register", new_callable=AsyncMock)

    await eula.del_message_and_register_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    register_mocker.assert_not_awaited()


query_input = [
    [None, None],
    [MagicMock(), None],
]


@pytest.mark.asyncio
@pytest.mark.parametrize("query, message", query_input)
async def test_del_message_and_register_callback_no_quey(query, message, mocker):
    """Test if the message is sent without query and query.message"""
    update = MagicMock()
    update.callback_query = query
    if update.callback_query is not None:
        update.callback_query.message = message

    context = AsyncMock()
    register_mocker = mocker.patch("command.eula.register", new_callable=AsyncMock)

    await eula.del_message_and_register_callback(update, context)

    context.bot.delete_message.assert_not_awaited()
    register_mocker.assert_not_awaited()


@pytest.mark.asyncio
async def test_del_message_and_register_callback_correct(mocker: MockerFixture):
    """Test if the message is sent with correct input"""
    update = MagicMock()
    update.effective_user.id = 1234
    update.callback_query.message.message_id = 4321

    context = AsyncMock()
    register_mocker = mocker.patch("command.eula.register", new_callable=AsyncMock)

    await eula.del_message_and_register_callback(update, context)

    context.bot.delete_message.assert_called_once_with(
        chat_id=1234,
        message_id=4321,
    )
    register_mocker.assert_awaited_once()
