import asyncio
import logging
import inspect

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import app.jobs as jobs
import app.config as conf
import app.model as model
from app.middleware import RegisterMiddleware
from app.handlers import get_handlers


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Register BOT commands that will be accessible via dropdown menu in telegram"""
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Почнімо."),
            BotCommand(command="/drink", description="Випити водички."),
            BotCommand(command="/stats", description="Статистика."),
            BotCommand(command="/settings", description="Налаштування."),
            BotCommand(command="/cancel", description="Скасувати дію."),
        ]
    )


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting watermelon bot")

    bot = Bot(token=conf.get_bot_token())
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Initialize database
    model.init_db()

    # Register handlers
    for handler in get_handlers():
        if len(inspect.getfullargspec(handler).args) == 2:
            handler(dp, conf.get_admin_id())  # type: ignore
        else:
            handler(dp)  # type: ignore

    # Setup Middlewares
    dp.middleware.setup(RegisterMiddleware())

    # Setup BOT commands
    await set_commands(bot)

    # Setup task scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(jobs.notify_job, "interval", minutes=5)
    scheduler.add_job(jobs.water_facts, "interval", minutes=60)

    scheduler.start()

    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
