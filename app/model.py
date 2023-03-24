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
)
from typing_extensions import Self

from app.config import is_debug_enabled


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
    name: Mapped[str] = mapped_column(types.String, nullable=False, unique=True)
    fullname: Mapped[Optional[str]]
    weight: Mapped[int]
    climate: Mapped[str]
    activity: Mapped[str]

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"

    @classmethod
    def get(cls, user_reference: Optional[str]) -> Optional[Self]:
        query = Session.query(cls).autoflush(False)
        query = query.filter(cls.id == user_reference)
        return query.first()


class Drinks(Base):
    __tablename__ = "drinks"

    id: Mapped[str] = mapped_column(
        types.Text(length=36), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    timestamp: Mapped[datetime] = mapped_column(types.DateTime, nullable=False)
    amount: Mapped[int] = mapped_column(types.Integer, nullable=False)


def init_db():
    """Initialize DB tables"""
    if is_debug_enabled():
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
