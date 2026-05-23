from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.trivia_participant import TriviaParticipant
    from app.models.trivia_question import TriviaQuestion


class Trivia(Base):
    __tablename__ = "trivias"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    trivia_questions: Mapped[list["TriviaQuestion"]] = relationship(
        back_populates="trivia",
        cascade="all, delete-orphan",
    )
    participants: Mapped[list["TriviaParticipant"]] = relationship(
        back_populates="trivia",
        cascade="all, delete-orphan",
    )
