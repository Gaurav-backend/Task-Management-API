from datetime import datetime, UTC
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column , relationship
from app.database.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    owner_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False,
    )

    owner = relationship(
    "User",
    back_populates="tasks",
    )