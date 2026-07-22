"""Generation router – POST /api/v1/generate and GET /api/v1/download/{token}."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.models.schemas import (
    AgentInfo,
    AgentTarget,
    GenerateRequest,
    GenerateResponse,
)
from app.services.generator import AGENT_META, generate_artifacts
from app.services.llm import LLMClient, get_llm_client
from app.services.packager import build_zip, retrieve_zip, store_zip

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["generation"])


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------


def _llm_client() -> LLMClient:
    try:
        return get_llm_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/agents", response_model=list[AgentInfo], summary="List supported agents")
async def list_agents() -> list[AgentInfo]:
    """Return metadata for all supported target agents."""
    return [
        AgentInfo(
            id=agent_id,
            display_name=meta["display_name"],
            primary_artifact=meta["primary_file"],
            description=meta["readme_note"],
        )
        for agent_id, meta in AGENT_META.items()
    ]


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate skill artifacts",
    status_code=200,
)
async def generate(
    request: GenerateRequest,
    llm: LLMClient = Depends(_llm_client),
) -> GenerateResponse:
    """
    Generate context artifacts (SKILL.md, .cursorrules, etc.) for the chosen
    AI agent target, package them as a ZIP, and return a download token.
    """
    try:
        artifacts, suggested_prompt = await generate_artifacts(request, llm)
    except Exception as exc:
        logger.exception("Artifact generation failed")
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    zip_bytes = build_zip(artifacts)
    token = store_zip(zip_bytes)

    return GenerateResponse(
        artifacts=artifacts,
        suggested_prompt=suggested_prompt,
        download_token=token,
    )


@router.get(
    "/download/{token}",
    summary="Download generated ZIP",
    responses={
        200: {
            "content": {"application/zip": {}},
            "description": "ZIP archive containing all generated artifacts.",
        },
        404: {"description": "Token not found or expired."},
    },
)
async def download(token: str) -> Response:
    """Download the ZIP archive previously generated for *token*."""
    zip_bytes = retrieve_zip(token)
    if zip_bytes is None:
        raise HTTPException(status_code=404, detail="Token not found or expired.")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="skill-forge-{token[:8]}.zip"'},
    )
