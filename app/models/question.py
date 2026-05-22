from typing import TYPE_CHECKING

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Usamos esta solución para evitar ignorar warnings,
# debido a que solo muestra un type error, pero no falla en runtime.
if TYPE_CHECKING:
    from app.models.answer_option import AnswerOption

class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    options: Mapped[list["AnswerOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )