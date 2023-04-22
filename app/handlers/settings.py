from __future__ import annotations

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.model as model
import app.utils as utils
from app.handlers.register import register_start


SETTINGS = ["notify"]


class DailyNorm(StatesGroup):
    wait_for_input = State()


class NotificationRange(StatesGroup):
    wait_for_input = State()


class NotificationFrequency(StatesGroup):
    wait_for_input = State()


def register_handlers_settings(dp: Dispatcher):
    dp.register_message_handler(cmd_settings, commands="settings", state="*")
    dp.callback_query_handler(lambda c: c.data == "notifications")(
        cb_notifications
    )
    dp.callback_query_handler(lambda c: c.data == "close")(cb_close)
    dp.callback_query_handler(lambda c: c.data == "user_update")(
        cb_user_update
    )
    dp.callback_query_handler(lambda c: c.data == "daily_norm")(cb_daily_norm)
    dp.register_message_handler(confirm_norm, state=DailyNorm.wait_for_input)

    dp.callback_query_handler(lambda c: c.data == "n_time")(cb_n_time)
    dp.callback_query_handler(lambda c: c.data == "n_frequency")(
        cb_n_frequency
    )


async def cmd_settings(message: types.Message):
    user: model.User = model.User.get(message.from_user.id)  # type: ignore

    await message.answer(
        "Налаштування",
        reply_markup=_get_settigns_kb(user),
    )


async def cb_notifications(query: types.CallbackQuery):
    user: model.User = model.User.get(query.from_user.id)  # type: ignore
    user.toggle_notifications()

    await query.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=_get_settigns_kb(user),
    )


def _get_settigns_kb(user: model.User) -> types.InlineKeyboardMarkup:
    notification_state: str = "увімкнені" if user.notify else "вимкнені"

    return (
        types.InlineKeyboardMarkup()
        .row(
            types.InlineKeyboardButton(
                f"⚙️ Сповіщення ({notification_state})",
                callback_data="notifications",
            ),
            types.InlineKeyboardButton(
                f"⚙️ Оновити дані юзера",
                callback_data="user_update",
            ),
        )
        .row(
            types.InlineKeyboardButton(
                f"🚰 Встановити добову норму",
                callback_data="daily_norm",
            ),
            types.InlineKeyboardButton(
                f"🕓 Час сповіщень",
                callback_data="n_time",
            ),
        )
        .row(
            types.InlineKeyboardButton(
                f"🔔 Частота сповіщень",
                callback_data="n_frequency",
            ),
        )
        .row(
            types.InlineKeyboardButton(
                f"🔙 Закрити",
                callback_data="close",
            ),
        )
    )


async def cb_close(query: types.CallbackQuery):
    await query.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(),
    )


async def cb_user_update(query: types.CallbackQuery, state: FSMContext):
    user: model.User = model.User.get(query.from_user.id)  # type: ignore
    user.drop()

    await query.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(),
    )
    await register_start(query.message, state)


async def cb_daily_norm(query: types.CallbackQuery):
    """Set a custom daily norm for a user"""
    current_norm: int = utils.calculate_user_norm(query.message.chat.id)

    await query.message.answer(f"Ваша поточна добова норма - {current_norm}")
    await query.message.answer("Введіть нову норму (ціле число)")
    await query.answer(await DailyNorm.wait_for_input.set())


async def confirm_norm(message: types.Message, state: FSMContext):
    new_norm: str = message.text

    if not new_norm.isdigit():
        await message.answer(
            "Добова норма має бути цілим числом. Спробуйте ще раз."
        )
        return await DailyNorm.wait_for_input.set()

    user: model.User = model.User.get(message.from_user.id)  # type: ignore
    user.set_norm(int(new_norm))

    await state.finish()

    await message.answer(f"Нова норма встановлена - {new_norm}!")


async def cb_n_time(query: types.CallbackQuery, state: FSMContext):
    pass


async def cb_n_frequency(query: types.CallbackQuery, state: FSMContext):
    pass
