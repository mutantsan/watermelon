from aiogram import Dispatcher, types

import app.utils as utils


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_today, commands="today", state="*")


async def cmd_today(message: types.Message):
    user: types.User = message.from_user

    amount: int = sum(d.amount for d in utils.get_today_drinks(user))
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(
        f"Сьогодні ви випили {amount}/{norm} мл.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
