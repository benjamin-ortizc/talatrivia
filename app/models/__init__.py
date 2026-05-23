from app.models.answer_option import AnswerOption
from app.models.question import Question
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.models.user import User
from app.models.user_answer import UserAnswer

# Usamos __all__ sólo para ser explícitos sobre lo que exporta el módulo,
# aunque no es un requerimiento mandatorio.
__all__ = [
    "User",
    "Question",
    "AnswerOption",
    "Trivia",
    "TriviaQuestion",
    "TriviaParticipant",
    "UserAnswer",
]
