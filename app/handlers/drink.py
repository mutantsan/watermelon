from __future__ import annotations

from typing import Any

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.utils as utils

AMOUNTS = [
    ["250", "330"],
    ["500", "750"],
    ["1000"],
]
YES = "так"
NO = "ні"


class Drink(StatesGroup):
    drink = State()
    drink_type = State()
    confirmation = State()


async def get_drink_amount_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)  # type: ignore

    for row in AMOUNTS:
        kb.add(*[types.KeyboardButton(amount) for amount in row]) # type: ignore

    return kb


async def get_drink_types_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)  # type: ignore
    type_labels = utils.get_drink_types()

    for i in range(0, len(type_labels), 2):
        if i + 1 < len(type_labels):
            kb.add(*[type_labels[i], type_labels[i + 1]])
        else:
            kb.add(type_labels[i])

    return kb


async def drink_something(message: types.Message, state: FSMContext):
    await message.answer(
        "Скільки ви випили?",
        reply_markup=await get_drink_amount_kb(),
    )
    await state.set_state(Drink.drink.state)


async def user_drinked(message: types.Message, state: FSMContext):
    drink_amount: str = message.text.lower()

    if not drink_amount.isdigit():
        await message.answer(
            "Будь ласка, оберіть обсяг випитого за допомогою клавіатури"
            " нижче.",
            reply_markup=await get_drink_amount_kb(),
        )
        return

    drink_int: int = int(drink_amount)

    if drink_int < 100:
        await message.answer(
            "Будь ласка, введіть число більше за 100мл.",
            reply_markup=await get_drink_amount_kb(),
        )
        return

    await state.update_data(amount=drink_int)

    await message.answer(
        f"Що саме ви пили?", reply_markup=await get_drink_types_kb()
    )
    await state.set_state(Drink.drink_type.state)


async def set_drink_type(message: types.Message, state: FSMContext):
    drink_type: str = message.text
    drink_type_obj = utils.get_drink_type_by_label(drink_type)

    if not drink_type_obj:
        await message.answer(
            "Будь ласка, оберіть що саме ви випили за допомогою клавіатури"
            " нижче",
            reply_markup=await get_drink_types_kb(),
        )
        return

    data: dict[str, Any] = await state.get_data("amount")
    amount = data["amount"]
    coef = drink_type_obj.coefficient
    useful_amount = int(amount * (coef / 100))

    await state.update_data(amount=useful_amount)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)  # type: ignore

    for answer in (YES, NO):
        keyboard.add(answer)

    await message.answer(
        f"Ви випили: {drink_type_obj.label} - `{amount}`мл, коефіціент гідратації - `{coef}%`. "
        f"Це дорівнює `{useful_amount}`мл води. Все правильно?",
        reply_markup=keyboard,
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.set_state(Drink.confirmation.state)


async def confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == NO:
        await message.answer(f"Почнімо з початку...")
        await state.finish()
        await drink_something(message, state)
        return

    data: dict[str, Any] = await state.get_data()
    user: types.User = message.from_user

    utils.update_drink_consumption(user.id, data["amount"])
    today_total: int = sum(d.amount for d in utils.get_today_drinks(user.id))
    norm: int = utils.calculate_user_norm(user.id)

    await message.answer(
        f"Обсяг випитої рідини внесено - `{data['amount']}`мл. Сьогодні ви"
        f" випили вже `{today_total}/{norm}` мл.",
        reply_markup=types.ReplyKeyboardRemove(),  # type: ignore
        parse_mode=types.ParseMode.MARKDOWN
    )
    await state.finish()


def register_handlers_drink(dp: Dispatcher):
    dp.register_message_handler(drink_something, commands="drink", state="*")
    dp.register_message_handler(set_drink_type, state=Drink.drink_type)
    dp.register_message_handler(user_drinked, state=Drink.drink)
    dp.register_message_handler(confirmation, state=Drink.confirmation)
