from src.application.use_cases.optimize_skill import OptimizeSkillUseCase
from src.api.schemas.generation import SkillOptimizationGoal
from src.domain.entities import TargetAgent


class _DummySaiClient:
    async def execute(self, prompt: str) -> str:
        return prompt


def test_detect_target_agent_copilot_signature() -> None:
    use_case = OptimizeSkillUseCase(sai_client=_DummySaiClient())

    detected = use_case.detect_target_agent("Use .github/copilot-instructions.md para ativar")

    assert detected == TargetAgent.COPILOT


def test_detect_target_agent_returns_none_when_no_signature() -> None:
    use_case = OptimizeSkillUseCase(sai_client=_DummySaiClient())

    detected = use_case.detect_target_agent("Conteúdo genérico sem assinatura específica")

    assert detected is None


def test_build_prompt_disables_conditional_policies_when_goals_not_selected() -> None:
    use_case = OptimizeSkillUseCase(sai_client=_DummySaiClient())

    prompt = use_case._build_prompt(
        skill_markdown="# Skill\nconteudo",
        goals=[],
        target_agent=TargetAgent.CLAUDE,
    )

    assert "NÃO aplicar técnicas específicas desses dois grupos nesta otimização." in prompt


def test_build_prompt_enables_token_policy_only_when_token_goal_selected() -> None:
    use_case = OptimizeSkillUseCase(sai_client=_DummySaiClient())

    prompt = use_case._build_prompt(
        skill_markdown="# Skill\nconteudo",
        goals=[SkillOptimizationGoal.TOKEN_REDUCTION],
        target_agent=TargetAgent.CLAUDE,
    )

    assert "POLÍTICA CONDICIONAL — REDUÇÃO DE TOKENS" in prompt
    assert "Token Economy Without Decision Loss" in prompt
    assert "não duplicar detalhes operacionais de publicação/execução" in prompt.lower()
    assert "$fabric-full-agent" in prompt
    assert "POLÍTICA CONDICIONAL — ROBUSTEZ/TEMPO TOTAL/QUALIDADE" not in prompt


def test_build_prompt_enables_execution_policy_only_when_execution_goal_selected() -> None:
    use_case = OptimizeSkillUseCase(sai_client=_DummySaiClient())

    prompt = use_case._build_prompt(
        skill_markdown="# Skill\nconteudo",
        goals=[SkillOptimizationGoal.EXECUTION_DEPTH],
        target_agent=TargetAgent.CLAUDE,
    )

    assert "POLÍTICA CONDICIONAL — ROBUSTEZ/TEMPO TOTAL/QUALIDADE" in prompt
    assert "Regra de decisão final" in prompt
    assert "POLÍTICA CONDICIONAL — REDUÇÃO DE TOKENS" not in prompt
