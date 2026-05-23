import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models import (  # noqa: F401
    AnswerOption,
    Question,
    Trivia,
    TriviaParticipant,
    TriviaQuestion,
    User,
    UserAnswer,
)
from app.models.user import UserRole

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql+psycopg://{settings.db_user}:{settings.db_password}"
    f"@db-test:5432/{settings.db_name}_test",
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session) -> User:
    user = User(
        name="Admin Test",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def player_user(db_session) -> User:
    user = User(
        name="Player Test",
        email="player@test.com",
        password_hash=hash_password("player123"),
        role=UserRole.PLAYER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user) -> str:
    return create_access_token(subject=admin_user.id, role=admin_user.role)


@pytest.fixture
def player_token(player_user) -> str:
    return create_access_token(subject=player_user.id, role=player_user.role)


@pytest.fixture
def admin_client(client, admin_token) -> TestClient:
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client


@pytest.fixture
def player_client(client, player_token) -> TestClient:
    client.headers["Authorization"] = f"Bearer {player_token}"
    return client
