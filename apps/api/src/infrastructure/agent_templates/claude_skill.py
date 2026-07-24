from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    SENIOR_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
    usage_prompt,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Regras", "Execução", "Saída"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"

    content = f"""\
---
name: {project.skill_name}
description: {project.objective}
version: 1.0.0
---

## Skill Graph
{graph}
## Contexto
| Campo | Valor |
|---|---|
| Domínio | `{project.domain}` |
| Autonomia | `{project.autonomy_level}` |

## Objetivo
{project.high_level_description}

## Materiais → [[Materiais]]
{materials_table(materials)}

## Restrições
{constraints_block}

{TOKEN_ECONOMY_BLOCK}

{ANTI_DUPLICATION_BLOCK}

{SENIOR_RULES_BLOCK}

## Núcleo Gerado
{generated_core}

## Execução
- Consulte `[[Materiais]]` antes de iniciar qualquer leitura de contexto.
- Aplique `[[Anti-Duplicação]]` em cada mudança.
- Pare ao concluir o objetivo; não expanda o escopo.
"""
    return [GeneratedFile(path="SKILL.md", content=content)]
