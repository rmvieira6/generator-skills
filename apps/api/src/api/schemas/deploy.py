from pydantic import BaseModel, Field

from src.domain.entities import TargetAgent


class DeployRequest(BaseModel):
    download_token: str = Field(description="Token retornado pelo endpoint /generate.")
    target_agent: TargetAgent = Field(description="Agente para o qual os artefatos foram gerados.")
    project_path: str = Field(
        min_length=2,
        max_length=512,
        description="Caminho absoluto do diretório raiz do projeto onde os artefatos serão instalados.",
    )


class DeployedFile(BaseModel):
    relative_path: str
    absolute_path: str
    status: str  # "created" | "overwritten" | "skipped"


class DeployResponse(BaseModel):
    success: bool
    project_path: str
    deployed_files: list[DeployedFile]
    instructions: str
    message: str
