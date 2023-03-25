from __future__ import annotations

from datetime import datetime

import app.utils as utils
import app.model as model
import app.const as const


async def notify_job():
    """Notify user if he didn't drink for N hours"""
    if await _is_night():
        return

    users: list[model.User] = model.User.all()

    for user in users:
        treshold: int = const.HOUR * 2
        user_drinks: list[model.Drinks] = utils.get_today_drinks(user.id)
        last_drink: model.Drinks | None = (
            user_drinks[-1] if user_drinks else None
        )

        if not last_drink:
            return await utils.send_notification(
                f"Ви сьогодні ще не пили. Зробіть це зараз /drink", user.id
            )

        time_passed: float = (
            datetime.now() - last_drink.timestamp
        ).total_seconds()
        today_total: int = sum(
            d.amount for d in utils.get_today_drinks(user.id)
        )
        norm: int = utils.calculate_user_norm(user.id)

        if today_total >= norm:
            return

        if time_passed >= treshold:
            await utils.send_notification(
                (
                    f"Ви не пили вже {int(time_passed//const.HOUR)} годин(и)."
                    " Зробіть це зараз /drink"
                ),
                user.id,
            )


async def _is_night() -> bool:
    """Check if it's too late to send notifications"""
    current_hour: int = datetime.now().hour

    return current_hour >= 22 or current_hour < 8
