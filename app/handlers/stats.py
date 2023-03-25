from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import app.utils as utils


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_today, commands="today", state="*")


async def cmd_today(message: types.Message):
    print(message)
    user: types.User = message.from_user

    amount: int = sum(d.amount for d in utils.get_today_drinks(user.id))
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(f"Сьогодні ви випили {amount} мл.")
    await message.answer(f"Ваша норма {norm} мл.")
