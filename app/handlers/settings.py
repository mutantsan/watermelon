from __future__ import annotations

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import app.model as model
from app.handlers.register import register_start


SETTINGS = ["notify"]


def register_handlers_settings(dp: Dispatcher):
    dp.register_message_handler(cmd_settings, commands="settings", state="*")
    dp.callback_query_handler(lambda c: c.data == "notifications")(
        cb_notifications
    )
    dp.callback_query_handler(lambda c: c.data == "close")(cb_close)
    dp.callback_query_handler(lambda c: c.data == "user_update")(
        cb_user_update
    )


async def cmd_settings(message: types.Message):
    await message.answer(
        "Налаштування",
        reply_markup=_get_settigns_kb(message.from_user.id),
    )


async def cb_notifications(query: types.CallbackQuery):
    await query.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=_get_settigns_kb(query.from_user.id),
    )


def _get_settigns_kb(user_id: int) -> types.InlineKeyboardMarkup:
    user: model.User = model.User.get(user_id)  # type: ignore
    notification_state: str = (
        "увімкнені" if user.toggle_notifications() else "вимкнені"
    )

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
