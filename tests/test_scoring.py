"""Unit tests del módulo de scoring."""

import pytest

from app.core.scoring import points_for
from app.models.question import QuestionDifficulty


@pytest.mark.parametrize(
    "difficulty,expected_points",
    [
        (QuestionDifficulty.EASY.value, 1),
        (QuestionDifficulty.MEDIUM.value, 2),
        (QuestionDifficulty.HARD.value, 3),
    ],
)
def test_points_for(difficulty, expected_points):
    assert points_for(difficulty) == expected_points


def test_dificultad_invalida():
    with pytest.raises(KeyError):
        points_for("imposible")
