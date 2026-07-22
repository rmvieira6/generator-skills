from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    core_rule = f"""---
description: Core rule for {project.skill_name}
globs:
  - "**/*"
alwaysApply: true
---

# Objetivo
{project.objective}

# Materiais
{materials_table(materials)}

# Diretriz
{generated_core}
"""

    anti_dup_rule = f"""---
description: Anti-duplicacao e padroes senior
globs:
  - "**/*"
alwaysApply: true
---

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}
"""

    legacy = (
        f"Objetivo: {project.objective}\n\n"
        f"{ANTI_DUPLICATION_BLOCK}\n"
        f"{senior_rules()}\n"
        f"Diretriz: {generated_core}\n"
    )

    return [
        GeneratedFile(path=".cursor/rules/core.mdc", content=core_rule),
        GeneratedFile(path=".cursor/rules/anti-duplication.mdc", content=anti_dup_rule),
        GeneratedFile(path=".cursorrules", content=legacy),
    ]
