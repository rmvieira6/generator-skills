# Skill Forge

Skill Forge gera artefatos de contexto para agentes de IA (SKILL.md, regras do Cursor, copilot-instructions, system_instruction do Vertex, etc.) a partir de um wizard de 4 passos.

## Stack
- Backend: FastAPI (Python 3.11+)
- Frontend: Streamlit (Python)
- LLM: SAI Library (via wrapper interno)
- Historico/anti-duplicacao: SQLite + SQLModel

## Como rodar
1. Garanta Python 3.11+ instalado e entre na pasta do projeto: `cd skill-forge`.
2. Instale tudo por um unico arquivo: `pip install -r requirements.txt`.
3. Em um terminal (na raiz `skill-forge`), rode a API: `./start_api.ps1`.
4. Em outro terminal (na raiz `skill-forge`), rode o Streamlit: `./start_web.ps1`.
5. Abra a URL exibida pelo Streamlit (padrao: http://localhost:8501).

Atalho manual (se nao quiser os scripts):
- `uvicorn src.main:app --reload --port 8000 --app-dir apps/api`
- `streamlit run apps/web/src/app.py`

## Estabilidade do Wizard
- A navegacao agora e por botoes por passo, com chaves unicas.
- O wizard nao troca mais de passo durante digitacao em campos do formulario.

## Frontend Streamlit
- Wizard de 4 passos com multi-selecao de agentes.
- Cadastro de materiais com descricao obrigatoria e teste de conexao.
- Revisao de payload, geracao e links de download por agente.
- Preview do artefato e prompt sugerido na propria interface.

## Estrategia de geracao
- `packages/skill-master-template/SKILL.master.md` e a unica fonte de verdade para o meta-prompt.
- Cada agente alvo recebe template nativo em `apps/api/src/infrastructure/agent_templates/`.
- Jobs identicos sao reaproveitados por hash para evitar custo redundante.
- Mudancas parciais de materiais geram hint de diff incremental para a SAI Library.

## Comandos uteis
- `make dev-api`
- `make dev-web`
- `pip install -r requirements.txt`
- `make lint`
- `make test`
- `make build`

## Seguranca
- Nunca hardcode segredos.
- Nunca persistir senha/token em texto puro no historico.
- `.env` esta no `.gitignore`.
