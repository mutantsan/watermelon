from __future__ import annotations

from datetime import datetime, date
from typing import Any

from aiogram import types

import app.const as const
from app.model import Session, User, Drinks


def create_user(user_data: dict[str, Any]) -> User:
    """Create a user withing database"""
    user: User = User(**user_data)
    Session.add(user)
    Session.commit()

    return user


def get_user(user_id: int) -> User | None:
    """Get a user from database. Return None if not exists"""
    return User.get(user_id)


def update_water_consumption(user_id: int, amount: int) -> None:
    drink: Drinks = Drinks(user_id=user_id, timestamp=datetime.now(), amount=amount)

    Session.add(drink)
    Session.commit()


def get_today_drinks(user_id: int) -> int:
    today: date = date.today()

    drinks: list[Drinks] = (
        Session.query(Drinks)
        .filter(Drinks.user_id == user_id)
        .filter(
            Drinks.timestamp.between(
                datetime.combine(today, datetime.min.time()),
                datetime.combine(today, datetime.max.time()),
            )
        )
        .all()
    )

    return sum(d.amount for d in drinks)


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
