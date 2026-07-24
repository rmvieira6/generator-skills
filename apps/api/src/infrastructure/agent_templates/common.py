from src.domain.entities import Material, Project


# ---------------------------------------------------------------------------
# Blocos reutilizáveis — importe-os; nunca duplique inline nos templates
# ---------------------------------------------------------------------------

ANTI_DUPLICATION_BLOCK = """\
## Protocolo Anti-Duplicação → [[Anti-Duplicação]]
1. Leia `IMPLEMENTATION_LOG.md` antes de qualquer implementação.
2. Busque equivalente no código-base antes de criar — se existir, reutilize.
3. Diff mínimo: menor mudança que resolve; não reescreva arquivos inteiros.
4. Avalie consistência com nomenclatura, arquitetura e testes do projeto.
5. Registre ao final: data, resumo e arquivos tocados em `IMPLEMENTATION_LOG.md`.
6. **Nunca gere código morto** ou implementações por precaução.\
"""

TOKEN_ECONOMY_BLOCK = """\
## Regras de Token Economy → [[Token Economy]]
- Progressive disclosure: corpo mínimo; detalhes em seções âncora.
- Wikilinks `[[Seção]]` para referenciar sem copiar conteúdo.
- Linguagem telegráfica e imperativa; sem meta-comentário.
- Tabelas para 3+ itens; bullets só para sequências.
- 1 exemplo por regra; referencie caminhos — não copie conteúdo.
- Constraints como negativos explícitos: "NÃO faça X".\
"""

SENIOR_RULES_BLOCK = """\
## Padrões Sênior → [[Padrões Sênior]]
- Separação de camadas: domínio / aplicação / infraestrutura.
- Nomenclatura consistente e autoexplicativa.
- Testes automatizados para nova lógica de negócio.
- Erro explícito: proibir `except: pass` ou catch silencioso.
- Documentação mínima: README e docstrings públicas atualizados.
- Logs estruturados; sem `print` solto em produção.
- Segurança: nunca commitar segredos; validar toda entrada externa.\
"""


def skill_graph(sections: list[str]) -> str:
    """Gera um Skill Graph Mermaid compacto a partir de uma lista de seções."""
    if len(sections) < 3:
        return ""
    nodes = " --> ".join(f"S{i}[{s}]" for i, s in enumerate(sections))
    return f"```mermaid\ngraph LR\n    {nodes}\n```\n"


def materials_table(materials: list[Material]) -> str:
    if not materials:
        return "_Nenhum material fornecido._"
    lines = ["| Material | Tipo | Por que importa |", "|---|---|---|"]
    for item in materials:
        lines.append(f"| {item.name} | `{item.connector_type.value}` | {item.description} |")
    return "\n".join(lines)


def senior_rules() -> str:
    return SENIOR_RULES_BLOCK


def usage_prompt(project: Project) -> str:
    return (
        f"Ative a skill **{project.skill_name}** no domínio `{project.domain}`. "
        "Siga anti-duplicação, diff mínimo e registre em `IMPLEMENTATION_LOG.md`."
    )
