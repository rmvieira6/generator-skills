from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    SENIOR_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Diretrizes", "Anti-Dup", "Sênior"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"

    core_rule = f"""\
---
description: Regra principal para {project.skill_name}
globs:
  - "**/*"
alwaysApply: true
---

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

## Diretrizes
{generated_core}
"""

    anti_dup_rule = f"""\
---
description: Anti-duplicação e padrões sênior para {project.skill_name}
globs:
  - "**/*"
alwaysApply: true
---

{ANTI_DUPLICATION_BLOCK}

{SENIOR_RULES_BLOCK}
"""

    # .cursorrules legado (compatibilidade com versões antigas do Cursor)
    legacy = (
        f"# {project.skill_name}\n"
        f"Objetivo: {project.objective}\n\n"
        f"{ANTI_DUPLICATION_BLOCK}\n\n"
        f"{SENIOR_RULES_BLOCK}\n\n"
        f"## Diretrizes\n{generated_core}\n"
    )

    return [
        GeneratedFile(path=".cursor/rules/core.mdc", content=core_rule),
        GeneratedFile(path=".cursor/rules/anti-duplication.mdc", content=anti_dup_rule),
        GeneratedFile(path=".cursorrules", content=legacy),
    ]
