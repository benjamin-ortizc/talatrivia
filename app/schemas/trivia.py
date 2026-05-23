from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.question import QuestionRead
from app.schemas.user import UserRead


class AnswerOptionPlay(BaseModel):
    """
    Modelo de datos de la respuesta a la pregunta.
    Devuelve el texto de la posible respuesta, sin exponer si es correcta.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str


class QuestionPlay(BaseModel):
    """Modelo de datos de la pregunta que verá el jugador, incluye AnswerOptionPlay"""

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
    Modelo de datos del endpoint de play. Devuelve las preguntas y opciones de una trivia ocultando
    información sensible acerca de las respuestas (dificultad y si es que la respuesta es correcta)
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    questions: list[QuestionPlay]


class AnswerSubmit(BaseModel):
    """Una respuesta enviada por el jugador para una pregunta de la trivia."""

    question_id: int
    selected_option_id: int


class TriviaSubmit(BaseModel):
    """Modelo de datos del endpoint de submit. Debe incluir solo una respuesta por cada pregunta."""

    answers: list[AnswerSubmit] = Field(min_length=1)

    @model_validator(mode="after")
    def no_duplicate_questions(self) -> "TriviaSubmit":
        question_ids = [a.question_id for a in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError(
                "No se pueden enviar respuestas duplicadas para la misma pregunta"
            )
        return self


class QuestionResult(BaseModel):
    """Resultado individual de una pregunta, utilizado como un set en TriviaSubmitResult"""

    model_config = ConfigDict(from_attributes=True)

    question_id: int
    is_correct: bool


class TriviaSubmitResult(BaseModel):
    """Resultado del submit de la trivia"""

    model_config = ConfigDict(from_attributes=True)

    score: int
    completed_at: datetime
    results: list[QuestionResult] = Field(validation_alias="answers")


class RankingUser(BaseModel):
    """Datos mínimos del usuario para el ranking, sin exponer email, role ni created_at."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RankingItem(BaseModel):
    """Una entrada del ranking de una trivia"""

    model_config = ConfigDict(from_attributes=True)

    user: RankingUser
    score: int
