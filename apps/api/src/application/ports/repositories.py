from abc import ABC, abstractmethod

from src.domain.entities import GenerationJob


class GenerationHistoryRepositoryPort(ABC):
    @abstractmethod
    def find_by_request_hash(self, request_hash: str) -> GenerationJob | None:
        raise NotImplementedError

    @abstractmethod
    def find_latest_for_agent(self, agent_id: str, project_hash: str) -> GenerationJob | None:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        request_hash: str,
        project_hash: str,
        materials_hash: str,
        target_agent: str,
        summary: str,
        artifact_index: str,
    ) -> GenerationJob:
        raise NotImplementedError
