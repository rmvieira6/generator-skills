# Architecture (ADR-lite)

## Decisoes
1. FastAPI + Clean Architecture para separar dominio, casos de uso e adaptadores.
2. Frontend em Streamlit para manter stack 100% Python e reduzir complexidade operacional.
2. SAI Library encapsulada em `SaiLibraryClient` com retry exponencial.
3. Anti-duplicacao por hash de requisicao (agente + descricao + materiais).
4. Persistencia leve local em SQLite com SQLModel para historico de jobs.
5. Templates puros por agente para testabilidade isolada.

## Fluxo principal
1. Frontend coleta dados em wizard de 4 passos.
2. API valida materiais e limites de configuracao.
3. Use case calcula hashes e consulta historico.
4. Se hash identico: retorna cache.
5. Se novo: monta prompt a partir do `SKILL.master.md`, chama SAI, renderiza template do agente.
6. Empacota `zip` com artefatos + `README_USO.md` + `PROMPT_SUGERIDO.md`.
7. Disponibiliza download por token temporario.

## Trade-offs
- Armazenamento de artefatos em JSON no historico simplifica cache e evita dependencia externa.
- Store de download em memoria privilegia privacidade/ephemeralidade, mas nao e distribuida para multi-instancia.
- Endpoint de teste de conexao faz validacao leve de parametros; pode evoluir para probes reais por conector.
- Sem Docker por escolha de execucao local direta, exigindo setup manual de Python nos dois apps.
