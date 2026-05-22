from fastapi import FastAPI

from app.api.routes import auth, users, question
from app.config import settings

app = FastAPI(
    title="TalaTrivia API",
    description="API para crear/gestionar trivias de RRHH.",
    version="0.0.1",
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(question.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "debug": settings.debug}