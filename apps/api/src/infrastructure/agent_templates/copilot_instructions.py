from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    SENIOR_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Diretrizes", "Restrições"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"

    content = f"""\
# {project.skill_name} — Copilot Instructions

> Aplique estas instruções sempre ao trabalhar neste repositório.

## Skill Graph
{graph}
## Objetivo
{project.objective}

## Contexto Completo
{project.high_level_description}

## Materiais → [[Materiais]]
{materials_table(materials)}

## Restrições
{constraints_block}

{TOKEN_ECONOMY_BLOCK}

{ANTI_DUPLICATION_BLOCK}

{SENIOR_RULES_BLOCK}

## Diretrizes Operacionais
{generated_core}

## Protocolo de Resposta
- Responda de forma direta e acionável.
- NÃO invente requisitos fora do escopo definido.
- Ao concluir: liste arquivos alterados e testes executados.
- Pare quando o objetivo for entregue.
"""
    return [GeneratedFile(path=".github/copilot-instructions.md", content=content)]
