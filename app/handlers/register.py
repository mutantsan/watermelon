from __future__ import annotations

from typing import Any

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.utils as utils
import app.const as const

ACTIVITIES = [
    "малорухливий",
    "легка активність",
    "помірно активний",
    "дуже активний",
    "надзвичайно активний",
]
CLIMATES = ["тропічний", "помірний", "холодний"]
YES = "так"
NO = "ні"


class Registration(StatesGroup):
    user_activity = State()
    user_climate = State()
    user_weight = State()
    user_timezone = State()
    confirmation = State()


async def register_start(message: types.Message, state: FSMContext):
    if utils.get_user(message.from_user.id):
        return await message.answer("Ви вже зарєстровані.")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for activity in ACTIVITIES:
        keyboard.add(activity)

    await message.answer("Почнімо процес реєстрації!")
    await message.answer(
        "Оберіть ваш рівень активності:", reply_markup=keyboard
    )
    await state.set_state(Registration.user_activity.state)


async def activity_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in ACTIVITIES:
        await message.answer(
            "Будь ласка, оберіть рівень активності, за допомогою клавіатури"
            " нижче."
        )
        return

    await state.update_data(activity=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for climate in CLIMATES:
        keyboard.add(climate)

    await state.set_state(Registration.user_climate.state)
    await message.answer("Оберіть тип вашого клімату:", reply_markup=keyboard)


async def climate_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in CLIMATES:
        await message.answer(
            "Будь ласка, оберіть тип вашого клімату, за допомогою клавіатури"
            " нижче."
        )
        return

    await state.update_data(climate=message.text.lower())

    await state.set_state(Registration.user_weight.state)
    await message.answer(
        "Введіть вашу вагу:", reply_markup=types.ReplyKeyboardRemove()
    )


async def weight_provided(message: types.Message, state: FSMContext):
    if not message.text.lower().isdigit():
        await message.answer("Вага має бути вказана, як число. Приклад: 67")
        return

    await state.update_data(weight=int(message.text.lower()))

    await state.set_state(Registration.user_timezone.state)
    await message.answer(
        (
            "Введіть назву вашого міста. Це потрібно, щоб визначити ваш"
            " часовий пояс:"
        ),
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def timezone_provided(message: types.Message, state: FSMContext):
    if not message.text.isalpha():
        await message.answer(
            "Введіть тільки назву вашого міста. Приклад: Київ"
        )
        return

    data: dict[str, Any] = await state.get_data()
    tz: str = utils.get_timezone_by_city(message.text)
    await state.update_data(timezone=tz)

    await message.answer(
        "Ви вказали наступні дані. "
        f"Активність: {data['activity']}, Клімат: {data['climate']}, "
        f"Вага: {data['weight']}. Часовий пояс: {message.text}, {tz}"
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in (YES, NO):
        keyboard.add(answer)

    await state.set_state(Registration.confirmation.state)
    await message.answer("Все вірно?", reply_markup=keyboard)


async def need_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == NO:
        await message.answer(f"Почнімо з початку...")
        await state.finish()
        await register_start(message, state)
        return

    data: dict[str, Any] = await state.get_data()
    user: types.User = message.from_user

    data.update(
        id=user.id,
        name=user.username,
        fullname=f"{user.first_name or ''} {user.last_name or ''}",
    )

    utils.create_user(data)

    await message.answer(
        f"Користувач успішно створений!",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()


def register_handlers_register(dp: Dispatcher):
    dp.register_message_handler(register_start, commands="register", state="*")
    dp.register_message_handler(
        activity_chosen, state=Registration.user_activity
    )
    dp.register_message_handler(
        climate_chosen, state=Registration.user_climate
    )
    dp.register_message_handler(
        weight_provided, state=Registration.user_weight
    )
    dp.register_message_handler(
        timezone_provided, state=Registration.user_timezone
    )
    dp.register_message_handler(need_confirm, state=Registration.confirmation)
