from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: CurrentUser) -> User:
    """Obtiene los datos del usuario actual autenticado"""
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(admin: AdminUser, db: DbSession) -> list[User]:
    """Obtiene los datos de todos los usuarios (admin-only)"""
    users = db.scalars(select(User)).all()
    return list(users)
