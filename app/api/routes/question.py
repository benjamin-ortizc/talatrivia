from fastapi import APIRouter
from starlette import status

from app.api.deps import AdminUser, DbSession
from app.models import Question
from app.schemas.question import QuestionCreate, QuestionRead
from app.services import question as question_service

router = APIRouter(prefix="/questions", tags=["Preguntas"])


@router.post("", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
def create_question(
    question_data: QuestionCreate,
    admin: AdminUser,
    db: DbSession,
) -> Question:
    """Endpoint que permite crear una nueva question, junto con sus respuestas"""
    return question_service.create_question(db, question_data)


@router.get("", response_model=list[QuestionRead])
def list_questions(admin: AdminUser, db: DbSession) -> list[Question]:
    """Endpoint que lista las questions de la aplicación"""
    return question_service.list_questions(db)
