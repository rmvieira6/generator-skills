import json

from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    instruction = {
        "system_instruction": {
            "role": "system",
            "parts": [
                {
                    "text": "\n".join(
                        [
                            f"Objetivo: {project.objective}",
                            materials_table(materials),
                            ANTI_DUPLICATION_BLOCK,
                            senior_rules(),
                            generated_core,
                        ]
                    )
                }
            ],
        },
        "tools": [
            {
                "function_declarations": [
                    {
                        "name": "register_implementation_log",
                        "description": "Registra alteracoes no IMPLEMENTATION_LOG.md",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "files": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["summary", "files"],
                        },
                    }
                ]
            }
        ],
    }
    return [GeneratedFile(path="vertex/system_instruction.json", content=json.dumps(instruction, indent=2))]
