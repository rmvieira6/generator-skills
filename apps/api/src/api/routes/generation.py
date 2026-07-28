import logging

from fastapi import APIRouter, HTTPException

from src.api.schemas.generation import (
    ConnectionTestRequest,
    ConnectionTestResponse,
    GenerateItemResponse,
    GenerateRequest,
    GenerateResponse,
    OptimizeSkillRequest,
    OptimizeSkillResponse,
)
from src.application.use_cases.generate_skill import GenerateSkillUseCase
from src.application.use_cases.optimize_skill import OptimizeSkillUseCase
from src.application.use_cases.package_artifacts import package_as_zip
from src.core.config import settings
from src.core.sai_client import SaiAuthError, SaiConfigurationError, SaiLibraryClient, SaiUpstreamError
from src.domain.entities import Material, Project
from src.infrastructure.persistence.artifact_store import artifact_store
from src.infrastructure.persistence.generation_repository import SqlGenerationHistoryRepository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    if len(request.high_level_description) > settings.MAX_DESCRIPTION_LENGTH:
        raise HTTPException(status_code=422, detail="Descrição excede o limite configurado.")

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
        try:
            result = await use_case.execute(project=project, materials=materials, target_agent=target_agent)
        except SaiConfigurationError as exc:
            logger.error("SAI not configured: %s", exc)
            raise HTTPException(
                status_code=503,
                detail=(
                    "A API de geração não está configurada. "
                    "Copie .env.example para .env na raiz do projeto e preencha "
                    "SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID."
                ),
            ) from exc
        except SaiAuthError as exc:
            logger.error("SAI auth error: %s", exc)
            raise HTTPException(
                status_code=502,
                detail=(
                    "Credenciais da SAI Library inválidas (401/403). "
                    "Verifique SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID no arquivo .env."
                ),
            ) from exc
        except SaiUpstreamError as exc:
            logger.error("SAI upstream error: %s", exc)
            raise HTTPException(
                status_code=502,
                detail=f"Erro na SAI Library: {exc}",
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected error generating skill for agent %s", target_agent)
            raise HTTPException(
                status_code=500,
                detail=f"Erro inesperado ao gerar artefato: {exc}",
            ) from exc

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


@router.post("/optimize-skill", response_model=OptimizeSkillResponse)
async def optimize_skill(request: OptimizeSkillRequest) -> OptimizeSkillResponse:
    use_case = OptimizeSkillUseCase(sai_client=SaiLibraryClient())

    try:
        optimized_markdown, detected_target, effective_target, quality_notes = await use_case.execute(
            skill_markdown=request.skill_markdown,
            goals=request.goals,
            target_agent=request.target_agent,
            objective_refinement_request=request.objective_refinement_request,
        )
    except SaiConfigurationError as exc:
        logger.error("SAI not configured: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=(
                "A API de otimização não está configurada. "
                "Copie .env.example para .env na raiz do projeto e preencha "
                "SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID."
            ),
        ) from exc
    except SaiAuthError as exc:
        logger.error("SAI auth error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "Credenciais da SAI Library inválidas (401/403). "
                "Verifique SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID no arquivo .env."
            ),
        ) from exc
    except SaiUpstreamError as exc:
        logger.error("SAI upstream error: %s", exc)
        raise HTTPException(status_code=502, detail=f"Erro na SAI Library: {exc}") from exc
    except Exception as exc:
        logger.exception("Unexpected error optimizing skill")
        raise HTTPException(status_code=500, detail=f"Erro inesperado ao otimizar skill: {exc}") from exc

    return OptimizeSkillResponse(
        optimized_markdown=optimized_markdown,
        detected_target_agent=detected_target,
        effective_target_agent=effective_target,
        applied_goals=request.goals,
        quality_notes=quality_notes,
    )
