from datetime import datetime

from sqlmodel import Field, SQLModel


class GenerationJobRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    request_hash: str = Field(index=True, nullable=False, max_length=128)
    project_hash: str = Field(index=True, nullable=False, max_length=128)
    materials_hash: str = Field(index=True, nullable=False, max_length=128)
    target_agent: str = Field(index=True, nullable=False, max_length=80)

    summary: str = Field(default="", nullable=False)
    artifact_index: str = Field(default="", nullable=False)
