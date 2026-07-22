from sqlmodel import desc, select

from src.application.ports.repositories import GenerationHistoryRepositoryPort
from src.domain.entities import GenerationJob, TargetAgent
from src.infrastructure.persistence.db import get_session
from src.infrastructure.persistence.models import GenerationJobRecord


class SqlGenerationHistoryRepository(GenerationHistoryRepositoryPort):
    def find_by_request_hash(self, request_hash: str) -> GenerationJob | None:
        with get_session() as session:
            statement = select(GenerationJobRecord).where(GenerationJobRecord.request_hash == request_hash)
            record = session.exec(statement).first()
            return self._to_domain(record)

    def find_latest_for_agent(self, agent_id: str, project_hash: str) -> GenerationJob | None:
        with get_session() as session:
            statement = (
                select(GenerationJobRecord)
                .where(GenerationJobRecord.target_agent == agent_id)
                .where(GenerationJobRecord.project_hash == project_hash)
                .order_by(desc(GenerationJobRecord.created_at))
            )
            record = session.exec(statement).first()
            return self._to_domain(record)

    def save(
        self,
        request_hash: str,
        project_hash: str,
        materials_hash: str,
        target_agent: str,
        summary: str,
        artifact_index: str,
    ) -> GenerationJob:
        with get_session() as session:
            record = GenerationJobRecord(
                request_hash=request_hash,
                project_hash=project_hash,
                materials_hash=materials_hash,
                target_agent=target_agent,
                summary=summary,
                artifact_index=artifact_index,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            domain = self._to_domain(record)
            if domain is None:
                raise RuntimeError("Failed to map generation job")
            return domain

    def _to_domain(self, record: GenerationJobRecord | None) -> GenerationJob | None:
        if record is None or record.id is None:
            return None
        return GenerationJob(
            id=record.id,
            request_hash=record.request_hash,
            project_hash=record.project_hash,
            materials_hash=record.materials_hash,
            target_agent=TargetAgent(record.target_agent),
            summary=record.summary,
            artifact_index=record.artifact_index,
        )
