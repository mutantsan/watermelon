from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Any

import requests
import pytz
from aiogram import types

import app.config as conf
import app.const as const
from app.model import Session, User, Drinks


logger = logging.getLogger(__name__)


def create_user(user_data: dict[str, Any]) -> User:
    """Create a user withing database"""
    user: User = User(**user_data)
    Session.add(user)
    Session.commit()

    logger.info(f"{user} has been created")
    return user


def get_user(user_id: int) -> User | None:
    """Get a user from database. Return None if not exists"""
    return User.get(user_id)


def update_water_consumption(user_id: int, amount: int) -> None:
    drink: Drinks = Drinks(user_id=user_id, amount=amount)

    Session.add(drink)
    Session.commit()


def get_today_drinks(user_id: int) -> list[Drinks]:
    today = get_local_date()

    drinks: list[Drinks] = (
        Session.query(Drinks)
        .filter(Drinks.user_id == user_id)
        .filter(
            Drinks.timestamp.between(
                datetime.combine(today, datetime.min.time()),
                datetime.combine(today, datetime.max.time()),
            )
        )
        .order_by(Drinks.timestamp)
        .all()
    )

    return drinks


def calculate_user_norm(user_id: int) -> int:
    """Calculate a daily water consumption for a user

    Water consumption = N kg x 35 ml/kg/day x climate x activity

    30-40 ml per kilo is a default norm for a regular person
    """

    user: User | None = User.get(user_id)

    if not user:
        return 0

    weight: int = user.weight
    activity_value = const.ACTIVITY_MAP[user.activity]
    climate_value = const.CLIMATE_MAP[user.climate]

    return int(weight * 35 * climate_value * activity_value)


def get_user_appeal(user: types.User) -> str:
    """Get a proper way to address the user"""
    user_appeal = "друже"

    if user.first_name or user.last_name:
        user_appeal = f"{user.first_name or ''} {user.last_name or ''}"
    elif user.username:
        user_appeal = user.username

    return user_appeal


async def send_notification(message: str, chat_id: int) -> None:
    """
    Sends notification to users with a specific message
    """

    url: str = (
        f"https://api.telegram.org/bot{conf.get_bot_token()}/sendMessage"
    )

    requests.post(url, json={"chat_id": chat_id, "text": message})

    logger.info(f"Notification to user {chat_id} has been sent")


def get_local_time() -> datetime:
    kiyv_tz: Any = pytz.timezone("Europe/Kiev")
    return datetime.now(kiyv_tz)


def get_local_date() -> date:
    kiyv_tz: Any = pytz.timezone("Europe/Kiev")
    return datetime.now(kiyv_tz).date()
