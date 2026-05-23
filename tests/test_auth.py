"""Tests de errores en register y login."""


def test_register_email_duplicado(client):
    payload = {
        "name": "Duplicado",
        "email": "dupe@test.com",
        "password": "password123",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "registrado" in response.json()["detail"].lower()


def test_login_ok(client, player_user):
    response = client.post(
        "/auth/login",
        json={"email": player_user.email, "password": "player123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["access_token"]


def test_login_password_invalido(client, player_user):
    response = client.post(
        "/auth/login",
        json={"email": player_user.email, "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email o password inválidos"


def test_login_email_inexistente(client):
    # Mismo mensaje que password inválido para evitar user enumeration.
    response = client.post(
        "/auth/login",
        json={"email": "noexiste@test.com", "password": "asd123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email o password inválidos"


def test_register_ignora_rol(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Intento Admin",
            "email": "fake-admin@test.com",
            "password": "password123",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "player"
