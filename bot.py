import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import app.utils as utils
import app.model as model
from app.handlers.common import register_handlers_common
from app.handlers.register import register_handlers_register


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Почнімо."),
            BotCommand(command="/register", description="Реєстрація."),
        ]
    )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    bot = Bot(token=utils.get_bot_token())
    dp = Dispatcher(bot, storage=MemoryStorage())

    model.init_db()

    register_handlers_common(dp, utils.get_admin_id() or 0)
    register_handlers_register(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
