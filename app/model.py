from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy import types
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    scoped_session,
    relationship,
)
from typing_extensions import Self

from app.config import is_debug_enabled


logger = logging.getLogger(__name__)
engine = create_engine("sqlite:///water.sqlite")
Session = scoped_session(
    sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(types.String)
    fullname: Mapped[Optional[str]] = mapped_column(types.String)
    weight: Mapped[int] = mapped_column(types.Integer, nullable=False)
    climate: Mapped[str] = mapped_column(types.String, nullable=False)
    activity: Mapped[str] = mapped_column(types.String, nullable=False)
    notify: Mapped[bool] = mapped_column(
        types.Boolean, default=True, nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        types.String, server_default="Europe/Kiev"
    )
    norm: Mapped[int] = mapped_column(types.Integer, nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"

    @classmethod
    def get(cls, user_reference: Optional[int]) -> Optional[Self]:
        query = Session.query(cls).autoflush(False)
        query = query.filter(cls.id == user_reference)
        return query.first()

    @classmethod
    def all(cls) -> list[Self]:
        return Session.query(cls).all()

    def toggle_notifications(self) -> bool:
        self.notify = not self.notify
        logger.info(f"Toggle notifications for user {self.id}: {self.notify}.")

        Session.commit()

        return self.notify

    def drop(self) -> None:
        Session.delete(self)
        logger.info(f"User {self.id} has been deleted")

        Session.commit()

    def set_norm(self, norm: int) -> int:
        self.norm = norm
        logger.info(f"Setting custom daily norm for user {self.id}")

        Session.commit()

        return self.norm


class Drinks(Base):
    __tablename__ = "drinks"

    id: Mapped[str] = mapped_column(
        types.Text(length=36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    amount: Mapped[int] = mapped_column(types.Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        types.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"User(id={self.user_id}, date={self.timestamp},"
            f" amount={self.amount})"
        )


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id: Mapped[str] = mapped_column(
        types.Text(length=36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    start_time: Mapped[int] = mapped_column(
        types.Integer, nullable=False, default=480
    )
    end_time: Mapped[int] = mapped_column(
        types.Integer, nullable=False, default=1320
    )
    frequency: Mapped[int] = mapped_column(
        types.Integer, nullable=False, default=15
    )
    notified_at: Mapped[datetime] = mapped_column(
        types.DateTime, nullable=True
    )

    user = relationship(User)

    @classmethod
    def get(cls, user_reference: Optional[int]) -> Optional[Self]:
        query = Session.query(cls).autoflush(False)
        query = query.filter(cls.user_id == user_reference)
        return query.one_or_none()

    def update_range(self, start: int, end: int) -> None:
        self.start_time = start
        self.end_time = end

        logger.info(
            f"User {self.user_id} has updated notification time range:"
            f" {start} to {end}."
        )

        Session.commit()

    def get_humanized_n_range(self) -> str:
        hours_start: int = self.start_time // 60
        minutes_start: int = self.start_time % 60
        string_start: str = (
            f"{hours_start}.{minutes_start}"
            if minutes_start
            else f"{hours_start}"
        )

        hours_end: int = self.end_time // 60
        minutes_end: int = self.end_time % 60
        string_end: str = (
            f"{hours_end}.{minutes_end}" if minutes_end else f"{hours_end}"
        )

        return f"{string_start}-{string_end}"

    def update_notified_at(self) -> None:
        self.notified_at = datetime.utcnow()
        Session.commit()

    def update_frequency(self, frequency: int) -> None:
        old_frequency: int = self.frequency
        self.frequency = frequency

        logger.info(
            f"User {self.user_id} has updated notification frequency: "
            f"From {old_frequency} to {self.frequency}."
        )

        Session.commit()


def init_db():
    """Initialize DB tables"""
    if is_debug_enabled():
        logging.info("Database has been cleared")
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
    logging.info("Database has been initialized")
