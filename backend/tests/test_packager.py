"""Tests for the packager service."""

from __future__ import annotations

import io
import zipfile

import pytest

from app.models.schemas import ArtifactFile
from app.services.packager import build_zip, delete_zip, retrieve_zip, store_zip


def _make_artifacts() -> list[ArtifactFile]:
    return [
        ArtifactFile(path="SKILL.md", content="# Skill\n\nContent here."),
        ArtifactFile(path="README.md", content="# README\n\nUsage instructions."),
    ]


def test_build_zip_contains_all_files() -> None:
    artifacts = _make_artifacts()
    raw = build_zip(artifacts)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    assert set(zf.namelist()) == {"SKILL.md", "README.md"}
    assert zf.read("SKILL.md") == b"# Skill\n\nContent here."


def test_build_zip_nested_path() -> None:
    artifacts = [ArtifactFile(path=".github/copilot-instructions.md", content="# Copilot")]
    raw = build_zip(artifacts)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    assert ".github/copilot-instructions.md" in zf.namelist()


def test_store_and_retrieve_zip() -> None:
    artifacts = _make_artifacts()
    raw = build_zip(artifacts)
    token = store_zip(raw)
    assert len(token) == 36  # UUID4 string

    retrieved = retrieve_zip(token)
    assert retrieved == raw


def test_retrieve_unknown_token_returns_none() -> None:
    import uuid
    token = str(uuid.uuid4())
    assert retrieve_zip(token) is None


def test_retrieve_invalid_token_returns_none() -> None:
    assert retrieve_zip("../../etc/passwd") is None
    assert retrieve_zip("not-a-uuid") is None


def test_delete_zip() -> None:
    raw = build_zip(_make_artifacts())
    token = store_zip(raw)
    assert retrieve_zip(token) is not None
    deleted = delete_zip(token)
    assert deleted is True
    assert retrieve_zip(token) is None


def test_delete_nonexistent_token() -> None:
    import uuid
    assert delete_zip(str(uuid.uuid4())) is False
