from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer_option import AnswerOption
from app.models.question import Question
from app.schemas.question import QuestionCreate


def create_question(db: Session, question_data: QuestionCreate) -> Question:
    """
    Crea una pregunta con sus opciones de respuesta.
    Las validaciones son manejadas por el schema
    """
    question = Question(
        text=question_data.text,
        difficulty=question_data.difficulty.value,
    )

    for option_data in question_data.options:
        option = AnswerOption(
            text=option_data.text,
            is_correct=option_data.is_correct,
        )
        question.options.append(option)

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def list_questions(db: Session) -> list[Question]:
    """Lista todas las preguntas del sistema con sus opciones."""
    questions = db.scalars(select(Question)).all()
    return list(questions)
