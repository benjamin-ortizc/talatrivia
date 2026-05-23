from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionRead
from app.schemas.user import UserRead


class AnswerOptionPlay(BaseModel):
    """
    Contrato de la respuesta a la pregunta.
    Devuelve el texto de la posible respuesta, sin exponer si es correcta.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class QuestionPlay(BaseModel):
    """Contrato de la pregunta que verá el jugador, incluye AnswerOptionPlay"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    options: list[AnswerOptionPlay]


class TriviaCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    question_ids: list[int] = Field(min_length=1)
    participant_ids: list[int] = Field(min_length=1)


class TriviaParticipantRead(BaseModel):
    """Participante de una trivia con su estado de juego."""

    model_config = ConfigDict(from_attributes=True)

    user: UserRead
    score: int
    started_at: datetime | None
    completed_at: datetime | None


class TriviaSummary(BaseModel):
    """Resumen para listados (sin preguntas ni participantes detallados)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class TriviaRead(BaseModel):
    """Detalle completo con preguntas y participantes."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    questions: list[QuestionRead]
    participants: list[TriviaParticipantRead]


class TriviaForUser(BaseModel):
    """Trivia asignada a un usuario con su estado de juego."""

    model_config = ConfigDict(from_attributes=True)

    trivia: TriviaSummary
    score: int
    started_at: datetime | None
    completed_at: datetime | None


class TriviaPlay(BaseModel):
    """
    Contrato del endpoint de play. Devuelve las preguntas y opciones de una trivia ocultando
    información sensible acerca de las respuestas (dificultad y si es que la respuesta es correcta)
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    questions: list[QuestionPlay]
