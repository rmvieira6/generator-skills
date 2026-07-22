from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    content = f"""---
name: {project.skill_name}
description: {project.objective}
version: 1.0.0
---

# Objetivo
{project.high_level_description}

# Contexto Necessario
{materials_table(materials)}

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}

# Execucao
- Siga escopo pedido e pare ao concluir objetivo.
- Consulte arquivos auxiliares do projeto em vez de duplicar contexto no prompt.

# Nucleo Gerado
{generated_core}
"""
    return [GeneratedFile(path="SKILL.md", content=content)]
