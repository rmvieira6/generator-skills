from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    SENIOR_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    """Gera steering file para o Kiro IDE (.kiro/steering/<name>.md)."""
    graph = skill_graph(["Objetivo", "Materiais", "Regras", "Execução"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"
    # Normaliza o nome do arquivo: minúsculas, espaços → hífens
    safe_name = project.skill_name.lower().replace(" ", "-")

    content = f"""\
---
inclusion: always
---

# {project.skill_name}

> Steering file para o Kiro IDE. Incluído automaticamente em todas as sessões do workspace.

## Skill Graph
{graph}
## Objetivo
{project.objective}

## Contexto
{project.high_level_description}

## Materiais → [[Materiais]]
{materials_table(materials)}

## Restrições
{constraints_block}

{TOKEN_ECONOMY_BLOCK}

{ANTI_DUPLICATION_BLOCK}

{SENIOR_RULES_BLOCK}

## Diretrizes
{generated_core}

## Como ativar
Esta skill é carregada automaticamente pelo Kiro IDE ao abrir o workspace.
Para uso manual: mencione `#{safe_name}` no chat do Kiro.
"""
    return [GeneratedFile(path=f".kiro/steering/{safe_name}.md", content=content)]
