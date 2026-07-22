from enum import Enum

from pydantic import BaseModel, Field


class TargetAgent(str, Enum):
    CLAUDE = "claude"
    COPILOT = "copilot"
    CURSOR = "cursor"
    VERTEX_AI = "vertex_ai"
    WINDSURF = "windsurf"
    GENERIC_OPENAI = "generic_openai"
    FABRIC_PYSPARK_NOTEBOOK = "fabric_pyspark_notebook"


class ConnectorType(str, Enum):
    LOCAL_FILE = "local_file"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REST_API = "rest_api"
    GRAPHQL_API = "graphql_api"
    OBJECT_STORAGE = "object_storage"
    GOOGLE_DRIVE = "google_drive"
    NOTION = "notion"
    CONFLUENCE = "confluence"
    GIT_REPOSITORY = "git_repository"


class Material(BaseModel):
    connector_type: ConnectorType
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1200)
    connection_metadata: dict[str, str | int | bool | None] = Field(default_factory=dict)


class Project(BaseModel):
    skill_name: str = Field(min_length=2, max_length=120)
    objective: str = Field(min_length=10, max_length=500)
    domain: str = Field(default="general", min_length=2, max_length=80)
    autonomy_level: str = Field(default="suggest_only", min_length=3, max_length=80)
    constraints: str = Field(default="", max_length=2000)
    high_level_description: str = Field(min_length=20, max_length=5000)
    target_agents: list[TargetAgent] = Field(min_length=1)


class GeneratedFile(BaseModel):
    path: str
    content: str


class GenerationResult(BaseModel):
    files: list[GeneratedFile]
    preview_markdown: str
    suggested_prompt: str
    used_cached_job: bool = False


class GenerationJob(BaseModel):
    id: int
    request_hash: str
    project_hash: str
    materials_hash: str
    target_agent: TargetAgent
    summary: str
    artifact_index: str
