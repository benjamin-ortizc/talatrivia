from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.trivia import Trivia
    from app.models.question import Question

class TriviaQuestion(Base):
    __tablename__ = "trivia_questions"

    trivia_id: Mapped[int] = mapped_column(
        ForeignKey("trivias.id", ondelete="CASCADE"),
        primary_key=True,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    trivia: Mapped["Trivia"] = relationship(back_populates="trivia_questions")
    question: Mapped["Question"] = relationship()