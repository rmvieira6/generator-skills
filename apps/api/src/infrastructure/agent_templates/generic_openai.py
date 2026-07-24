import json

from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    SENIOR_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Diretrizes", "Ferramentas"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "_Sem restrições adicionais._"

    system_prompt = f"""\
# {project.skill_name} — System Prompt

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
"""

    tools = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "append_implementation_log",
                    "description": (
                        "Registra a execução no IMPLEMENTATION_LOG.md do projeto. "
                        "Chame ao final de cada sessão de trabalho."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Data no formato YYYY-MM-DD.",
                            },
                            "summary": {
                                "type": "string",
                                "description": "Resumo em 1–3 frases do que foi implementado.",
                            },
                            "files": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista de arquivos criados ou modificados.",
                            },
                        },
                        "required": ["date", "summary", "files"],
                    },
                },
            }
        ]
    }

    return [
        GeneratedFile(path="system_prompt.md", content=system_prompt),
        GeneratedFile(path="tools.json", content=json.dumps(tools, indent=2, ensure_ascii=False)),
    ]
