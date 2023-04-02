from __future__ import annotations

import logging
from datetime import datetime

import app.utils as utils
import app.model as model
import app.const as const


logger = logging.getLogger(__name__)


async def notify_job():
    """Notify user if he didn't drink for N hours"""

    users: list[model.User] = model.User.all()

    for user in users:
        if not user.notify:
            logger.info(
                f"User {user.id} {user.name} has turned off his notifications."
                " Skipping."
            )
            continue

        if _is_night(user):
            logger.info(
                "It's too late to send notifications for a user. Skipping."
                f" {user.id} {user.name}"
            )
            continue

        await _notify_user(user)


async def _notify_user(user: model.User):
    """Notify a user if didn't drink properly

    - If he didn't drink today
    - If more than 2 hours have passed since the previous time

    Args:
        user (model.User): User object
    """
    user_drinks: list[model.Drinks] = utils.get_today_drinks(user)
    last: model.Drinks | None = user_drinks[-1] if user_drinks else None

    if not last:
        return await utils.send_notification(
            f"Ви сьогодні ще не пили. Зробіть це зараз /drink", user.id
        )

    if _get_today_total(user) >= utils.calculate_user_norm(user.id):
        return

    time_passed: float = (datetime.utcnow() - last.timestamp).total_seconds()

    if abs(time_passed) >= const.NOTIFY_THRESHOLD:
        await utils.send_notification(
            (
                f"Ви не пили вже {int(time_passed//const.HOUR)} годин(и)."
                " Зробіть це зараз /drink"
            ),
            user.id,
        )


def _get_today_total(user: model.User) -> int:
    """Get the number of how much the user drank today"""
    return sum(d.amount for d in utils.get_today_drinks(user))


def _is_night(user: model.User) -> bool:
    """Check if it's too late to send notifications for a specific user
    according to his timezone"""
    local_time: int = utils.get_local_time(user).hour

    return local_time >= 22 or local_time < 8
