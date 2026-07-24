import json

from src.domain.entities import GeneratedFile, Material, Project, TargetAgent
from src.infrastructure.agent_templates import (
    claude_skill,
    copilot_instructions,
    cursor_rules,
    fabric_pyspark_notebook,
    generic_openai,
    kiro_skill,
    vertex_ai,
    windsurf,
)
from src.infrastructure.agent_templates.common import usage_prompt


def render_for_agent(
    target_agent: TargetAgent,
    project: Project,
    materials: list[Material],
    generated_core: str,
) -> list[GeneratedFile]:
    renderers = {
        TargetAgent.CLAUDE: claude_skill.render,
        TargetAgent.KIRO: kiro_skill.render,
        TargetAgent.COPILOT: copilot_instructions.render,
        TargetAgent.CURSOR: cursor_rules.render,
        TargetAgent.VERTEX_AI: vertex_ai.render,
        TargetAgent.WINDSURF: windsurf.render,
        TargetAgent.GENERIC_OPENAI: generic_openai.render,
        TargetAgent.FABRIC_PYSPARK_NOTEBOOK: fabric_pyspark_notebook.render,
    }
    return renderers[target_agent](project, materials, generated_core)


def suggested_prompt(project: Project) -> str:
    return usage_prompt(project)


def encode_artifact_index(
    files: list[GeneratedFile],
    preview_markdown: str,
    suggested_prompt: str,
    request_payload: dict[str, object],
) -> str:
    payload = {
        "files": [file.model_dump(mode="json") for file in files],
        "preview_markdown": preview_markdown,
        "suggested_prompt": suggested_prompt,
        "request_payload": request_payload,
    }
    return json.dumps(payload, ensure_ascii=True)


def decode_artifact_index(value: str) -> dict[str, object]:
    return json.loads(value)


def files_from_dicts(entries: object) -> list[GeneratedFile]:
    if not isinstance(entries, list):
        return []
    return [GeneratedFile.model_validate(item) for item in entries]
