from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from src.infrastructure.persistence.artifact_store import artifact_store

router = APIRouter()


@router.get("/{token}")
def download(token: str) -> Response:
    payload = artifact_store.get(token)
    if payload is None:
        raise HTTPException(status_code=404, detail="Download token not found or expired")

    return Response(
        content=payload,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=skill-forge-artifacts.zip"},
    )
