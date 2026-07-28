import json

from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import (
    ANTI_DUPLICATION_BLOCK,
    ENTERPRISE_RULES_BLOCK,
    TOKEN_ECONOMY_BLOCK,
    materials_table,
    skill_graph,
)


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    graph = skill_graph(["Objetivo", "Materiais", "Diretrizes", "Ferramentas"])
    constraints_block = project.constraints.strip() if project.constraints.strip() else "Sem restrições adicionais."

    system_text = "\n\n".join([
        f"# {project.skill_name}",
        f"## Skill Graph\n{graph}",
        f"## Objetivo\n{project.objective}",
        f"## Contexto\n{project.high_level_description}",
        f"## Materiais\n{materials_table(materials)}",
        f"## Restrições\n{constraints_block}",
        TOKEN_ECONOMY_BLOCK,
        ANTI_DUPLICATION_BLOCK,
        ENTERPRISE_RULES_BLOCK,
        f"## Diretrizes\n{generated_core}",
    ])

    instruction = {
        "system_instruction": {
            "role": "system",
            "parts": [{"text": system_text}],
        },
        "tools": [
            {
                "function_declarations": [
                    {
                        "name": "register_implementation_log",
                        "description": (
                            "Registra alterações no IMPLEMENTATION_LOG.md. "
                            "Chame ao final de cada sessão de trabalho."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string",
                                    "description": "Resumo em 1–3 frases do que foi implementado.",
                                },
                                "files": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Arquivos criados ou modificados.",
                                },
                            },
                            "required": ["summary", "files"],
                        },
                    }
                ]
            }
        ],
    }

    return [
        GeneratedFile(
            path="vertex/system_instruction.json",
            content=json.dumps(instruction, indent=2, ensure_ascii=False),
        )
    ]
