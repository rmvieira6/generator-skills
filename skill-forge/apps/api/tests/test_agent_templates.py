from src.domain.entities import ConnectorType, Material, Project, TargetAgent
from src.infrastructure.agent_templates.registry import render_for_agent


def _project() -> Project:
    return Project(
        skill_name="Backend Reviewer",
        objective="Revisar PRs de backend",
        domain="backend",
        autonomy_level="apply_changes",
        constraints="Sem reescrever arquivos completos",
        high_level_description="Criar skill para revisao de PRs Node com padroes internos",
        target_agents=[TargetAgent.CLAUDE],
    )


def _materials() -> list[Material]:
    return [
        Material(
            connector_type=ConnectorType.GIT_REPOSITORY,
            name="Repo Principal",
            description="Fonte de verdade do codigo",
            connection_metadata={"url": "https://example.com/repo.git", "branch": "main"},
        )
    ]


def test_claude_template() -> None:
    files = render_for_agent(TargetAgent.CLAUDE, _project(), _materials(), "Core")
    assert any(item.path == "SKILL.md" for item in files)


def test_copilot_template() -> None:
    files = render_for_agent(TargetAgent.COPILOT, _project(), _materials(), "Core")
    assert any(item.path == ".github/copilot-instructions.md" for item in files)


def test_cursor_template() -> None:
    files = render_for_agent(TargetAgent.CURSOR, _project(), _materials(), "Core")
    assert any(item.path.endswith(".mdc") for item in files)


def test_vertex_template() -> None:
    files = render_for_agent(TargetAgent.VERTEX_AI, _project(), _materials(), "Core")
    assert any(item.path.endswith("system_instruction.json") for item in files)


def test_windsurf_template() -> None:
    files = render_for_agent(TargetAgent.WINDSURF, _project(), _materials(), "Core")
    assert any(item.path == ".windsurfrules" for item in files)


def test_generic_openai_template() -> None:
    files = render_for_agent(TargetAgent.GENERIC_OPENAI, _project(), _materials(), "Core")
    assert any(item.path == "system_prompt.md" for item in files)


def test_fabric_template() -> None:
    files = render_for_agent(TargetAgent.FABRIC_PYSPARK_NOTEBOOK, _project(), _materials(), "Core")
    assert any(item.path == "fabric/SKILL.md" for item in files)
