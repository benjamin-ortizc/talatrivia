"""Tests de permisos y autenticación en endpoints protegidos."""

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/users",
        "/questions",
        "/trivias",
        "/trivias/1",
    ],
)
def test_get_admin_only(player_client, path):
    response = player_client.get(path)
    assert response.status_code == 403


def test_post_questions_admin_only(player_client):
    response = player_client.post(
        "/questions",
        json={
            "text": "test",
            "difficulty": "easy",
            "options": [
                {"text": "a", "is_correct": True},
                {"text": "b", "is_correct": False},
            ],
        },
    )
    assert response.status_code == 403


def test_post_trivias_admin_only(player_client):
    response = player_client.post(
        "/trivias",
        json={
            "name": "no debería poder",
            "question_ids": [1],
            "participant_ids": [1],
        },
    )
    assert response.status_code == 403


def test_sin_token(client):
    response = client.get("/users/me")
    assert response.status_code == 403


def test_token_invalido(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert response.status_code == 401
