"""Tests for callback.py"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from src import callback


@pytest.mark.asyncio
async def test_handle_euela_accept_failure():
    """This functions tests the initial returns on accept_euela func"""
    update = MagicMock()
    update.callback_query = None
    context = MagicMock()

    await callback.handle_euela_accept(update, context)


@pytest.mark.asyncio
async def test_handle_euela_accept_success():
    """This function handles the successful cases on accept_euela function"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    update.callback_query = query
    await callback.handle_euela_accept(update, context)

    query.answer.assert_awaited_once()
    query.edit_message_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_euela_decline_none_values():
    """Tests None values on euela_decline function"""
    update = AsyncMock()
    context = AsyncMock()

    update.callback_query = None
    update.effective_user = None

    await callback.handle_euela_decline(update, context)


@pytest.mark.asyncio
async def test_handle_euela_decline_case_false(mocker: MockerFixture):
    """Tests the case on witch the db call return false"""

    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    update.callback_query = query

    update.effective_user = MagicMock()
    query.edit_message_text = AsyncMock()
    query.answer = AsyncMock()

    mocker.patch("src.db_manager.MatchesDB.del_user", return_value=False)

    await callback.handle_euela_decline(update, context)

    query.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_euela_decline_case_true(mocker: MockerFixture):
    """Tests the case on witch the db call returns true"""

    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    update.callback_query = query

    update.effective_user = MagicMock()
    query.edit_message_text = AsyncMock()
    query.answer = AsyncMock()

    mocker.patch("src.db_manager.MatchesDB.del_user", return_value=True)

    await callback.handle_euela_decline(update, context)

    query.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_match_decline_case_query_is_none():
    """Tests the null query cases"""
    context = MagicMock()

    query = MagicMock()
    query.message = None
    await callback.match_decline(query, context)


@pytest.mark.asyncio
async def test_match_decline_success():
    """Tests the delete message function"""
    context = MagicMock()

    query = MagicMock()
    query.message = AsyncMock()
    context.bot.delete_message = AsyncMock()

    await callback.match_decline(query, context)
    context.bot.delete_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_refuse_match():
    """Tests the function's early returns"""
    update = MagicMock()
    context = MagicMock()

    update.callback_query = None
    await callback.handle_refuse_match(update, context)


@pytest.mark.asyncio
async def test_handle_refuse_match_context_error():
    """tests the function for context errors"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    query.answer = AsyncMock()
    update.callback_query = query

    context.match = None
    update.effective_user = AsyncMock()

    await callback.handle_refuse_match(update, context)
    query.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_refuse_match_update_error():
    """tests the function for update errors"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    query.answer = AsyncMock()
    update.callback_query = query

    context.match = AsyncMock()
    update.effective_user = None

    await callback.handle_refuse_match(update, context)
    query.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_refuse_match_success():
    """Test for succesful function call"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    update.callback_query = query

    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    context.bot = AsyncMock()
    context.match = AsyncMock()
    context.match.group = AsyncMock()

    await callback.handle_refuse_match(update, context)

    query.answer.assert_awaited_once()
    query.edit_message_text.assert_awaited_once()
    context.bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_accept_match_early_returns():
    """tests the early function returns on a None query"""
    update = MagicMock()
    context = MagicMock()

    update.callback_query = None
    await callback.handle_accept_match(update, context)


@pytest.mark.asyncio
async def test_handle_accept_match_context_error():
    """Tests the function for context errors"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    query.answer = AsyncMock()
    update.callback_query = query

    context.match = None
    update.effective_user = AsyncMock()

    await callback.handle_accept_match(update, context)


@pytest.mark.asyncio
async def test_handle_accept_match_update_error():
    """tests the function for update errors"""
    update = MagicMock()
    context = MagicMock()

    query = MagicMock()
    query.answer = AsyncMock()
    update.callback_query = query

    context.match = AsyncMock()
    update.effective_user = None

    await callback.handle_accept_match(update, context)
