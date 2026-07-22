"""Pydantic schemas for Skill Forge API."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class AgentTarget(str, Enum):
    claude = "claude"
    copilot = "copilot"
    cursor = "cursor"
    vertex_ai = "vertex_ai"
    windsurf = "windsurf"
    generic_openai = "generic_openai"


class ConnectorType(str, Enum):
    file = "file"
    postgres = "postgres"
    mysql = "mysql"
    rest_api = "rest_api"
    graphql = "graphql"
    s3 = "s3"
    google_drive = "google_drive"
    repository = "repository"
    docs = "docs"


class ConnectionMetadata(BaseModel):
    """
    Connection metadata for a context material.

    Secrets (passwords, API keys, tokens) MUST be provided as references to
    environment variable names (e.g. ``{"password": "$env:DB_PASSWORD"}``),
    NOT as plain-text values. The backend validates this convention and never
    logs or stores resolved secret values.
    """

    host: str | None = Field(None, description="Host / URL for network connectors")
    port: int | None = Field(None, description="Port for network connectors")
    database: str | None = Field(None, description="Database / bucket / drive name")
    username: str | None = Field(None, description="Username (non-secret)")
    # Secrets are referenced by env-var name, e.g. "$env:DB_PASSWORD"
    password_env_ref: str | None = Field(
        None,
        description=(
            "Reference to the environment variable that holds the password, "
            "e.g. '$env:DB_PASSWORD'. Never supply the actual password here."
        ),
    )
    api_key_env_ref: str | None = Field(
        None,
        description=(
            "Reference to the environment variable that holds the API key, "
            "e.g. '$env:MY_API_KEY'."
        ),
    )
    # Generic extra fields (non-secret)
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("password_env_ref", "api_key_env_ref", mode="before")
    @classmethod
    def _must_be_env_ref(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("$env:"):
            raise ValueError(
                "Secret references must start with '$env:' "
                "(e.g. '$env:MY_SECRET'). Do not supply raw secrets."
            )
        return v


class ContextMaterial(BaseModel):
    """A single piece of context material supplied by the user."""

    connector_type: ConnectorType
    connection_metadata: ConnectionMetadata = Field(default_factory=ConnectionMetadata)
    description: str = Field(
        ...,
        min_length=10,
        description=(
            "Mandatory description of why this material matters and what the "
            "AI agent should extract from it."
        ),
    )


class GenerateRequest(BaseModel):
    """Request body for the /generate endpoint."""

    agent_target: AgentTarget = Field(
        ..., description="Target agent / IDE for which the artifacts are generated."
    )
    high_level_description: str = Field(
        ...,
        min_length=20,
        description="High-level description of the desired skill / artifact.",
    )
    context_materials: list[ContextMaterial] = Field(
        default_factory=list,
        description="List of context materials the agent should be aware of.",
    )


class ArtifactFile(BaseModel):
    """A single generated file inside the output ZIP."""

    path: str = Field(..., description="Relative path inside the ZIP archive.")
    content: str = Field(..., description="UTF-8 text content of the file.")


class GenerateResponse(BaseModel):
    """Response returned after artifact generation."""

    artifacts: list[ArtifactFile] = Field(
        ..., description="All generated files (also bundled in the ZIP)."
    )
    suggested_prompt: str = Field(
        ..., description="Ready-to-paste prompt for the target agent."
    )
    download_token: str = Field(
        ...,
        description=(
            "Opaque token used to download the ZIP via GET /api/v1/download/{token}."
        ),
    )


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class AgentInfo(BaseModel):
    id: AgentTarget
    display_name: str
    primary_artifact: str
    description: str
