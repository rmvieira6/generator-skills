from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    content = f"""Windsurf rules for {project.skill_name}

Objetivo: {project.objective}

Materiais:
{materials_table(materials)}

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}

Diretriz principal:
{generated_core}
"""
    return [GeneratedFile(path=".windsurfrules", content=content)]
