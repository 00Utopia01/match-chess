"""Test for play.py functions"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture

from command import play

# Test self_msg()>-------------------------------


@pytest.mark.asyncio
async def test_self_msg_no_message():
    """Test if send the message without update.message"""

    update = MagicMock()
    update.message = None

    await play.self_match_msg(update)

    update = MagicMock()
    update.message.reply_text = AsyncMock()

    update.message.reply_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_self_msg_correct():
    """Test if send the message without update.message"""

    update = MagicMock()
    update.message.reply_text = AsyncMock()

    await play.self_match_msg(update)

    update.message.reply_text.assert_called_once()


# Test no_user_db_msg() >-----------------------------------


button_config = [
    ("ab23!de", (1, True)),
    ("ab23!de", (2, True)),
    ("ab23!de", (3, True)),
    ("ab23!de", (1, False)),
    ("ab23!de", (2, False)),
    ("ab23!de", (3, False)),
    ("1234", (3, True)),
    ("1234", (3, False)),
]


@pytest.mark.parametrize("p1_id, modes", button_config)
def test_create_button_invalid_input(p1_id, modes):
    """Test invalid input"""
    result = play.create_button(p1_id=p1_id, mode=modes, p1_firstname="test")

    assert result is None


mode = [(1, False), (1, True), (2, False), (2, True)]


@pytest.mark.parametrize("modes", mode)
def test_create_button_correct(modes):
    """test if work with correct parameters"""
    p1_id = "1234"
    p1_firstname = "test"

    accept_callback = f"usr:accept_match_{p1_id}_{modes[0]}_{p1_firstname}"
    refuse_callback = f"usr:refuse_match_{p1_id}_{modes[0]}_{p1_firstname}"

    result = play.create_button(p1_id=p1_id, mode=modes, p1_firstname=p1_firstname)

    assert result.inline_keyboard[0][0].callback_data == accept_callback
    assert result.inline_keyboard[0][1].callback_data == refuse_callback


mode = [
    (3, False),
    (3, True),
]


@pytest.mark.parametrize("modes", mode)
def test_set_text_invalid_input(modes):
    """test invalid input"""
    result = play.set_text("test", modes)

    assert result == ""


mode_config = [
    [(1, False), "match"],
    [(2, False), "match"],
    [(1, True), "black"],
    [(2, True), "white"],
]


@pytest.mark.parametrize("modes, string", mode_config)
def test_set_text_correct(modes, string):
    """Test invalid inputs"""
    result = play.set_text("test", modes)
    assert string in result


@pytest.mark.asyncio
async def test_no_user_db_msg_no_chat():
    """Test if it works when there is no user in the DB"""
    update = MagicMock()
    update.effective_chat = None

    context = AsyncMock()

    await play.no_user_db_msg(update, context)

    context.bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_no_user_db_msg_correct():
    """Test if it works with all the correct parameters"""
    update = MagicMock()

    context = AsyncMock()

    await play.no_user_db_msg(update, context)

    context.bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_match_request_msg_no_user():
    """Test if it works when there is no user in the DB"""
    update = MagicMock()
    update.effective_user = None

    context = AsyncMock()

    await play.match_request_msg(
        p1_id="temp",
        p2_id="temp",
        mode=(1, True),
        p1_firstname="temp",
        update=update,
        context=context,
    )

    context.bot.send_message.assert_not_awaited()


mode_variable = [
    (3, False),
    (3, True),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode_variables", mode_variable)
async def test_match_request_msg_invalid_mode(mode_variables):
    """Test if works when the mode is invalid"""
    update = MagicMock()
    context = AsyncMock()

    await play.match_request_msg(
        p1_id="temp",
        p2_id="temp",
        mode=mode_variables,
        p1_firstname="temp",
        update=update,
        context=context,
    )

    context.bot.send_message.assert_not_awaited()


mode_variable = [(1, False), (2, False), (1, True), (2, True)]


@pytest.mark.asyncio
@pytest.mark.parametrize("mode_variables", mode_variable)
async def test_match_request_msg_correct(mode_variables, mocker: MockerFixture):
    "Test if it works with correct parameters"
    update = MagicMock()
    context = AsyncMock()

    await play.match_request_msg(
        p1_id="1234",
        p2_id="123",
        mode=mode_variables,
        p1_firstname="temp",
        update=update,
        context=context,
    )

    context.bot.send_message.assert_called_once_with(
        chat_id="123", text=mocker.ANY, reply_markup=mocker.ANY
    )
