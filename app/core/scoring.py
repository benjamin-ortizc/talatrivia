from app.models.question import QuestionDifficulty

DIFFICULTY_POINTS: dict[str, int] = {
    QuestionDifficulty.EASY.value: 1,
    QuestionDifficulty.MEDIUM.value: 2,
    QuestionDifficulty.HARD.value: 3,
}


def points_for(difficulty: str) -> int:
    return DIFFICULTY_POINTS[difficulty]
