import asyncio

from src.application.ports.repositories import GenerationHistoryRepositoryPort
from src.application.use_cases.generate_skill import GenerateSkillUseCase
from src.domain.entities import ConnectorType, GenerationJob, Material, Project, TargetAgent


class FakeSaiClient:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, prompt: str) -> str:
        self.calls += 1
        return f"generated::{len(prompt)}"


class InMemoryHistoryRepository(GenerationHistoryRepositoryPort):
    def __init__(self) -> None:
        self._records: list[GenerationJob] = []

    def find_by_request_hash(self, request_hash: str) -> GenerationJob | None:
        for record in self._records:
            if record.request_hash == request_hash:
                return record
        return None

    def find_latest_for_agent(self, agent_id: str, project_hash: str) -> GenerationJob | None:
        candidates = [
            item for item in self._records if item.target_agent.value == agent_id and item.project_hash == project_hash
        ]
        return candidates[-1] if candidates else None

    def save(
        self,
        request_hash: str,
        project_hash: str,
        materials_hash: str,
        target_agent: str,
        summary: str,
        artifact_index: str,
    ) -> GenerationJob:
        record = GenerationJob(
            id=len(self._records) + 1,
            request_hash=request_hash,
            project_hash=project_hash,
            materials_hash=materials_hash,
            target_agent=TargetAgent(target_agent),
            summary=summary,
            artifact_index=artifact_index,
        )
        self._records.append(record)
        return record


def test_deduplicates_identical_generation() -> None:
    repo = InMemoryHistoryRepository()
    sai = FakeSaiClient()
    use_case = GenerateSkillUseCase(repo, sai)

    project = Project(
        skill_name="SkillX",
        objective="Objective X long enough",
        domain="backend",
        autonomy_level="suggest_only",
        constraints="",
        high_level_description="Descricao suficientemente longa para passar validacao",
        target_agents=[TargetAgent.CLAUDE],
    )
    materials = [
        Material(
            connector_type=ConnectorType.LOCAL_FILE,
            name="README",
            description="Documento principal",
            connection_metadata={"path": "README.md"},
        )
    ]

    first = asyncio.run(use_case.execute(project, materials, TargetAgent.CLAUDE))
    second = asyncio.run(use_case.execute(project, materials, TargetAgent.CLAUDE))

    assert first.used_cached_job is False
    assert second.used_cached_job is True
    assert sai.calls == 1
