from src.domain.entities import Material, Project

ANTI_DUPLICATION_BLOCK = """## Protocolo Anti-Duplicacao e Continuidade
1. Antes de implementar algo, leia o historico de implementacao (changelog, commits recentes, IMPLEMENTATION_LOG.md ou equivalente).
2. Antes de criar funcao/modulo/endpoint, busque no codigo-base se algo equivalente ja existe; se existir, reutilize ou estenda.
3. Aplique apenas a menor mudanca necessaria (diff minimo).
4. Avalie qualidade no contexto do projeto inteiro, nao apenas no diff.
5. Registre a mudanca em IMPLEMENTATION_LOG.md com data, resumo e arquivos tocados.
6. Nunca gere codigo morto ou implementacoes por via das duvidas.
"""


def materials_table(materials: list[Material]) -> str:
    lines = ["| Nome | Tipo | Por que importa |", "|---|---|---|"]
    for item in materials:
        lines.append(f"| {item.name} | {item.connector_type.value} | {item.description} |")
    return "\n".join(lines)


def senior_rules() -> str:
    return """## Padroes Senior Obrigatorios
- Respeite a arquitetura existente e evolua por camadas quando aplicavel.
- Use nomenclatura clara e consistente.
- Cubra nova regra de negocio com testes automatizados.
- Trate erros explicitamente; nao silencie falhas.
- Atualize README e docstrings publicas quando houver mudanca relevante.
- Use logs estruturados em producao.
- Nao commite segredos; valide toda entrada externa.
"""


def usage_prompt(project: Project) -> str:
    return (
        f"Usando a skill gerada para {project.skill_name}, trabalhe no dominio {project.domain} "
        "seguindo estritamente regras de anti-duplicacao, diff minimo e registro em IMPLEMENTATION_LOG.md."
    )
