from pydantic import BaseModel


class AgentCatalogItem(BaseModel):
    id: str
    label: str
    files: list[str]


class ConnectorCatalogItem(BaseModel):
    id: str
    label: str
    fields: list[str]


class CatalogResponse(BaseModel):
    agents: list[AgentCatalogItem]
    connectors: list[ConnectorCatalogItem]
