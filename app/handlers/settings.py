from __future__ import annotations

from typing import cast
from datetime import time, datetime

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
    dp.register_message_handler(
        confirm_n_time, state=NotificationRange.wait_for_input
    )

    dp.callback_query_handler(lambda c: c.data == "n_frequency")(
        cb_n_frequency
    )
    dp.register_message_handler(
        confirm_n_frequency, state=NotificationFrequency.wait_for_input
    )


async def cmd_settings(message: types.Message):
    user: model.User = cast(model.User, model.User.get(message.from_user.id))

    await message.answer(
        "Налаштування",
        reply_markup=_get_settigns_kb(user),
    )


async def cb_notifications(query: types.CallbackQuery):
    user: model.User = cast(model.User, model.User.get(query.from_user.id))
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
    user: model.User = cast(model.User, model.User.get(query.from_user.id))
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

    user: model.User = cast(model.User, model.User.get(message.from_user.id))
    user.set_norm(int(new_norm))

    await state.finish()

    await message.answer(f"Нова норма встановлена - {new_norm}!")


async def cb_n_time(query: types.CallbackQuery, state: FSMContext):
    """Set a notification time range"""
    settings: model.NotificationSettings = (
        utils.get_or_create_user_notification_settings(query.message.chat.id)
    )

    await query.message.answer(
        f"Поточний діапазон нотифікацій: {settings.get_humanized_n_range()}"
    )
    await query.message.answer(
        "Введіть новий діапазон у якій будуть присилатися сповіщення. Приклад:"
        " 7.30-21"
    )
    await query.answer(await NotificationRange.wait_for_input.set())


async def confirm_n_time(message: types.Message, state: FSMContext):
    new_range: str = message.text

    try:
        start, end = new_range.split("-")
    except ValueError:
        await message.answer("Діпазон має бути у форматі 7.30-21.45.")
        return await NotificationRange.wait_for_input.set()

    if not _is_int_or_float(start) or not _is_int_or_float(end):
        await message.answer("Діпазон має бути у форматі 7.30-21.45.")
        return await NotificationRange.wait_for_input.set()

    try:
        start_time: time = _string_to_time(start)
        end_time: time = _string_to_time(end)
    except ValueError:
        await message.answer(
            "Не виходить спарсити час. Перевірти формат введення, приклад:"
            " 7.30-21.45 або 8-22. Максимальний кінцевий час 23.59"
        )
        return await NotificationRange.wait_for_input.set()

    if start_time > end_time:
        await message.answer(
            "Початковий час не може бути більший за кінцевий!"
            " 7.30-21.45 або 8-22"
        )
        return await NotificationRange.wait_for_input.set()

    start_minutes = _calc_minutes(start_time)
    end_minutes = _calc_minutes(end_time)

    settings: model.NotificationSettings = (
        utils.get_or_create_user_notification_settings(message.from_user.id)
    )

    settings.update_range(start_minutes, end_minutes)

    await state.finish()

    await message.answer(
        f"Встановлений новий діапазон для сповіщень - З {start} до {end}!"
    )


def _is_int_or_float(number: str) -> bool:
    try:
        float(number)
    except ValueError:
        return False

    return True


def _string_to_time(t: str) -> time:
    _format: str = "%H.%M" if "." in t else "%H"
    return datetime.strptime(t.strip(), _format).time()


def _calc_minutes(time: time) -> int:
    return time.hour * 60 + time.minute


async def cb_n_frequency(query: types.CallbackQuery, state: FSMContext):
    """Set a notification frequency for a user"""
    settings: model.NotificationSettings = (
        utils.get_or_create_user_notification_settings(query.message.chat.id)
    )

    await query.message.answer(
        f"Зараз сповіщення приходять кожні {settings.frequency} хвилин"
    )
    await query.message.answer(
        "Введіть нову частоту у хвилинах (ціле число, більше 5)"
    )
    await query.answer(await NotificationFrequency.wait_for_input.set())


async def confirm_n_frequency(message: types.Message, state: FSMContext):
    new_frequency: str = message.text

    if (
        not new_frequency.isdigit()
        or int(new_frequency) < 1
        or int(new_frequency) > 60
    ):
        await message.answer(
            "Введіть нову частоту у хвилинах (ціле число, від 5 до 60)"
        )
        return await NotificationFrequency.wait_for_input.set()

    settings: model.NotificationSettings = (
        utils.get_or_create_user_notification_settings(message.from_user.id)
    )

    settings.update_frequency(int(new_frequency))

    await state.finish()

    await message.answer(
        f"Встановлена нова частота сповіщень - {new_frequency}!"
    )
