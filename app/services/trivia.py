from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.question import Question
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.models.user import User
from app.schemas.trivia import TriviaCreate


class QuestionsNotFoundError(Exception):
    """Error handler cuando uno o más questions_id no se encuentran en la DB"""

    def __init__(self, missing_ids: list[int]):
        self.missing_ids = missing_ids
        super().__init__(f"Preguntas no encontradas: {missing_ids}")


class ParticipantsNotFoundError(Exception):
    """Error handler cuando uno o más participant_id no se encuentran en la DB"""

    def __init__(self, missing_ids: list[int]):
        self.missing_ids = missing_ids
        super().__init__(f"Participantes no encontrados: {missing_ids}")


class TriviaNotFoundError(Exception):
    """Error handler cuando no se encuentra la trivia en la DB"""

    pass


class NotParticipantError(Exception):
    """Error handler cuando el usuario no está asignado como participante de la trivia"""

    pass


class TriviaAlreadyCompletedError(Exception):
    """Error handler cuando el usuario ya completó la trivia y no puede volver a jugarla"""

    pass


def create_trivia(db: Session, trivia_data: TriviaCreate) -> Trivia:
    """
    Crea una trivia con sus preguntas y participantes asignados.
    """
    _validate_questions_exist(db, trivia_data.question_ids)
    _validate_participants_exist(db, trivia_data.participant_ids)

    trivia = Trivia(
        name=trivia_data.name,
        description=trivia_data.description,
    )

    for question_id in trivia_data.question_ids:
        tq = TriviaQuestion(question_id=question_id)
        trivia.trivia_questions.append(tq)

    for user_id in trivia_data.participant_ids:
        tp = TriviaParticipant(user_id=user_id)
        trivia.participants.append(tp)

    db.add(trivia)
    db.commit()
    db.refresh(trivia)
    return trivia


def list_trivias(db: Session) -> list[Trivia]:
    """Lista todas las trivias del sistema."""
    trivias = db.scalars(select(Trivia)).all()
    return list(trivias)


def get_trivia(db: Session, trivia_id: int) -> Trivia:
    """Obtiene una trivia por ID específica, si no existe, lanzamos TriviaNotFoundError"""
    trivia = db.scalar(select(Trivia).where(Trivia.id == trivia_id))
    if trivia is None:
        raise TriviaNotFoundError(f"Trivia {trivia_id} no encontrada")
    return trivia


def list_trivias_by_user(db: Session, user_id: int) -> list[TriviaParticipant]:
    participation = db.scalars(
        select(TriviaParticipant).where(TriviaParticipant.user_id == user_id)
    ).all()
    return list(participation)


def play_trivia(db: Session, trivia_id: int, user_id: int) -> Trivia:
    """Comienza a jugar la trivia, y le entrega las preguntas a responder"""

    # Preload de relaciones para evitar N+1
    trivia = db.scalar(
        select(Trivia)
        .where(Trivia.id == trivia_id)
        .options(selectinload(Trivia.questions).selectinload(Question.options))
    )
    if trivia is None:
        raise TriviaNotFoundError(f"Trivia {trivia_id} no encontrada")

    participant = db.scalar(
        select(TriviaParticipant).where(
            TriviaParticipant.trivia_id == trivia_id,
            TriviaParticipant.user_id == user_id,
        )
    )
    if participant is None:
        raise NotParticipantError(
            f"Usuario {user_id} no está asignado a la trivia {trivia_id}"
        )

    if participant.completed_at is not None:
        raise TriviaAlreadyCompletedError(
            f"Usuario {user_id} ya completó su participación en la trivia {trivia_id}"
        )

    # Si es la primera vez que entra a jugar, marcamos el inicio
    if participant.started_at is None:
        participant.started_at = datetime.now(timezone.utc)
        db.commit()

    return trivia


#
# Helpers privados de validación previa al commit en DB
#
def _validate_questions_exist(db: Session, question_ids: list[int]) -> None:
    """Validamos que todas las preguntas existan, si no lanzamos QuestionsNotFoundError"""
    existing_ids = db.scalars(
        select(Question.id).where(Question.id.in_(question_ids))
    ).all()
    missing = set(question_ids) - set(existing_ids)
    if missing:
        raise QuestionsNotFoundError(sorted(missing))


def _validate_participants_exist(db: Session, participant_ids: list[int]) -> None:
    """Validamos que todos los participantes existan, si no lanzamos ParticipantsNotFoundError"""
    existing_ids = db.scalars(select(User.id).where(User.id.in_(participant_ids))).all()
    missing = set(participant_ids) - set(existing_ids)
    if missing:
        raise ParticipantsNotFoundError(sorted(missing))
