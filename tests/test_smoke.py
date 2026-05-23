"""Smoke tests del setup de test."""

from sqlalchemy import select


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_persiste_usuario(client, db_session):
    from app.models import User

    response = client.post(
        "/auth/register",
        json={
            "name": "Smoke Test",
            "email": "smoke@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    user = db_session.scalar(select(User).where(User.email == "smoke@test.com"))
    assert user is not None
    assert user.name == "Smoke Test"
