"""
ZIP packager service.

Creates an in-memory ZIP archive from a list of ArtifactFile objects and
stores it temporarily on disk with an opaque token.  The token is returned to
the client, who then calls GET /api/v1/download/{token} to retrieve the file.

Tokens are UUID4 strings; the files are stored under ``settings.tmp_dir`` and
are cleaned up on server restart (they are ephemeral by design).
"""

from __future__ import annotations

import io
import logging
import os
import uuid
import zipfile
from pathlib import Path

from app.config import settings
from app.models.schemas import ArtifactFile

logger = logging.getLogger(__name__)


def _ensure_tmp_dir() -> Path:
    path = Path(settings.tmp_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_zip(artifacts: list[ArtifactFile]) -> bytes:
    """Return the raw bytes of a ZIP archive containing all artifacts."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for artifact in artifacts:
            zf.writestr(artifact.path, artifact.content)
    return buf.getvalue()


def store_zip(zip_bytes: bytes) -> str:
    """
    Persist *zip_bytes* to ``settings.tmp_dir`` and return an opaque token.

    The filename on disk is ``{token}.zip``.
    """
    token = str(uuid.uuid4())
    tmp_dir = _ensure_tmp_dir()
    dest = tmp_dir / f"{token}.zip"
    dest.write_bytes(zip_bytes)
    logger.info("ZIP stored at %s (token=%s)", dest, token)
    return token


def retrieve_zip(token: str) -> bytes | None:
    """
    Return the raw ZIP bytes for *token*, or ``None`` if not found.

    Validates that the token is a valid UUID4 to prevent path traversal.
    """
    try:
        uuid.UUID(token, version=4)
    except ValueError:
        logger.warning("Invalid token format: %s", token)
        return None

    path = Path(settings.tmp_dir) / f"{token}.zip"
    if not path.exists():
        return None
    return path.read_bytes()


def delete_zip(token: str) -> bool:
    """Delete the ZIP for *token*; returns True if the file existed."""
    try:
        uuid.UUID(token, version=4)
    except ValueError:
        return False
    path = Path(settings.tmp_dir) / f"{token}.zip"
    if path.exists():
        path.unlink()
        return True
    return False
