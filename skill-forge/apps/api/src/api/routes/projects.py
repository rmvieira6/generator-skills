from pathlib import Path

import yaml
from fastapi import APIRouter

from src.api.schemas.catalog import AgentCatalogItem, CatalogResponse, ConnectorCatalogItem
from src.core.config import settings

router = APIRouter()


def _load_yaml(path: str) -> dict[str, object]:
    raw = Path(path).read_text(encoding="utf-8")
    parsed = yaml.safe_load(raw)
    if isinstance(parsed, dict):
        return parsed
    return {}


@router.get("/catalog", response_model=CatalogResponse)
def get_catalog() -> CatalogResponse:
    agents_payload = _load_yaml(settings.AGENTS_CONFIG_PATH).get("agents", [])
    connectors_payload = _load_yaml(settings.CONNECTORS_CONFIG_PATH).get("connectors", [])

    agents = [AgentCatalogItem(**item) for item in agents_payload if isinstance(item, dict)]
    connectors = [ConnectorCatalogItem(**item) for item in connectors_payload if isinstance(item, dict)]

    return CatalogResponse(agents=agents, connectors=connectors)
