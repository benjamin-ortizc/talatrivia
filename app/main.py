from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="TalaTrivia API",
    description="API para crear/gestionar trivias de RRHH.",
    version="0.0.1",
)

@app.get("/health")
def health_check():
    return {"status": "ok", "debug": settings.debug}