from __future__ import annotations

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.deploy import router as deploy_router
from src.api.routes.downloads import router as downloads_router
from src.api.routes.generation import router as generation_router
from src.api.routes.projects import router as projects_router
from src.core.config import settings
from src.infrastructure.persistence.db import init_db

# ---------------------------------------------------------------------------
# Fix: WinError 10054 — no Windows o ProactorEventLoop do Python 3.8–3.11
# fecha conexões TCP de forma abrupta ao enviar respostas de erro.
# Forçar SelectorEventLoop elimina o traceback espúrio sem afetar performance.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Skill Forge API",
    version="0.2.0",
    description="Fábrica de SKILL.md e instruções de agente — Stefanini",
)

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
app.include_router(deploy_router, prefix="/api/generation", tags=["deploy"])


@app.on_event("startup")
def on_startup() -> None:
    init_db()

    # Validação antecipada: exibe aviso claro se credenciais SAI não estão configuradas.
    if not settings.sai_configured:
        logger.warning(
            "⚠️  SAI Library NÃO configurada. "
            "Copie .env.example para .env na raiz do projeto e preencha "
            "SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID. "
            "As requisições de geração retornarão HTTP 503 até a configuração ser feita."
        )
    else:
        logger.info("✅ SAI Library configurada. Template ID: %s", settings.SAI_LIBRARY_TEMPLATE_ID)

    logger.info("🚀 Skill Forge API iniciada | ENV=%s | origins=%s", settings.APP_ENV, settings.allowed_origins)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "sai_configured": settings.sai_configured,
        "env": settings.APP_ENV,
    }
