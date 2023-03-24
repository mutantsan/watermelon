from __future__ import annotations

import os
from typing import Any

from app.model import Session, User
from app.exceptions import BotConfigError


def create_user(user_data: dict[str, Any]) -> User:
    user: User = User(**user_data)
    Session.add(user)
    Session.commit()

    return user


def get_user(user_id: int) -> User | None:
    return Session.get(User, user_id)


def get_bot_token() -> str:
    token: str | None = os.environ.get("BOT_TOKEN")

    if not token:
        raise BotConfigError("Set a bot token to proceed!")

    return token


def get_admin_id() -> int | None:
    admin_id: str | None = os.environ.get("ADMIN_ID")

    if not admin_id:
        return

    if not admin_id.isdigit():
        raise BotConfigError("Admin ID must be an integer!")

    return int(admin_id)
