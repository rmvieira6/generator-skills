import json

from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    system_prompt = f"""# System Prompt - {project.skill_name}

Objetivo: {project.objective}

Materiais:
{materials_table(materials)}

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}

Nucleo:
{generated_core}
"""

    tools = {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "append_implementation_log",
                    "description": "Atualiza IMPLEMENTATION_LOG.md com o resumo da execucao.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "summary": {"type": "string"},
                            "files": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["date", "summary", "files"],
                    },
                },
            }
        ]
    }

    return [
        GeneratedFile(path="system_prompt.md", content=system_prompt),
        GeneratedFile(path="tools.json", content=json.dumps(tools, indent=2)),
    ]
