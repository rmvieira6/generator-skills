from pydantic import BaseModel, Field

from src.domain.entities import ConnectorType, TargetAgent


class MaterialInput(BaseModel):
    connector_type: ConnectorType
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1200)
    connection_metadata: dict[str, str | int | bool | None] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    skill_name: str = Field(min_length=2, max_length=120)
    objective: str = Field(min_length=10, max_length=500)
    domain: str = Field(default="general", min_length=2, max_length=80)
    autonomy_level: str = Field(default="suggest_only", min_length=3, max_length=80)
    constraints: str = Field(default="", max_length=2000)
    high_level_description: str = Field(min_length=20, max_length=5000)
    target_agents: list[TargetAgent] = Field(min_length=1)
    materials: list[MaterialInput] = Field(default_factory=list)


class GenerateItemResponse(BaseModel):
    target_agent: TargetAgent
    preview_markdown: str
    suggested_prompt: str
    used_cached_job: bool
    download_token: str
    generated_files: list[str]


class GenerateResponse(BaseModel):
    items: list[GenerateItemResponse]


class ConnectionTestRequest(BaseModel):
    connector_type: ConnectorType
    connection_metadata: dict[str, str | int | bool | None] = Field(default_factory=dict)


class ConnectionTestResponse(BaseModel):
    ok: bool
    detail: str
