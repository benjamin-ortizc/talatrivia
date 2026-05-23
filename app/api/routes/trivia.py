from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.models import TriviaParticipant
from app.models.trivia import Trivia
from app.models.user import UserRole
from app.schemas.trivia import (
    RankingItem,
    TriviaCreate,
    TriviaForUser,
    TriviaPlay,
    TriviaRead,
    TriviaSubmit,
    TriviaSubmitResult,
    TriviaSummary,
)
from app.services import trivia as trivia_service

router = APIRouter(prefix="/trivias", tags=["Trivias"])


@router.post(
    "",
    response_model=TriviaRead,
    status_code=status.HTTP_201_CREATED,
)
def create_trivia(
    trivia_data: TriviaCreate,
    admin: AdminUser,
    db: DbSession,
) -> Trivia:
    """Crea una trivia con preguntas y participantes asignados"""
    try:
        return trivia_service.create_trivia(db, trivia_data)
    except trivia_service.QuestionsNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Preguntas no encontradas: {e.missing_ids}",
        )
    except trivia_service.ParticipantsNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Usuarios no encontrados: {e.missing_ids}",
        )


@router.get("", response_model=list[TriviaSummary])
def list_trivias(
    admin: AdminUser,
    db: DbSession,
) -> list[Trivia]:
    """Lista todas las trivias del sistema"""
    return trivia_service.list_trivias(db)


@router.get("/me", response_model=list[TriviaForUser])
def list_my_trivias(
    current_user: CurrentUser,
    db: DbSession,
) -> list[TriviaParticipant]:
    """Lista las trivias asignadas al usuario autenticado con su estado de juego"""
    return trivia_service.list_trivias_by_user(db, current_user.id)


@router.get("/{trivia_id}", response_model=TriviaRead)
def get_trivia(
    trivia_id: int,
    admin: AdminUser,
    db: DbSession,
) -> Trivia:
    """Obtiene el detalle completo de una trivia específica"""
    try:
        return trivia_service.get_trivia(db, trivia_id)
    except trivia_service.TriviaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia {trivia_id} no encontrada",
        )


@router.get("/{trivia_id}/play", response_model=TriviaPlay)
def play_trivia(
    trivia_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> Trivia:
    """Obtiene las preguntas y posibles respuestas al usuario, sin exponer datos sensibles"""
    try:
        return trivia_service.play_trivia(db, trivia_id, current_user.id)
    except trivia_service.TriviaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia {trivia_id} no encontrada",
        )
    except trivia_service.NotParticipantError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )
    except trivia_service.TriviaAlreadyCompletedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya completaste esta trivia",
        )


@router.post("/{trivia_id}/submit", response_model=TriviaSubmitResult)
def submit_trivia(
    trivia_id: int,
    submit_data: TriviaSubmit,
    current_user: CurrentUser,
    db: DbSession,
) -> TriviaParticipant:
    """Envía las respuestas del jugador y devuelve el resultado"""
    try:
        return trivia_service.submit_trivia(db, trivia_id, current_user.id, submit_data)
    except trivia_service.NotParticipantError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )
    except trivia_service.TriviaNotStartedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aún no has iniciado la trivia",
        )
    except trivia_service.InvalidSubmitError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{trivia_id}/ranking", response_model=list[RankingItem])
def get_trivia_ranking(
    trivia_id: int,
    current_user: CurrentUser,
    db: DbSession,
) -> list[TriviaParticipant]:
    """
    Devuelve el ranking de la trivia especificada.
    """
    is_admin = current_user.role == UserRole.ADMIN.value
    try:
        return trivia_service.get_trivia_ranking(
            db, trivia_id, current_user.id, is_admin
        )
    except trivia_service.TriviaNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trivia {trivia_id} no encontrada",
        )
    except trivia_service.NotParticipantError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )
