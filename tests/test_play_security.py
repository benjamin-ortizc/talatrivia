"""GET /trivias/{id}/play no debe exponer is_correct ni difficulty."""

from app.models.answer_option import AnswerOption
from app.models.question import Question, QuestionDifficulty
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion


def test_play_oculta_campos_sensibles(player_client, player_user, db_session):
    # Una pregunta por dificultad para cubrir todas las variantes.
    trivia = Trivia(name="Security check", description=None)
    for difficulty in QuestionDifficulty:
        question = Question(
            text=f"Pregunta {difficulty.value}", difficulty=difficulty.value
        )
        question.options.append(AnswerOption(text="correcta", is_correct=True))
        question.options.append(AnswerOption(text="incorrecta 1", is_correct=False))
        question.options.append(AnswerOption(text="incorrecta 2", is_correct=False))
        db_session.add(question)
        db_session.flush()
        trivia.trivia_questions.append(TriviaQuestion(question_id=question.id))

    trivia.participants.append(TriviaParticipant(user_id=player_user.id))
    db_session.add(trivia)
    db_session.commit()
    db_session.refresh(trivia)

    response = player_client.get(f"/trivias/{trivia.id}/play")
    assert response.status_code == 200

    play = response.json()
    assert len(play["questions"]) == 3

    for question in play["questions"]:
        assert "difficulty" not in question
        for option in question["options"]:
            assert "is_correct" not in option
