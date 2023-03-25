from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter

import app.utils as utils


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(
        cmd_cancel, Text(equals="стоп", ignore_case=True), state="*"
    )
    dp.register_message_handler(cmd_admin, IDFilter(user_id=admin_id), commands="admin")


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()

    user: types.User = message.from_user

    if utils.get_user(user.id):
        user_appeal = "друже"

        if user.first_name or user.last_name:
            user_appeal = f"{user.first_name or ''} {user.last_name or ''}"
        elif user.username:
            user_appeal = user.username

        await message.answer(f"Вітаю, {user_appeal}!")
        return

    await message.answer(
        "Ви не зареєстровані. Натисність /register, щоб продовжити.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Дія скасована.", reply_markup=types.ReplyKeyboardRemove())


async def cmd_admin(message: types.Message):
    await message.answer("Вітаю! Ця команда доступна лише адміністратору бота.")
