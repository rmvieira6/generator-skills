from __future__ import annotations

import re

from src.api.schemas.generation import SkillOptimizationGoal
from src.core.sai_client import SaiLibraryClient
from src.domain.entities import TargetAgent


class OptimizeSkillUseCase:
    def __init__(self, sai_client: SaiLibraryClient) -> None:
        self._sai_client = sai_client

    async def execute(
        self,
        skill_markdown: str,
        goals: list[SkillOptimizationGoal],
        target_agent: TargetAgent | None,
    ) -> tuple[str, TargetAgent | None, TargetAgent, list[str]]:
        detected = self.detect_target_agent(skill_markdown)
        effective_target = target_agent or detected or TargetAgent.CLAUDE

        prompt = self._build_prompt(
            skill_markdown=skill_markdown,
            goals=goals,
            target_agent=effective_target,
        )
        optimized_markdown = await self._sai_client.execute(prompt)

        quality_notes = [
            "Texto revisado para maior clareza, consistência e gramática.",
            "Objetivos e instruções fortalecidos com padrão profissional e determinístico.",
            "Checklist e testes práticos exigidos para validação da execução.",
        ]

        return optimized_markdown.strip(), detected, effective_target, quality_notes

    def detect_target_agent(self, skill_markdown: str) -> TargetAgent | None:
        text = skill_markdown.lower()

        rules: list[tuple[TargetAgent, list[str]]] = [
            (TargetAgent.COPILOT, ["copilot-instructions", ".github/copilot-instructions.md"]),
            (TargetAgent.KIRO, [".kiro/steering", "kiro ide"]),
            (TargetAgent.CURSOR, [".cursor/rules", ".mdc", "cursor"]),
            (TargetAgent.WINDSURF, [".windsurfrules", "windsurf"]),
            (TargetAgent.VERTEX_AI, ["vertex ai", "system_instruction.json"]),
            (TargetAgent.GENERIC_OPENAI, ["assistants api", "system_prompt.md", "tools.json"]),
            (TargetAgent.FABRIC_PYSPARK_NOTEBOOK, ["pyspark", "microsoft fabric", "notebook_usage.md"]),
            (TargetAgent.CLAUDE, ["claude", "skill.md"]),
        ]

        for agent, signatures in rules:
            if any(signature in text for signature in signatures):
                return agent

        return None

    def _goal_instructions(self, goals: list[SkillOptimizationGoal]) -> str:
        mapping: dict[SkillOptimizationGoal, str] = {
            SkillOptimizationGoal.TOKEN_REDUCTION: (
                "- Reduzir consumo de tokens com divulgação progressiva, frases curtas e remoção de redundâncias."
            ),
            SkillOptimizationGoal.EXECUTION_DEPTH: (
                "- Aumentar robustez da execução com passos completos, pré-condições, pós-condições e tratamento de erros."
            ),
            SkillOptimizationGoal.QUALITY_IMPROVEMENT: (
                "- Elevar qualidade geral com linguagem técnica sênior, estrutura clara e consistência terminológica."
            ),
            SkillOptimizationGoal.OBJECTIVE_REFINEMENT: (
                "- Refinar objetivo com escopo, critérios de aceitação e limites explícitos."
            ),
            SkillOptimizationGoal.DETERMINISTIC_INSTRUCTIONS: (
                "- Converter instruções para formato determinístico: ação + condição + saída esperada."
            ),
            SkillOptimizationGoal.PRACTICAL_TESTS_CHECKLIST: (
                "- Adicionar testes práticos e checklist de verificação final."
            ),
            SkillOptimizationGoal.DIRECT_NEGATIVE_INSTRUCTIONS: (
                "- Incluir instruções negativas diretas (NÃO fazer X) no lugar de explicações vagas."
            ),
            SkillOptimizationGoal.REUSE_AND_ANTI_DUPLICATION: (
                "- Reforçar reaproveitamento e anti-duplicação com diff mínimo e bloqueio de código morto."
            ),
        }
        return "\n".join(mapping[goal] for goal in goals)

    def _token_policy_block(self) -> str:
        return (
            "POLÍTICA CONDICIONAL — REDUÇÃO DE TOKENS (aplicar apenas se goal token_reduction estiver selecionado):\n"
            "1. Priorize densidade informacional: remova títulos/explicações/checklists redundantes; "
            "não repita regra; frases curtas e determinísticas; nunca remova regra crítica.\n"
            "2. Otimize para decisão do agente (não para documentação): priorize escopo, roteamento, "
            "regras críticas, workflow, stop conditions e critérios de saída; evite conteúdo decorativo.\n"
            "3. Reduza acoplamento: evite hardcode de caminho, alias, máquina e ambiente quando não essencial; "
            "mantenha somente premissas garantidas e necessárias.\n"
            "4. Evite ambiguidade por compactação excessiva: mantenha explícito o que validar/produzir.\n"
            "5. Evite duplicidade entre skills: se já pertence a skill especializada, referencie e não copie procedimento completo.\n"
            "6. Não duplicar detalhes operacionais de publicação/execução que já pertencem ao $fabric-full-agent; "
            "na skill orquestradora, apenas roteie e referencie esse agente.\n"
            "7. Aplique o princípio 'Token Economy Without Decision Loss': menor SKILL possível sem perda de decisão crítica, "
            "roteamento, validação, bloqueios, anti-alucinação e consistência com demais skills.\n"
        )

    def _execution_policy_block(self) -> str:
        return (
            "POLÍTICA CONDICIONAL — ROBUSTEZ/TEMPO TOTAL/QUALIDADE (aplicar apenas se goal execution_depth estiver selecionado):\n"
            "1. Preserve integralmente regras que protegem qualidade: dependências obrigatórias, limites de escopo, "
            "autorização para escrita/execução, validação local, validação de dados, critérios de bloqueio, ordem de etapas, "
            "condições de publicação/execução, pré-requisitos e regras anti-alucinação.\n"
            "2. Use stop conditions explícitas, objetivas e verificáveis para bloquear risco de artefato incorreto, "
            "execução indevida ou resultado não confiável.\n"
            "3. Separe orquestração de implementação: skill principal roteia ordem/pré-condições/bloqueios; "
            "detalhes operacionais ficam em skills especializadas; referencie em vez de duplicar.\n"
            "4. Otimize workflow com sequência curta e determinística, sem repetição, com dependências entre fases; "
            "não avance sem validação da fase anterior; diferencie geração local, validação local, publicação, execução e pós-validação.\n"
            "5. Preserve autorização por turno para operações destrutivas/de escrita/execução; não herde autorização de turnos anteriores.\n"
            "6. Faça revisão de impacto antes de finalizar: tokens removidos, regras críticas preservadas/removidas, ambiguidades, "
            "riscos de artefatos incorretos, execução prematura, duplicidade, acoplamento, impacto em latência/tempo total e reutilização.\n"
            "7. Ao otimizar skill existente: não faça reescrita estética; identifique redundante vs crítico vs pertencente a outra skill; "
            "preserve regras críticas; remova apenas o que não muda decisão/comportamento; entregue versão final completa.\n"
            "8. Ao criar skill nova: prefira estrutura mínima com frontmatter preciso, referências externas só quando necessário, "
            "routing/boundaries, regras operacionais críticas, workflow determinístico e stop conditions.\n"
            "9. Regra de decisão final (ordem obrigatória): correção e segurança operacional -> robustez e prevenção de erros -> "
            "clareza determinística -> eliminação de duplicidade -> redução de tokens -> otimização adicional de latência.\n"
            "A redução de tokens nunca pode remover regra necessária para geração correta ou para bloquear execução inválida.\n"
        )

    def _conditional_policy_instructions(self, goals: list[SkillOptimizationGoal]) -> str:
        blocks: list[str] = []
        if SkillOptimizationGoal.TOKEN_REDUCTION in goals:
            blocks.append(self._token_policy_block())
        if SkillOptimizationGoal.EXECUTION_DEPTH in goals:
            blocks.append(self._execution_policy_block())

        if not blocks:
            return (
                "Nenhuma política condicional de redução de token ou robustez/tempo foi selecionada.\n"
                "NÃO aplicar técnicas específicas desses dois grupos nesta otimização.\n"
            )

        return "\n".join(blocks)

    def _build_prompt(
        self,
        skill_markdown: str,
        goals: list[SkillOptimizationGoal],
        target_agent: TargetAgent,
    ) -> str:
        goals_block = self._goal_instructions(goals)

        conditional_policies = self._conditional_policy_instructions(goals)
        return (
            "Você é um especialista em engenharia de prompts e skills enterprise.\n"
            "Objetivo: otimizar a SKILL.md enviada pelo usuário sem perder intenção funcional.\n\n"
            "Regras obrigatórias:\n"
            "1) Preserve o padrão do agente/IDE alvo e o formato markdown do arquivo.\n"
            "2) Corrija português, clareza e precisão técnica.\n"
            "3) Aplique APENAS as políticas condicionais permitidas pelos goals selecionados.\n"
            "4) Se um goal condicional não foi selecionado, não aplique a política correspondente.\n"
            "5) Evite prolixidade e redundância sem perder regras críticas de decisão.\n"
            "6) Entregue APENAS o markdown final otimizado, sem comentários extras.\n\n"
            "4) Evite prolixidade e redundância sem perder regras críticas de decisão.\n"
            "5) Entregue APENAS o markdown final otimizado, sem comentários extras.\n\n"
            f"Agente/IDE alvo: {target_agent.value}\n"
            "Políticas condicionais ativas para esta execução:\n"
            f"{conditional_policies}\n"
            "clareza determinística -> eliminação de duplicidade -> redução de tokens -> otimização adicional de latência.\n"
            "A redução de tokens nunca pode remover regra necessária para geração correta ou para bloquear execução inválida.\n\n"
            "SKILL original do usuário:\n"
            "```markdown\n"
            f"{skill_markdown}\n"
            "```\n"
        )
