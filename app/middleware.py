from __future__ import annotations

import logging

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

import app.utils as utils


logger = logging.getLogger(__name__)


class RegisterMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        if (message.get_command() == "/register") or (
            "Registration" in data.get("raw_state", "")
        ):
            return

        user: types.User = message.from_user

        if not utils.get_user(user.id):
            logger.info(f"User {user.id} {user.username or ''} isn't registered")
            await message.answer(
                "Ви не зареєстровані. Натисність /register, щоб продовжити.",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            raise CancelHandler()
