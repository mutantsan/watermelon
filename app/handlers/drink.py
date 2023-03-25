from curses.ascii import isdigit
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.utils as utils

AMOUNTS = [
    "250",
    "500",
    "750",
    "1000",
]
YES = "так"
NO = "ні"


class Drink(StatesGroup):
    drink_water = State()
    confirmation = State()


async def get_water_amount_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for amount in AMOUNTS:
        keyboard.add(amount)

    return keyboard


async def drink_water(message: types.Message, state: FSMContext):
    await message.answer(
        "Скільки води ви випили?", reply_markup=await get_water_amount_keyboard()
    )
    await state.set_state(Drink.drink_water.state)


async def water_drinked(message: types.Message, state: FSMContext):
    water_amount: str = message.text.lower()

    if not water_amount.isdigit():
        await message.answer(
            "Будь ласка, оберіть обсяг води, за допомогою клавіатури нижче.",
            reply_markup=await get_water_amount_keyboard(),
        )
        return

    water_int: int = int(water_amount)

    if water_int < 250:
        await message.answer(
            "Будь ласка, введіть число більше за 250мл.",
            reply_markup=await get_water_amount_keyboard(),
        )
        return

    await state.update_data(amount=water_int)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in (YES, NO):
        keyboard.add(answer)

    await message.answer(
        f"Ви випили {water_int}мл. Все правильно?", reply_markup=keyboard
    )
    await state.set_state(Drink.confirmation.state)


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == NO:
        await message.answer(f"Почнімо з початку...")
        await state.finish()
        await drink_water(message, state)
        return

    data = await state.get_data()
    user: types.User = message.from_user

    utils.update_water_consumption(user.id, data["amount"])
    today_total: int = sum(d.amount for d in utils.get_today_drinks(user.id))
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(
        f"Обсяг випитої води внесено - {data['amount']}. Сьогодні ви випили вже {today_total}/{norm}мл",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()


def register_handlers_drink(dp: Dispatcher):
    dp.register_message_handler(drink_water, commands="drink", state="*")
    dp.register_message_handler(water_drinked, state=Drink.drink_water)
    dp.register_message_handler(confirmation, state=Drink.confirmation)
