# ⚡ Skill Forge — Fábrica de Skills Stefanini

Gerador padronizado de `SKILL.md` e instruções de agente para IDEs e plataformas de IA.
Produz artefatos prontos para uso no Claude, Kiro, Copilot, Cursor, Windsurf, Vertex AI,
OpenAI Assistants e Microsoft Fabric — com economia de tokens, qualidade sênior e deploy automático.

---

## IDEs e Ambientes Suportados

| Agente | Artefato gerado | Onde fica |
|---|---|---|
| Claude / Claude.ai | `SKILL.md` | Raiz do projeto ou Project Instructions |
| **Kiro IDE** | `.kiro/steering/<nome>.md` | `.kiro/steering/` do workspace |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/` do repositório |
| Cursor | `.cursor/rules/core.mdc` + `anti-duplication.mdc` | `.cursor/rules/` |
| Windsurf | `.windsurfrules` | Raiz do projeto |
| Vertex AI Agent Builder | `vertex/system_instruction.json` | Importar no console GCP |
| OpenAI / Assistants API | `system_prompt.md` + `tools.json` | Usar via API |
| Microsoft Fabric PySpark | `fabric/SKILL.md` + `NOTEBOOK_USAGE.md` | Junto ao notebook |

---

## Pré-requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recomendado) ou pip
- Credenciais da SAI Library (`.env`)

---

## Instalação rápida

```powershell
# Clone o repositório
git clone <url-do-repo>
cd generator-skills

# Copie e edite as variáveis de ambiente
Copy-Item .env.example .env
# Edite .env com sua SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID

# Instale dependências (backend)
cd apps/api
pip install -e ".[dev]"

# Instale dependências (frontend)
cd ../web
pip install -e ".[dev]"
```

---

## Executar

```powershell
# Terminal 1 — Backend (API)
cd apps/api
uvicorn src.main:app --reload --port 8000

# Terminal 2 — Frontend (UI)
cd apps/web
streamlit run src/app.py
```

Acesse: [http://localhost:8501](http://localhost:8501)

Ou use os scripts prontos:

```powershell
.\start_api.ps1   # inicia o backend
.\start_web.ps1   # inicia o frontend
```

---

## Como usar — Wizard de 5 passos

```
1. Agente     → Selecione o IDE/ambiente de destino
2. Descrição  → Nome, objetivo, domínio, autonomia e restrições
3. Materiais  → Fontes de contexto (arquivos, APIs, bancos...)
4. Revisar    → Confirme e clique em "Gerar artefatos"
5. Instalar   → Baixe o .zip ou instale automaticamente no diretório do projeto
```

### Deploy automático (Passo 5)
No passo 5, informe o **caminho completo** da pasta raiz do seu projeto. O Skill Forge:
1. Copia todos os artefatos para os locais corretos conforme a IDE selecionada.
2. Exibe instruções específicas de como ativar a skill naquela IDE.
3. Indica o que fazer a seguir para começar a usar imediatamente.

---

## Qualidade dos artefatos gerados

Todos os artefatos seguem automaticamente:

- **Skill Graph** — grafo mermaid de dependências entre seções
- **Wikilinks** — `[[Seção]]` para referência sem repetição de conteúdo
- **Token Economy** — progressive disclosure, linguagem telegráfica, zero redundância
- **Protocolo Anti-Duplicação** — diff mínimo, IMPLEMENTATION_LOG.md, sem código morto
- **Padrões Sênior** — separação de camadas, testes, tratamento de erro, segurança

---

## Arquitetura

```
generator-skills/
├── apps/
│   ├── api/               # FastAPI — Clean Architecture
│   │   └── src/
│   │       ├── api/       # Rotas e schemas (REST)
│   │       ├── application/  # Use cases (generate, package, validate, deploy)
│   │       ├── core/      # Config + SAI Library client
│   │       ├── domain/    # Entidades e value objects
│   │       └── infrastructure/
│   │           ├── agent_templates/  # Um módulo por agente
│   │           └── persistence/      # SQLite via SQLModel
│   └── web/               # Streamlit — wizard de 5 passos
│       └── src/app.py
├── packages/
│   └── skill-master-template/
│       └── SKILL.master.md   # Template mestre do prompt LLM
├── .kiro/steering/
│   └── skill-forge.md        # Steering file do Kiro IDE
├── agents.yaml               # Catálogo de agentes suportados
├── connectors.yaml           # Catálogo de conectores disponíveis
└── .env.example              # Variáveis de ambiente necessárias
```

Veja [ARCHITECTURE.md](ARCHITECTURE.md) para decisões de design detalhadas.

---

## Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `SAI_LIBRARY_BASE_URL` | URL base da SAI Library |
| `SAI_LIBRARY_API_KEY` | Chave de API da SAI Library |
| `SAI_LIBRARY_TEMPLATE_ID` | ID do template de geração |
| `DATABASE_URL` | SQLite local (padrão: `sqlite:///./skillforge_history.db`) |
| `MAX_MATERIALS_PER_PROJECT` | Limite de materiais por skill (padrão: 20) |

---

## Adicionar novo agente

1. Crie `apps/api/src/infrastructure/agent_templates/<nome>.py` com função `render(project, materials, generated_core) -> list[GeneratedFile]`.
2. Importe os blocos de `common.py` — nunca duplique inline.
3. Adicione o valor em `TargetAgent` em `domain/entities.py`.
4. Registre em `infrastructure/agent_templates/registry.py`.
5. Adicione entrada em `agents.yaml`.
6. Adicione instruções de uso em `application/use_cases/package_artifacts.py`.
