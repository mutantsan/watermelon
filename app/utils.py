from __future__ import annotations

from typing import Any

from app.model import Session, User


def create_user(user_data: dict[str, Any]) -> User:
    """Create a user withing database"""
    user: User = User(**user_data)
    Session.add(user)
    Session.commit()

    return user


def get_user(user_id: int) -> User | None:
    """Get a user from database. Return None if not exists"""
    return Session.get(User, user_id)
