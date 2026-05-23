from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import auth, question, trivia, users
from app.config import settings
from app.core.ratelimit import limiter

app = FastAPI(
    title="TalaTrivia API",
    description="API para crear/gestionar trivias de RRHH.",
    version="0.0.1",
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(question.router)
app.include_router(trivia.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "debug": settings.debug}
