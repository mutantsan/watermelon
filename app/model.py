from typing import Optional

from sqlalchemy import String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    scoped_session,
)
from typing_extensions import Self


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
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
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


def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
