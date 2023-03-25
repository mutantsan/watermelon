import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import app.config as conf
import app.model as model
from app.handlers import (
    register_handlers_drink,
    register_handlers_register,
    register_handlers_common,
    register_handlers_stats
)


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Register BOT commands that will be accessible via dropdown menu in telegram"""
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Почнімо."),
            BotCommand(command="/register", description="Реєстрація."),
            BotCommand(command="/drink", description="Випити водички."),
            BotCommand(command="/today", description="Скільки я сьогодні випив?"),
        ]
    )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    bot = Bot(token=conf.get_bot_token())
    dp = Dispatcher(bot, storage=MemoryStorage())

    model.init_db()

    register_handlers_common(dp, conf.get_admin_id())
    register_handlers_register(dp)
    register_handlers_drink(dp)
    register_handlers_stats(dp)

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
