from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.scoring import points_for
from app.models.question import Question
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.models.user import User
from app.models.user_answer import UserAnswer
from app.schemas.trivia import TriviaCreate, TriviaSubmit


class QuestionsNotFoundError(Exception):
    def __init__(self, missing_ids: list[int]):
        self.missing_ids = missing_ids
        super().__init__(f"Preguntas no encontradas: {missing_ids}")


class ParticipantsNotFoundError(Exception):
    def __init__(self, missing_ids: list[int]):
        self.missing_ids = missing_ids
        super().__init__(f"Participantes no encontrados: {missing_ids}")


class TriviaNotFoundError(Exception):
    pass


class NotParticipantError(Exception):
    pass


class TriviaAlreadyCompletedError(Exception):
    pass


class TriviaNotStartedError(Exception):
    pass


class InvalidSubmitError(Exception):
    pass


def create_trivia(db: Session, trivia_data: TriviaCreate) -> Trivia:
    """Crea una trivia con sus preguntas y participantes asignados."""
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


def submit_trivia(
    db: Session,
    trivia_id: int,
    user_id: int,
    submit_data: TriviaSubmit,
) -> TriviaParticipant:
    """Encargado de procesar el envío de respuestas de un jugador y calcula el score"""
    participant = db.scalar(
        select(TriviaParticipant)
        .where(
            TriviaParticipant.trivia_id == trivia_id,
            TriviaParticipant.user_id == user_id,
        )
        .options(
            selectinload(TriviaParticipant.trivia)
            .selectinload(Trivia.questions)
            .selectinload(Question.options),
            selectinload(TriviaParticipant.answers),
        )
    )
    if participant is None:
        raise NotParticipantError(
            f"Usuario {user_id} no está asignado a la trivia {trivia_id}"
        )

    if participant.completed_at is not None:
        return participant

    if participant.started_at is None:
        raise TriviaNotStartedError(
            f"Usuario {user_id} no inició la trivia {trivia_id}"
        )

    trivia = participant.trivia
    _validate_submit(trivia, submit_data)

    answers_by_qid = {a.question_id: a for a in submit_data.answers}
    score = 0
    for question in trivia.questions:
        answer = answers_by_qid[question.id]
        correct_option_id = next(o.id for o in question.options if o.is_correct)
        is_correct = answer.selected_option_id == correct_option_id
        if is_correct:
            score += points_for(question.difficulty)
        participant.answers.append(
            UserAnswer(
                question_id=question.id,
                selected_option_id=answer.selected_option_id,
                is_correct=is_correct,
            )
        )

    participant.score = score
    participant.completed_at = datetime.now(timezone.utc)
    db.commit()
    return participant


def get_trivia_ranking(
    db: Session,
    trivia_id: int,
    user_id: int,
    is_admin: bool,
) -> list[TriviaParticipant]:
    """
    Devuelve el ranking de una trivia específica
    """
    trivia_exists = (
        db.scalar(select(Trivia.id).where(Trivia.id == trivia_id)) is not None
    )
    if not trivia_exists:
        raise TriviaNotFoundError(f"Trivia {trivia_id} no encontrada")

    if not is_admin:
        is_participant = (
            db.scalar(
                select(TriviaParticipant.id).where(
                    TriviaParticipant.trivia_id == trivia_id,
                    TriviaParticipant.user_id == user_id,
                )
            )
            is not None
        )
        if not is_participant:
            raise NotParticipantError(
                f"Usuario {user_id} no está asignado a la trivia {trivia_id}"
            )

    # Devuelve ordenado ASC el ranking de los usuarios que hayan
    # finalizado la trivia, se desempata con el que haya terminado primero.
    ranking = db.scalars(
        select(TriviaParticipant)
        .where(
            TriviaParticipant.trivia_id == trivia_id,
            TriviaParticipant.completed_at.is_not(None),
        )
        .order_by(
            TriviaParticipant.score.desc(),
            (TriviaParticipant.completed_at - TriviaParticipant.started_at).asc(),
        )
        .options(selectinload(TriviaParticipant.user))
    ).all()

    return list(ranking)


#
# Helpers privados
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


def _validate_submit(trivia: Trivia, submit_data: TriviaSubmit) -> None:
    """Valida que las answers cubran exactamente las preguntas de la trivia
    y que cada option seleccionada pertenezca a su pregunta."""
    options_by_question: dict[int, set[int]] = {
        q.id: {o.id for o in q.options} for q in trivia.questions
    }
    expected = set(options_by_question)
    submitted = {a.question_id for a in submit_data.answers}

    if submitted != expected:
        raise InvalidSubmitError(
            "El set de preguntas enviadas no coincide con las preguntas de la trivia"
        )

    for a in submit_data.answers:
        if a.selected_option_id not in options_by_question[a.question_id]:
            raise InvalidSubmitError(
                f"La opción {a.selected_option_id} no pertenece a la pregunta {a.question_id}"
            )
