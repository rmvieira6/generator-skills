from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.downloads import router as downloads_router
from src.api.routes.generation import router as generation_router
from src.api.routes.projects import router as projects_router
from src.core.config import settings
from src.infrastructure.persistence.db import init_db

app = FastAPI(title="Skill Forge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(generation_router, prefix="/api/generation", tags=["generation"])
app.include_router(downloads_router, prefix="/api/downloads", tags=["downloads"])


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
