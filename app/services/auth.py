from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, user_data: UserCreate) -> User:
    """Registra a un nuevo usuario, utilizando el contrato de UserCreate"""
    existing = db.scalar(select(User).where(User.email == user_data.email))

    if existing is not None:
        raise EmailAlreadyRegisteredError("Email ya registrado")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=UserRole.PLAYER.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> str:
    """
    Recibe las credenciales y valida autenticación del usuario,
    entrega access JWT token al cliente
    """
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        raise InvalidCredentialsError("Email o password inválidos")

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Email o password inválidos")

    return create_access_token(subject=user.id, role=user.role)
