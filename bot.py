import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage


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

    bot = Bot(token=os.environ.get("BOT_TOKEN"))
    dp = Dispatcher(bot, storage=MemoryStorage())

    await set_commands(bot)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
