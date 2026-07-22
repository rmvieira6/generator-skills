from src.domain.entities import GeneratedFile, Material, Project
from src.infrastructure.agent_templates.common import ANTI_DUPLICATION_BLOCK, materials_table, senior_rules


def render(project: Project, materials: list[Material], generated_core: str) -> list[GeneratedFile]:
    content = f"""# Instrucoes de Repositorio - {project.skill_name}

Aplique estas instrucoes sempre ao trabalhar neste repositorio.

## Objetivo
{project.objective}

## Materiais de Contexto
{materials_table(materials)}

{ANTI_DUPLICATION_BLOCK}

{senior_rules()}

## Restricoes
{project.constraints or '- Nenhuma restricao adicional.'}

## Instrucoes Operacionais
- Responda de forma direta e acionavel.
- Nao invente requisitos fora do escopo.
- Ao concluir, descreva arquivos alterados e testes executados.

## Nucleo Gerado
{generated_core}
"""
    return [GeneratedFile(path=".github/copilot-instructions.md", content=content)]
