from __future__ import annotations

import locale
import logging
from datetime import datetime, date
from typing import Any, Optional
from io import BytesIO

import requests
import pytz
import matplotlib.pyplot as plt
from aiogram import types
from geopy.geocoders import Nominatim
from geopy.location import Location
from timezonefinder import TimezoneFinder

import app.model as model
import app.config as conf
import app.const as const
from app.model import Session, User, Drinks, NotificationSettings


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
    logger.info(
        f"User {user_id} has updated water consumption for {amount} ml"
    )

    Session.add(drink)
    Session.commit()


def get_today_drinks(user_id: int) -> list[Drinks]:
    user: model.User = User.get(user_id)  # type: ignore
    today: date = get_local_date(user)

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


def monthly_report_plot(user_id: int) -> BytesIO:
    """Build a monthly report plot"""
    norm: int = calculate_user_norm(user_id)
    drink_history: list[Drinks] = get_drink_history(user_id)
    aggregated_data = aggregate_monthly_data(drink_history)

    y_axis: list[int] = []
    x_axis: list[str] = []

    locale.setlocale(locale.LC_ALL, "uk_UA.utf8")

    for drink_date, amount in aggregated_data.items():
        y_axis.append(amount)
        x_axis.append(drink_date.strftime("%e %B"))

    # clear the previous data
    plt.clf()

    # set a points on a plot
    colors: list[str] = ["r" if y < norm else "b" for y in y_axis]
    plt.scatter(range(len(x_axis)), y_axis, color=colors)
    # draw a line connecting them
    plt.plot(x_axis, y_axis, "-g", alpha=0.3)

    # add a threshold line and color span
    plt.axhline(y=norm, color="r", linestyle="--", label="Добова норма")
    plt.axhspan(0, norm, color="red", alpha=0.1)

    # add labels and plot title
    plt.xlabel("Дата", fontsize=12)
    plt.ylabel("Випито води (мл.)", fontsize=12)
    plt.title("Місячний звіт", fontsize=14)

    # rotate x labels if there a too many of theme to fit the image
    if len(y_axis) > 6:
        plt.xticks(rotation=len(y_axis) * 2.85)

    plt.tight_layout()  # fitting the x axis labels after steep rotation
    plt.legend(loc="upper left")  # location of the legend
    plt.margins(y=0.10)  # y axis margin
    plt.grid()  # add a grid lines

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    return buffer


def get_drink_history(user_id: int) -> list[Drinks]:
    drinks: list[Drinks] = (
        Session.query(Drinks)
        .filter(Drinks.user_id == user_id)
        .order_by(Drinks.timestamp)
        .all()
    )

    return drinks


def aggregate_monthly_data(drink_list: list[Drinks]) -> dict[date, int]:
    aggregated_data: dict[date, int] = {}

    for drink in drink_list:
        drink_date: date = drink.timestamp.date()
        aggregated_data.setdefault(drink_date, 0)
        aggregated_data[drink_date] += drink.amount

    this_month: int = datetime.now().date().month

    return {
        _date: amount
        for _date, amount in aggregated_data.items()
        if _date.month == this_month
    }


def calculate_user_norm(user_id: int) -> int:
    """Calculate a daily water consumption for a user
    Use custom daily norm if the user has set it and do not calculate anything.

    Water consumption = N kg x 35 ml/kg/day x climate x activity

    30-40 ml per kilo is a default norm for a regular person
    """

    user: User | None = User.get(user_id)

    if not user:
        return 0

    if user.norm:
        return user.norm

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


def get_local_time(user: model.User) -> datetime:
    timezone: Any = pytz.timezone(user.timezone)
    return datetime.now(timezone)


def get_local_date(user: model.User) -> date:
    timezone: Any = pytz.timezone(user.timezone)
    return datetime.now(timezone).date()


def get_timezone_by_city(city: str) -> str:
    geolocator = Nominatim(user_agent="watermelon-tg-bot")

    location: Location | None = geolocator.geocode(city)  # type: ignore

    if not location:
        return const.DEFAULT_TZ

    tz_finder: TimezoneFinder = TimezoneFinder()

    timezone: str | None = tz_finder.timezone_at(
        lng=location.longitude, lat=location.latitude
    )

    return const.DEFAULT_TZ if not timezone else timezone


def get_or_create_user_notification_settings(user_id: int) -> NotificationSettings:
    settings: Optional[NotificationSettings] = NotificationSettings.get(user_id)

    if settings:
        return settings

    init_settings: NotificationSettings = NotificationSettings(
        user_id=user_id
    )

    model.Session.add(init_settings)
    model.Session.commit()

    logger.info(f"Settings for user {user_id} has been initialized.")
    return init_settings
