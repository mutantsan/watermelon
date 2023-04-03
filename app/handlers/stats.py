from aiogram import Dispatcher, types
from app.model import Drinks

import app.utils as utils


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_today, commands="today", state="*")
    dp.register_message_handler(cmd_graph, commands="graph", state="*")


async def cmd_today(message: types.Message):
    user: types.User = message.from_user

    amount: int = sum(d.amount for d in utils.get_today_drinks(user.id))
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(
        f"Сьогодні ви випили {amount}/{norm} мл.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cmd_graph(message: types.Message):
    drink_history: list[Drinks] = utils.get_drink_history(message.from_user.id)
    aggregated_data = utils.aggregate_monthly_data(drink_history)

    await message.answer_photo(
        utils.monthly_report_plot(aggregated_data)
    )
