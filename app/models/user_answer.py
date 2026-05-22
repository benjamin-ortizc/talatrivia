from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.trivia_participant import TriviaParticipant
    from app.models.question import Question
    from app.models.answer_option import AnswerOption

class UserAnswer(Base):
    __tablename__ = "user_answers"
    __table_args__ = (
        UniqueConstraint("participant_id", "question_id", name="uq_user_answer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("trivia_participants.id", ondelete="CASCADE")
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    selected_option_id: Mapped[int] = mapped_column(
        ForeignKey("answer_options.id", ondelete="CASCADE")
    )
    is_correct: Mapped[bool] = mapped_column(Boolean)

    participant: Mapped["TriviaParticipant"] = relationship(back_populates="answers")
    question: Mapped["Question"] = relationship()
    selected_option: Mapped["AnswerOption"] = relationship()