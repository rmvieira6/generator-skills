from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    skill = f"""---
name: {project.skill_name}-fabric
description: Skill para uso com notebooks PySpark no Microsoft Fabric
version: 1.0.0
---

# Objetivo
{project.objective}

# Materiais
{materials_table(materials)}

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}

# Regras Fabric PySpark
- Priorize celulas pequenas e reprodutiveis.
- Evite duplicar transformacoes; extraia funcoes utilitarias.
- Registre premissas de schema e qualidade de dados.

# Nucleo
{generated_core}
"""

    usage = """# Uso no Fabric PySpark Notebook
1. Cole o conteudo de SKILL.md no contexto do assistente de notebook usado pelo seu time.
2. Use o prompt sugerido para iniciar revisao de celulas ou transformacoes.
3. Mantenha a skill versionada junto com o notebook.
"""

    return [
        GeneratedFile(path="fabric/SKILL.md", content=skill),
        GeneratedFile(path="fabric/NOTEBOOK_USAGE.md", content=usage),
    ]
