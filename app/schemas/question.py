from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.question import QuestionDifficulty


class AnswerOptionCreate(BaseModel):
    text: str = Field(min_length=1)
    is_correct: bool


class AnswerOptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    difficulty: QuestionDifficulty
    options: list[AnswerOptionCreate] = Field(min_length=2)

    # Validamos que exista al menos una respuesta correcta antes de crear Question
    @model_validator(mode="after")
    def validate_one_correct_option(self) -> "QuestionCreate":
        correct_count = sum(1 for opt in self.options if opt.is_correct)
        if correct_count != 1:
            raise ValueError(
                f"Debe haber exactamente una opción correcta, se encontraron {correct_count}"
            )
        return self


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    difficulty: QuestionDifficulty
    options: list[AnswerOptionRead]
    created_at: datetime
