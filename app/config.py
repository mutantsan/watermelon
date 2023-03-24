from __future__ import annotations

import os

from app.exceptions import BotConfigError
from app.const import BOT_TOKEN, ADMIN_ID, DEBUG_MODE


def get_bot_token() -> str:
    """Get a bot token. Register a bot with @BotFather (https://t.me/BotFather)
    to access a token"""
    token: str | None = os.environ.get(BOT_TOKEN)

    if not token:
        raise BotConfigError("Set a bot token to proceed!")

    return token


def get_admin_id() -> int:
    """Return an admin user_id. Return -1 if not set to restrict admin commands
    for everyone"""
    admin_id: str | None = os.environ.get(ADMIN_ID)

    if not admin_id:
        return -1

    if not admin_id.isdigit():
        raise BotConfigError("Admin ID must be an integer!")

    return int(admin_id)


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return bool(os.environ.get(DEBUG_MODE))
