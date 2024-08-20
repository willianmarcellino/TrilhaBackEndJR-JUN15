from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class LabelModel(Base):
    __tablename__ = 'labels'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
    )


class TaskStates(StrEnum):
    PENDING = 'pending'
    DOING = 'doing'
    DONE = 'done'
    EXPIRED = 'expired'


class TaskModel(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[TaskStates] = mapped_column(nullable=False)
    label: Mapped[LabelModel] = relationship()
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    label_id: Mapped[int | None] = mapped_column(
        ForeignKey('labels.id', ondelete='SET NULL'), nullable=True
    )
