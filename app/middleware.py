from __future__ import annotations

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

import app.utils as utils


class RegisterMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if message.get_command() == "/register":
            return

        user: types.User = message.from_user

        if not utils.get_user(user.id):
            await message.answer(
                "Ви не зареєстровані. Натисність /register, щоб продовжити.",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            raise CancelHandler()
