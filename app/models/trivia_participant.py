from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.trivia import Trivia
    from app.models.user import User
    from app.models.user_answer import UserAnswer


class TriviaParticipant(Base):
    __tablename__ = "trivia_participants"
    __table_args__ = (
        UniqueConstraint("trivia_id", "user_id", name="uq_trivia_participant"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    trivia_id: Mapped[int] = mapped_column(ForeignKey("trivias.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    trivia: Mapped["Trivia"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
    answers: Mapped[list["UserAnswer"]] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
    )
