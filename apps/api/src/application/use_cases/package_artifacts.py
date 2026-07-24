from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from src.domain.entities import GeneratedFile, Project, TargetAgent

# ---------------------------------------------------------------------------
# Instruções por IDE/Ambiente — linguagem simples para usuários leigos
# ---------------------------------------------------------------------------

_AGENT_LABEL: dict[TargetAgent, str] = {
    TargetAgent.CLAUDE: "Claude / Claude.ai",
    TargetAgent.KIRO: "Kiro IDE",
    TargetAgent.COPILOT: "GitHub Copilot (VS Code)",
    TargetAgent.CURSOR: "Cursor",
    TargetAgent.VERTEX_AI: "Vertex AI Agent Builder",
    TargetAgent.WINDSURF: "Windsurf",
    TargetAgent.GENERIC_OPENAI: "OpenAI / Assistants API",
    TargetAgent.FABRIC_PYSPARK_NOTEBOOK: "Microsoft Fabric PySpark Notebook",
}

_INSTALL_STEPS: dict[TargetAgent, str] = {
    TargetAgent.CLAUDE: """\
## Como instalar no Claude / Claude.ai

1. Localize o arquivo `SKILL.md` neste pacote.
2. No Claude.ai, abra **Projects** → selecione ou crie um projeto.
3. Vá em **Project Instructions** e cole o conteúdo de `SKILL.md`.
4. Salve. A skill estará ativa para todas as conversas do projeto.

> **Usando o Skill Forge com deploy automático:** clique em "Instalar automaticamente"
> na tela de resultados, informe o diretório do projeto e selecione Claude.
> O arquivo será copiado para o local correto.""",

    TargetAgent.KIRO: """\
## Como instalar no Kiro IDE

1. Localize o arquivo `.kiro/steering/<nome-da-skill>.md` neste pacote.
2. Copie-o para a pasta `.kiro/steering/` na raiz do seu projeto.
   - Se a pasta não existir, crie-a manualmente.
3. Reabra o workspace no Kiro IDE.
4. A skill será carregada **automaticamente** em todas as sessões.

> **Usando o Skill Forge com deploy automático:** clique em "Instalar automaticamente",
> informe o diretório raiz do seu projeto e selecione Kiro. O arquivo será copiado
> e ficará pronto para uso imediato.""",

    TargetAgent.COPILOT: """\
## Como instalar no GitHub Copilot (VS Code)

1. Localize o arquivo `.github/copilot-instructions.md` neste pacote.
2. Copie-o para a pasta `.github/` na raiz do seu repositório.
   - Se a pasta não existir, crie-a.
3. Reabra o VS Code — o Copilot lerá as instruções automaticamente.
4. Não é necessário configurar nada mais.

> **Requisito:** GitHub Copilot ativo na sua conta GitHub.""",

    TargetAgent.CURSOR: """\
## Como instalar no Cursor

1. Localize os arquivos `.cursor/rules/core.mdc` e `.cursor/rules/anti-duplication.mdc`.
2. Copie a pasta `.cursor/` para a raiz do seu projeto.
3. Copie também `.cursorrules` para a raiz (compatibilidade com versões antigas).
4. Reabra o projeto no Cursor — as regras serão carregadas automaticamente.

> Cursor 0.43+ usa `.cursor/rules/*.mdc`. Versões anteriores usam `.cursorrules`.""",

    TargetAgent.VERTEX_AI: """\
## Como instalar no Vertex AI Agent Builder

1. Localize o arquivo `vertex/system_instruction.json` neste pacote.
2. Abra o [Vertex AI Agent Builder](https://console.cloud.google.com/gen-app-builder) no GCP.
3. Selecione ou crie um Agente.
4. Em **System Instruction**, cole o valor do campo `"text"` dentro de `"parts"`.
5. Configure as ferramentas (functions) a partir da seção `"tools"` do JSON.
6. Salve e publique o agente.""",

    TargetAgent.WINDSURF: """\
## Como instalar no Windsurf

1. Localize o arquivo `.windsurfrules` neste pacote.
2. Copie-o para a raiz do seu projeto.
3. Reabra o workspace no Windsurf — as regras serão carregadas automaticamente.""",

    TargetAgent.GENERIC_OPENAI: """\
## Como instalar via OpenAI / Assistants API

1. **System Prompt:** use o conteúdo de `system_prompt.md` como System Prompt do seu Assistant.
2. **Ferramentas:** importe as definições de `tools.json` na seção "Functions" do Assistant.
3. No [Playground da OpenAI](https://platform.openai.com/playground), cole o system prompt
   e configure as functions.
4. Salve o Assistant e use o ID gerado nas chamadas de API.""",

    TargetAgent.FABRIC_PYSPARK_NOTEBOOK: """\
## Como instalar no Microsoft Fabric PySpark Notebook

1. Localize o arquivo `fabric/SKILL.md` neste pacote.
2. No Microsoft Fabric, abra o seu Notebook.
3. Cole o conteúdo de `SKILL.md` no contexto do assistente de IA do notebook.
4. Consulte `fabric/NOTEBOOK_USAGE.md` para instruções detalhadas de uso.
5. Versione a skill junto ao notebook no repositório Git da equipe.""",
}


def _usage_readme(agent: TargetAgent, project: Project, suggested_prompt: str) -> str:
    label = _AGENT_LABEL.get(agent, agent.value)
    steps = _INSTALL_STEPS.get(
        agent,
        "Consulte a documentação do seu agente para instruções de instalação.",
    )

    return f"""\
# Como usar esta Skill — {label}

**Projeto:** {project.skill_name}
**Objetivo:** {project.objective}

---

{steps}

---

## Prompt sugerido para começar agora

Cole este prompt na primeira mensagem após ativar a skill:

```
{suggested_prompt}
```

---

## Arquivos deste pacote

| Arquivo | Descrição |
|---|---|
| `README_USO.md` | Este guia de instalação e uso |
| `PROMPT_SUGERIDO.md` | Prompt de ativação isolado |
| `PROJECT_SUMMARY.md` | Resumo do projeto gerado |
| _(artefatos específicos do agente)_ | Os arquivos da skill propriamente ditos |

---

## Próximos passos

1. Instale os artefatos conforme as instruções acima.
2. Use o prompt sugerido para ativar a skill.
3. Ao modificar o domínio ou regras, regenere a skill no Skill Forge.
4. Versione os artefatos junto ao código do projeto.

> Gerado pelo **Skill Forge** — Fábrica de Skills Stefanini.
"""


def package_as_zip(
    files: list[GeneratedFile],
    project: Project,
    agent: TargetAgent,
    suggested_prompt: str,
) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, mode="w", compression=ZIP_DEFLATED) as zip_file:
        for generated in files:
            zip_file.writestr(generated.path, generated.content)

        zip_file.writestr(
            "README_USO.md",
            _usage_readme(agent, project, suggested_prompt),
        )
        zip_file.writestr("PROMPT_SUGERIDO.md", suggested_prompt)
        zip_file.writestr(
            "PROJECT_SUMMARY.md",
            f"# {project.skill_name}\n\n**Objetivo:** {project.objective}\n\n**Domínio:** {project.domain}\n",
        )

    return stream.getvalue()
