from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(user_data: UserCreate, db: DbSession) -> User:
    """Endpoint encargado de manejar el registro de un usuario"""
    try:
        user = auth_service.register_user(db, user_data)
    except auth_service.EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado",
        )
    return user


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: DbSession) -> TokenResponse:
    """Endpoint encargado de manejar el inicio de sesión de un usuario"""
    try:
        token = auth_service.authenticate_user(
            db,
            email=credentials.email,
            password=credentials.password,
        )
    except auth_service.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o password inválidos",
        )
    return TokenResponse(access_token=token)
