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
    # Use _safe_zip_path to stay consistent with retrieve/delete validation
    base = tmp_dir.resolve()
    dest = (base / f"{token}.zip").resolve()
    dest.write_bytes(zip_bytes)
    logger.info("ZIP stored at %s (token=%s)", dest, token)
    return token


def _safe_zip_path(token: str) -> Path | None:
    """
    Build a safe filesystem path for *token*.

    Validates that *token* is a UUID4 string (limiting the character set) and
    confirms the resolved path is within ``settings.tmp_dir`` to prevent any
    path-traversal attack.  Returns ``None`` if either check fails.
    """
    try:
        safe_token = str(uuid.UUID(token, version=4))
    except ValueError:
        return None

    base = Path(settings.tmp_dir).resolve()
    candidate = (base / f"{safe_token}.zip").resolve()

    # Ensure the resolved path is strictly inside tmp_dir
    if base not in candidate.parents:
        logger.warning("Path-traversal attempt detected for token: %s", token)
        return None

    return candidate


def retrieve_zip(token: str) -> bytes | None:
    """
    Return the raw ZIP bytes for *token*, or ``None`` if not found.

    Validates that the token is a valid UUID4 to prevent path traversal.
    """
    path = _safe_zip_path(token)
    if path is None:
        logger.warning("Invalid token format: %s", token)
        return None
    if not path.exists():
        return None
    return path.read_bytes()


def delete_zip(token: str) -> bool:
    """Delete the ZIP for *token*; returns True if the file existed."""
    path = _safe_zip_path(token)
    if path is None:
        return False
    if path.exists():
        path.unlink()
        return True
    return False
