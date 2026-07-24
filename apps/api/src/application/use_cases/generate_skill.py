from pathlib import Path

from src.application.ports.repositories import GenerationHistoryRepositoryPort
from src.application.use_cases.validate_materials import sanitize_metadata, validate_materials
from src.core.config import settings
from src.core.sai_client import SaiLibraryClient
from src.domain.entities import GenerationResult, Material, Project, TargetAgent
from src.domain.value_objects import material_diff, stable_hash
from src.infrastructure.agent_templates import registry


class GenerateSkillUseCase:
    def __init__(
        self,
        history_repo: GenerationHistoryRepositoryPort,
        sai_client: SaiLibraryClient,
    ) -> None:
        self._history_repo = history_repo
        self._sai_client = sai_client

    async def execute(self, project: Project, materials: list[Material], target_agent: TargetAgent) -> GenerationResult:
        materials = validate_materials(materials)

        project_payload = project.model_dump(mode="json")
        materials_payload = [
            {
                **item.model_dump(mode="json"),
                "connection_metadata": sanitize_metadata(item.connection_metadata),
            }
            for item in materials
        ]

        request_hash = stable_hash(
            {
                "agent": target_agent.value,
                "project": project_payload,
                "materials": materials_payload,
            }
        )
        project_hash = stable_hash(project_payload)
        materials_hash = stable_hash(materials_payload)

        cached = self._history_repo.find_by_request_hash(request_hash)
        if cached is not None:
            cached_payload = registry.decode_artifact_index(cached.artifact_index)
            files = registry.files_from_dicts(cached_payload["files"])
            return GenerationResult(
                files=files,
                preview_markdown=cached_payload["preview_markdown"],
                suggested_prompt=cached_payload["suggested_prompt"],
                used_cached_job=True,
            )

        previous = self._history_repo.find_latest_for_agent(target_agent.value, project_hash)
        incremental_hint = ""
        if previous is not None:
            previous_payload = registry.decode_artifact_index(previous.artifact_index)
            old_payload = previous_payload.get("request_payload", {})
            new_payload = {"materials": materials_payload}
            incremental_hint = material_diff(old_payload, new_payload)

        prompt = self._build_prompt(project, materials_payload, target_agent, incremental_hint)

        generated_core = await self._sai_client.execute(prompt)
        files = registry.render_for_agent(target_agent, project, materials, generated_core)
        suggested_prompt = registry.suggested_prompt(project)

        preview_markdown = next((item.content for item in files if item.path.endswith("SKILL.md")), files[0].content)

        artifact_index = registry.encode_artifact_index(
            files=files,
            preview_markdown=preview_markdown,
            suggested_prompt=suggested_prompt,
            request_payload={"materials": materials_payload},
        )

        self._history_repo.save(
            request_hash=request_hash,
            project_hash=project_hash,
            materials_hash=materials_hash,
            target_agent=target_agent.value,
            summary=f"Generated for {target_agent.value}",
            artifact_index=artifact_index,
        )

        return GenerationResult(
            files=files,
            preview_markdown=preview_markdown,
            suggested_prompt=suggested_prompt,
            used_cached_job=False,
        )

    def _build_prompt(
        self,
        project: Project,
        materials_payload: list[dict[str, object]],
        target_agent: TargetAgent,
        incremental_hint: str,
    ) -> str:
        master_template = self._read_master_template()
        materials_block = "\n".join(
            [
                f"- {item['name']} ({item['connector_type']}): {item['description']}"
                for item in materials_payload
            ]
        )

        return (
            master_template
            .replace("{{PROJECT_NAME}}", project.skill_name)
            .replace("{{OBJECTIVE}}", project.objective)
            .replace("{{DOMAIN}}", project.domain)
            .replace("{{AUTONOMY_LEVEL}}", project.autonomy_level)
            .replace("{{TARGET_AGENT}}", target_agent.value)
            .replace("{{HIGH_LEVEL_DESCRIPTION}}", project.high_level_description)
            .replace("{{CONSTRAINTS}}", project.constraints or "Sem restricoes adicionais")
            .replace("{{MATERIALS_TABLE}}", materials_block)
            .replace("{{INCREMENTAL_DIFF}}", incremental_hint or "Sem diff incremental")
        )

    def _read_master_template(self) -> str:
        configured_path = Path(settings.SKILL_MASTER_TEMPLATE_PATH)
        candidates = [configured_path]

        cwd = Path.cwd()
        candidates.append(cwd / configured_path)
        for parent in cwd.parents:
            candidates.append(parent / configured_path)

        for candidate in candidates:
            if candidate.exists():
                return candidate.read_text(encoding="utf-8")

        raise FileNotFoundError(f"SKILL master template not found at: {settings.SKILL_MASTER_TEMPLATE_PATH}")
