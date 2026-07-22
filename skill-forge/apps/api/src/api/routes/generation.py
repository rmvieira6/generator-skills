from fastapi import APIRouter, HTTPException

from src.api.schemas.generation import (
    ConnectionTestRequest,
    ConnectionTestResponse,
    GenerateItemResponse,
    GenerateRequest,
    GenerateResponse,
)
from src.application.use_cases.generate_skill import GenerateSkillUseCase
from src.application.use_cases.package_artifacts import package_as_zip
from src.core.config import settings
from src.core.sai_client import SaiLibraryClient
from src.domain.entities import Material, Project
from src.infrastructure.persistence.artifact_store import artifact_store
from src.infrastructure.persistence.generation_repository import SqlGenerationHistoryRepository

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    if len(request.high_level_description) > settings.MAX_DESCRIPTION_LENGTH:
        raise HTTPException(status_code=422, detail="High level description exceeds configured limit")

    project = Project(
        skill_name=request.skill_name,
        objective=request.objective,
        domain=request.domain,
        autonomy_level=request.autonomy_level,
        constraints=request.constraints,
        high_level_description=request.high_level_description,
        target_agents=request.target_agents,
    )
    materials = [Material(**item.model_dump(mode="json")) for item in request.materials]

    use_case = GenerateSkillUseCase(
        history_repo=SqlGenerationHistoryRepository(),
        sai_client=SaiLibraryClient(),
    )

    items: list[GenerateItemResponse] = []
    for target_agent in request.target_agents:
        result = await use_case.execute(project=project, materials=materials, target_agent=target_agent)
        zip_bytes = package_as_zip(
            files=result.files,
            project=project,
            agent=target_agent,
            suggested_prompt=result.suggested_prompt,
        )
        download_token = artifact_store.put(zip_bytes)

        items.append(
            GenerateItemResponse(
                target_agent=target_agent,
                preview_markdown=result.preview_markdown,
                suggested_prompt=result.suggested_prompt,
                used_cached_job=result.used_cached_job,
                download_token=download_token,
                generated_files=[item.path for item in result.files],
            )
        )

    return GenerateResponse(items=items)


@router.post("/test-connection", response_model=ConnectionTestResponse)
def test_connection(request: ConnectionTestRequest) -> ConnectionTestResponse:
    metadata = request.connection_metadata
    if request.connector_type.value in {"rest_api", "graphql_api"}:
        if "base_url" not in metadata and "endpoint" not in metadata:
            return ConnectionTestResponse(ok=False, detail="Missing base_url or endpoint")

    return ConnectionTestResponse(ok=True, detail="Connection parameters look valid")
