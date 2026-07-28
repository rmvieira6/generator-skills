from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    ENTERPRISE_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Regras Fabric", "Núcleo"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"

    skill = f"""\
---
name: {project.skill_name}-fabric
description: Skill para uso com notebooks PySpark no Microsoft Fabric
version: 1.0.0
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

{ANTI_DUPLICATION_BLOCK}

{ENTERPRISE_RULES_BLOCK}

## Regras Fabric PySpark → [[Regras Fabric]]
- Células pequenas e reprodutíveis; cada célula com propósito único.
- NÃO duplique transformações; extraia funções utilitárias reutilizáveis.
- Registre premissas de schema e qualidade de dados no início do notebook.
- Use `display()` apenas para debug; remova antes de produção.
- Prefira `spark.read` com schema explícito a inferência automática.

## Núcleo
{generated_core}
"""

    usage = f"""\
# Como usar esta Skill no Fabric PySpark Notebook

## Passo a passo
1. Abra o assistente de IA do seu notebook no Microsoft Fabric.
2. Cole o conteúdo de `SKILL.md` no campo de system prompt ou contexto do assistente.
3. Use o prompt sugerido abaixo para iniciar:

```
Usando a skill {project.skill_name}, revise as células deste notebook seguindo
as regras de anti-duplicação, células atômicas e schema explícito.
```

## Localização dos arquivos
| Arquivo | Onde colocar |
|---|---|
| `fabric/SKILL.md` | Junto ao notebook ou em repositório de skills da equipe |
| `fabric/NOTEBOOK_USAGE.md` | Documentação do projeto |

## Boas práticas
- Versione a skill junto com o notebook no repositório Git.
- Atualize a skill quando o schema de dados ou regras de negócio mudarem.
- Compartilhe a skill com a equipe para consistência entre notebooks.
"""

    return [
        GeneratedFile(path="fabric/SKILL.md", content=skill),
        GeneratedFile(path="fabric/NOTEBOOK_USAGE.md", content=usage),
    ]
