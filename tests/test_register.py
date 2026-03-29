"""Test for register.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from command import register

# Text and Button >--------------------------


@pytest.mark.asyncio
async def test_already_logged_mes_correct(mocker: MockerFixture):
    """Test if work with correct input"""
    context = AsyncMock()
    message_id = 1234
    chat_id = "4321"

    await register.already_logged_mes_err(message_id, chat_id, context)

    context.bot.edit_message_text.assert_called_once_with(
        message_id=message_id, chat_id=chat_id, text=mocker.ANY
    )


@pytest.mark.asyncio
async def test_registration_completed_mes_correct(mocker: MockerFixture):
    """Test if work with correct input"""
    context = AsyncMock()
    message_id = 1234
    chat_id = "4321"

    await register.registration_completed_mes(message_id, chat_id, context)

    context.bot.edit_message_text.assert_called_once_with(
        message_id=message_id, chat_id=chat_id, text=mocker.ANY, parse_mode="HTML"
    )


@pytest.mark.asyncio
async def test_generic_db_mes_err_correct(mocker: MockerFixture):
    """Test if work with correct input"""
    context = AsyncMock()
    message_id = 1234
    chat_id = "4321"

    await register.generic_db_mes_err(message_id, chat_id, context)

    context.bot.edit_message_text.assert_called_once_with(
        message_id=message_id, chat_id=chat_id, text=mocker.ANY
    )


# Command >------------------------------------------------


@pytest.mark.asyncio
async def test_register_no_user(mocker: MockerFixture):
    """Test if the message is sent without effective_user"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()
    already_logged_mocker = mocker.patch(
        "command.register.already_logged_mes_err", new_callable=AsyncMock
    )
    registration_completed_mocker = mocker.patch(
        "command.register.registration_completed_mes", new_callable=AsyncMock
    )
    generic_db_mocker = mocker.patch(
        "command.register.generic_db_mes_err", new_callable=AsyncMock
    )

    await register.register(update, context)

    context.bot.send_message.assert_not_awaited()
    already_logged_mocker.assert_not_awaited()
    registration_completed_mocker.assert_not_awaited()
    generic_db_mocker.assert_not_awaited()


username_value = [None, "temp"]


@pytest.mark.asyncio
@pytest.mark.parametrize("username", username_value)
async def test_register_user_in_db(username, mocker: MockerFixture):
    """Test if send error message when the user is in the db"""
    update = MagicMock()
    update.effective_user.username = username

    context = AsyncMock()
    already_logged_mocker = mocker.patch(
        "command.register.already_logged_mes_err", new_callable=AsyncMock
    )
    registration_completed_mocker = mocker.patch(
        "command.register.registration_completed_mes", new_callable=AsyncMock
    )
    generic_db_mocker = mocker.patch(
        "command.register.generic_db_mes_err", new_callable=AsyncMock
    )

    mocker.patch("command.register.db.get_username", return_value="test")

    await register.register(update, context)

    context.bot.send_message.assert_called_once()
    already_logged_mocker.assert_called_once()
    registration_completed_mocker.assert_not_awaited()
    generic_db_mocker.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("username", username_value)
async def test_register_err_loading_user(username, mocker: MockerFixture):
    """Test if send error message when db.insert_user() return False"""
    update = MagicMock()
    update.effective_user.username = username

    context = AsyncMock()
    already_logged_mocker = mocker.patch(
        "command.register.already_logged_mes_err", new_callable=AsyncMock
    )
    registration_completed_mocker = mocker.patch(
        "command.register.registration_completed_mes", new_callable=AsyncMock
    )
    generic_db_mocker = mocker.patch(
        "command.register.generic_db_mes_err", new_callable=AsyncMock
    )

    mocker.patch("command.register.db.get_username", return_value=None)
    mocker.patch("command.register.db.insert_user", return_value=False)

    await register.register(update, context)

    context.bot.send_message.assert_called_once()
    already_logged_mocker.assert_not_awaited()
    registration_completed_mocker.assert_not_awaited()
    generic_db_mocker.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("username", username_value)
async def test_register_correct(username, mocker: MockerFixture):
    """Test if work when db.insert_user() return True"""
    update = MagicMock()
    update.effective_user.username = username

    context = AsyncMock()
    already_logged_mocker = mocker.patch(
        "command.register.already_logged_mes_err", new_callable=AsyncMock
    )
    registration_completed_mocker = mocker.patch(
        "command.register.registration_completed_mes", new_callable=AsyncMock
    )
    generic_db_mocker = mocker.patch(
        "command.register.generic_db_mes_err", new_callable=AsyncMock
    )

    mocker.patch("command.register.db.get_username", return_value=None)
    mocker.patch("command.register.db.insert_user", return_value=True)

    await register.register(update, context)

    context.bot.send_message.assert_called_once()
    already_logged_mocker.assert_not_awaited()
    registration_completed_mocker.assert_awaited_once()
    generic_db_mocker.assert_not_awaited()
