from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import app.utils as utils


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_today, commands="today", state="*")


async def cmd_today(message: types.Message):
    user: types.User = message.from_user

    if not utils.get_user(user.id):
        return await message.answer(
            "Ви не зареєстровані. Натисність /register, щоб продовжити.",
            reply_markup=types.ReplyKeyboardRemove(),
        )

    amount: int = utils.get_today_drinks(user.id)
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(f"Сьогодні ви випили {amount} мл.")
    await message.answer(f"Ваша норма {norm} мл.")
