from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import app.utils as utils


def register_handlers_stats(dp: Dispatcher):
    dp.register_message_handler(cmd_stats, commands="stats", state="*")

    dp.callback_query_handler(lambda c: c.data == "graph")(cb_graph)
    dp.callback_query_handler(lambda c: c.data == "today")(cb_today)

    dp.register_message_handler(cmd_graph, commands="graph", state="*")
    dp.register_message_handler(cmd_today, commands="today", state="*")

    dp.callback_query_handler(lambda c: c.data == "close")(cb_close)


async def cmd_stats(message: types.Message):
    await message.answer(
        "Статистика",
        reply_markup=(
            types.InlineKeyboardMarkup()
            .row(
                types.InlineKeyboardButton(
                    f"🗓️ Місячний звіт",
                    callback_data="graph",
                ),
                types.InlineKeyboardButton(
                    f"💦 Скільки я сьогодні випив",
                    callback_data="today",
                ),
            )
            .row(
                types.InlineKeyboardButton(
                    f"🔙 Закрити",
                    callback_data="close",
                ),
            )
        ),
    )


async def cb_today(query: types.CallbackQuery, state: FSMContext):
    await query.answer(await cmd_today(query.message))


async def cmd_today(message: types.Message):
    amount: int = sum(d.amount for d in utils.get_today_drinks(message.chat.id))
    norm: int = utils.calculate_user_norm(message.chat.id)

    await message.answer(
        f"Сьогодні ви випили {amount}/{norm} мл.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cb_graph(query: types.CallbackQuery, state: FSMContext):
    await query.answer(await cmd_graph(query.message))


async def cmd_graph(message: types.Message):
    await message.answer_photo(utils.monthly_report_plot(message.chat.id))


async def cb_close(query: types.CallbackQuery):
    await query.bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=types.InlineKeyboardMarkup(),
    )
