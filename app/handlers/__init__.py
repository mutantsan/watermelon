from __future__ import annotations

from typing import Callable

from aiogram import Dispatcher

from app.handlers.common import register_handlers_common
from app.handlers.register import register_handlers_register
from app.handlers.drink import register_handlers_drink
from app.handlers.stats import register_handlers_stats


def get_handlers() -> (
    list[Callable[[Dispatcher], None] | Callable[[Dispatcher, int], None]]
):
    return [
        register_handlers_common,
        register_handlers_drink,
        register_handlers_register,
        register_handlers_stats,
    ]
