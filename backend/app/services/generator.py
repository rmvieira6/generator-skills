"""
Artifact generator service.

Builds the system prompt and user prompt for the LLM, calls the LLM via the
SAI Library abstraction, and assembles the list of ArtifactFile objects that
are specific to the target agent.
"""

from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING

from app.models.schemas import (
    AgentTarget,
    ArtifactFile,
    ContextMaterial,
    GenerateRequest,
)

if TYPE_CHECKING:
    from app.services.llm import LLMClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Agent-specific output file mapping
# ---------------------------------------------------------------------------

AGENT_META: dict[AgentTarget, dict] = {
    AgentTarget.claude: {
        "display_name": "Claude (Anthropic)",
        "primary_file": "SKILL.md",
        "readme_note": (
            "Place SKILL.md in your project root and reference it in your "
            "Claude project knowledge base or attach it as a file when starting "
            "a conversation."
        ),
    },
    AgentTarget.copilot: {
        "display_name": "GitHub Copilot (VS Code)",
        "primary_file": ".github/copilot-instructions.md",
        "readme_note": (
            "Commit `.github/copilot-instructions.md` to your repository root. "
            "GitHub Copilot will automatically pick it up."
        ),
    },
    AgentTarget.cursor: {
        "display_name": "Cursor",
        "primary_file": ".cursorrules",
        "readme_note": (
            "Place `.cursorrules` in your project root. "
            "Cursor will load it automatically when you open the project."
        ),
    },
    AgentTarget.vertex_ai: {
        "display_name": "Vertex AI (Google Cloud)",
        "primary_file": "system_instruction.txt",
        "readme_note": (
            "Use the contents of `system_instruction.txt` as the System "
            "Instruction field when configuring your Vertex AI Agent Builder or "
            "Gemini API request."
        ),
    },
    AgentTarget.windsurf: {
        "display_name": "Windsurf (Codeium)",
        "primary_file": ".windsurfrules",
        "readme_note": (
            "Place `.windsurfrules` in your project root. "
            "Windsurf will load it automatically when you open the project."
        ),
    },
    AgentTarget.generic_openai: {
        "display_name": "Generic (OpenAI-compatible)",
        "primary_file": "SKILL.md",
        "readme_note": (
            "Use the contents of `SKILL.md` as the system prompt when calling "
            "any OpenAI-compatible API (system message role)."
        ),
    },
}

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""\
    You are Skill Forge, an expert AI context-artifact generator.
    Your task is to produce a high-quality, structured context artifact for a
    specific AI agent / IDE.  Follow the format instructions exactly.
    Write in the same language the user used in their description.
    Be precise, actionable, and avoid generic filler text.
""")


def _build_materials_section(materials: list[ContextMaterial]) -> str:
    if not materials:
        return "No specific context materials were provided."
    lines = []
    for i, m in enumerate(materials, start=1):
        meta = m.connection_metadata
        parts = [f"**Material {i} – {m.connector_type.value}**"]
        parts.append(f"- Description: {m.description}")
        if meta.host:
            parts.append(f"- Host: {meta.host}")
        if meta.port:
            parts.append(f"- Port: {meta.port}")
        if meta.database:
            parts.append(f"- Database/Resource: {meta.database}")
        if meta.username:
            parts.append(f"- Username: {meta.username}")
        if meta.password_env_ref:
            parts.append(f"- Password: referenced via env var `{meta.password_env_ref}`")
        if meta.api_key_env_ref:
            parts.append(f"- API Key: referenced via env var `{meta.api_key_env_ref}`")
        for k, v in meta.extra.items():
            parts.append(f"- {k}: {v}")
        lines.append("\n".join(parts))
    return "\n\n".join(lines)


def _build_user_prompt(request: GenerateRequest, agent_meta: dict) -> str:
    materials_text = _build_materials_section(request.context_materials)
    agent_name = agent_meta["display_name"]
    primary_file = agent_meta["primary_file"]
    readme_note = agent_meta["readme_note"]

    return textwrap.dedent(f"""\
        ## Task
        Generate a complete context artifact for **{agent_name}**.
        The primary output file MUST be: `{primary_file}`

        ## User's High-Level Description
        {request.high_level_description}

        ## Context Materials
        {materials_text}

        ## Output Format
        Return ONLY valid Markdown (or plain text for .cursorrules/.windsurfrules/
        system_instruction.txt).  Do NOT include any explanation outside the artifact.

        Structure the artifact with these sections (adapt headings to the agent's
        conventions):

        1. **Purpose / Role** – concise statement of what the agent must do.
        2. **Context & Data Sources** – describe each material and what the agent
           should extract or be aware of.  Include connection hints (env-var
           references for secrets).
        3. **Operating Guidelines** – numbered rules/constraints the agent must
           always follow.
        4. **Output Format** – expected format of the agent's responses.
        5. **Examples** (optional but recommended) – one or two short examples.

        Usage note for the user: {readme_note}
    """)


# ---------------------------------------------------------------------------
# Suggested prompt builder
# ---------------------------------------------------------------------------


def _build_suggested_prompt(request: GenerateRequest, agent_meta: dict) -> str:
    return (
        f"I have loaded the {agent_meta['display_name']} skill artifact "
        f"(`{agent_meta['primary_file']}`) for this project.\n\n"
        f"My goal: {request.high_level_description}\n\n"
        "Please follow all instructions in the artifact and help me achieve this goal."
    )


# ---------------------------------------------------------------------------
# README builder
# ---------------------------------------------------------------------------


def _build_readme(request: GenerateRequest, agent_meta: dict) -> str:
    materials_count = len(request.context_materials)
    materials_list = "\n".join(
        f"- **{m.connector_type.value}**: {m.description}"
        for m in request.context_materials
    ) or "_No context materials provided._"

    return textwrap.dedent(f"""\
        # Skill Forge – Generated Artifact

        **Target agent:** {agent_meta['display_name']}
        **Primary file:** `{agent_meta['primary_file']}`
        **Context materials:** {materials_count}

        ## Description
        {request.high_level_description}

        ## Context Materials
        {materials_list}

        ## How to Use
        {agent_meta['readme_note']}

        ## Suggested Prompt
        Copy-paste the text below to start a conversation with the agent:

        ```
        {_build_suggested_prompt(request, agent_meta)}
        ```

        ---
        *Generated by Skill Forge.*
    """)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def generate_artifacts(
    request: GenerateRequest,
    llm_client: "LLMClient",
) -> tuple[list[ArtifactFile], str]:
    """
    Generate all artifact files for the given request.

    Returns:
        (artifacts, suggested_prompt)
    """
    agent_meta = AGENT_META[request.agent_target]
    logger.info(
        "Generating artifacts for agent=%s, materials=%d",
        request.agent_target,
        len(request.context_materials),
    )

    system_prompt = SYSTEM_PROMPT
    user_prompt = _build_user_prompt(request, agent_meta)

    primary_content = await llm_client.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    suggested_prompt = _build_suggested_prompt(request, agent_meta)
    readme_content = _build_readme(request, agent_meta)

    artifacts: list[ArtifactFile] = [
        ArtifactFile(path=agent_meta["primary_file"], content=primary_content),
        ArtifactFile(path="README.md", content=readme_content),
    ]

    logger.info("Artifacts generated: %d files", len(artifacts))
    return artifacts, suggested_prompt
