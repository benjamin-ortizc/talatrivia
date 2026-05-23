"""Test e2e del flujo completo"""


def test_flujo_completo(client, admin_user, player_user, admin_token, player_token):
    admin_auth = {"Authorization": f"Bearer {admin_token}"}
    player_auth = {"Authorization": f"Bearer {player_token}"}

    response = client.post(
        "/questions",
        headers=admin_auth,
        json={
            "text": "Cual es la fecha del dia de RRHH?",
            "difficulty": "easy",
            "options": [
                {"text": "20 de mayo", "is_correct": True},
                {"text": "18 de septiembre", "is_correct": False},
                {"text": "21 de mayo", "is_correct": False},
            ],
        },
    )
    assert response.status_code == 201
    question = response.json()
    question_id = question["id"]
    correct_option_id = next(o["id"] for o in question["options"] if o["is_correct"])

    response = client.post(
        "/trivias",
        headers=admin_auth,
        json={
            "name": "Trivia de prueba",
            "description": "Descripción de prueba",
            "question_ids": [question_id],
            "participant_ids": [player_user.id],
        },
    )
    assert response.status_code == 201
    trivia_id = response.json()["id"]

    response = client.get("/trivias/me", headers=player_auth)
    assert response.status_code == 200
    my_trivias = response.json()
    assert len(my_trivias) == 1
    assert my_trivias[0]["trivia"]["id"] == trivia_id
    assert my_trivias[0]["completed_at"] is None

    response = client.get(f"/trivias/{trivia_id}/play", headers=player_auth)
    assert response.status_code == 200
    play = response.json()
    assert play["id"] == trivia_id
    assert len(play["questions"]) == 1
    # difficulty e is_correct no deben filtrarse al player.
    assert "difficulty" not in play["questions"][0]
    for option in play["questions"][0]["options"]:
        assert "is_correct" not in option

    response = client.post(
        f"/trivias/{trivia_id}/submit",
        headers=player_auth,
        json={
            "answers": [
                {"question_id": question_id, "selected_option_id": correct_option_id},
            ],
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["score"] == 1
    assert result["completed_at"] is not None
    assert len(result["results"]) == 1
    assert result["results"][0]["question_id"] == question_id
    assert result["results"][0]["is_correct"] is True

    response = client.get(f"/trivias/{trivia_id}/ranking", headers=player_auth)
    assert response.status_code == 200
    ranking = response.json()
    assert len(ranking) == 1
    assert ranking[0]["user"]["id"] == player_user.id
    assert ranking[0]["score"] == 1
