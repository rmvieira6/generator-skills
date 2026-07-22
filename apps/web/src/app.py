from __future__ import annotations

import streamlit as st

from api_client import SkillForgeApiClient

st.set_page_config(page_title="Skill Forge", layout="wide")

client = SkillForgeApiClient()

FIELD_HELP: dict[str, str] = {
    "agents": "Escolha para quais agentes o artefato sera gerado. Voce pode selecionar mais de um.",
    "skill_name": "Nome interno da skill/instrucao gerada. Exemplo: Revisor Backend Node.",
    "objective": "Frase curta com resultado esperado. Exemplo: Revisar PRs com foco em seguranca e testes.",
    "domain": "Area principal de atuacao. Valor padrao 'backend'. Ajuste para dados, QA, DevOps etc.",
    "autonomy_level": (
        "Nivel de autonomia do agente. Exemplo: suggest_only (so sugerir), "
        "apply_changes (propor/aplicar alteracoes), run_commands (executar comandos)."
    ),
    "constraints": "Guardrails obrigatorios. Exemplo: nao mexer em migrations, nao alterar contratos de API.",
    "description": "Descricao mais completa do que a skill deve fazer. Minimo de 20 caracteres.",
    "connector_type": "Tipo da fonte de contexto que o agente deve consultar.",
    "material_name": "Nome curto para identificar o material na lista.",
    "material_description": "Explique por que esse material importa para a geracao. Campo obrigatorio.",
}

METADATA_HELP: dict[str, str] = {
    "path": "Caminho do arquivo ou pasta relevante.",
    "host": "Servidor do servico (sem protocolo).",
    "port": "Porta de conexao.",
    "database": "Nome do banco/schema principal.",
    "schema": "Schema alvo (ex.: public).",
    "username": "Usuario tecnico de acesso.",
    "password": "Senha/segredo. Usada apenas para teste; nao e persistida.",
    "base_url": "URL base da API REST.",
    "endpoint": "Endpoint da API GraphQL.",
    "auth_type": "Tipo de autenticacao (none, bearer, basic etc.).",
    "token": "Token temporario para teste de conectividade.",
    "provider": "Provedor de storage (s3, gcs, azure).",
    "bucket": "Bucket/container da origem.",
    "region": "Regiao do servico de storage.",
    "access_key": "Credencial de acesso. Nao persistida.",
    "secret_key": "Segredo da credencial. Nao persistido.",
    "folder_id": "Identificador da pasta remota (Drive).",
    "service_account_json": "JSON de service account para teste (nao persistido).",
    "workspace": "Workspace da ferramenta conectada.",
    "space_key": "Space key do Confluence.",
    "url": "URL do repositorio Git.",
    "branch": "Branch principal para leitura de contexto.",
}


def initialize_state() -> None:
    defaults: dict[str, object] = {
        "step": 1,
        "materials": [],
        "result": [],
        "selected_agents": [],
        "skill_name": "",
        "objective": "",
        "domain": "backend",
        "autonomy_level": "suggest_only",
        "constraints": "",
        "description": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def clear_for_new_run() -> None:
    st.session_state.step = 1
    st.session_state.result = []
    st.session_state.materials = []
    st.rerun()


initialize_state()

catalog = client.catalog()
agents = catalog.get("agents", [])
connectors = catalog.get("connectors", [])

st.title("Skill Forge")
st.caption("Gerador de SKILL.md e instrucoes para Claude, Copilot, Cursor, Vertex, Windsurf e mais.")
st.markdown("1. Selecionar agente | 2. Descrever artefato | 3. Materiais | 4. Revisar e gerar")

with st.container(border=True):
    if st.session_state.step == 1:
        st.subheader("Passo 1: Selecionar agente-alvo")
        st.session_state.selected_agents = st.multiselect(
            "Agentes",
            options=[agent["id"] for agent in agents],
            format_func=lambda value: next((a["label"] for a in agents if a["id"] == value), value),
            default=st.session_state.selected_agents,
            key="step1_selected_agents",
            help=FIELD_HELP["agents"],
        )

        _, right_col = st.columns([1, 1])
        with right_col:
            if st.button(
                "Continuar para passo 2",
                key="step1_next",
                disabled=len(st.session_state.selected_agents) == 0,
            ):
                go_to(2)

    elif st.session_state.step == 2:
        st.subheader("Passo 2: Descrever artefato")
        st.session_state.skill_name = st.text_input(
            "Nome da skill",
            st.session_state.skill_name,
            key="step2_skill_name",
            help=FIELD_HELP["skill_name"],
        )
        st.session_state.objective = st.text_input(
            "Objetivo (1 frase)",
            st.session_state.objective,
            key="step2_objective",
            help=FIELD_HELP["objective"],
        )
        st.session_state.domain = st.text_input(
            "Dominio",
            st.session_state.domain,
            key="step2_domain",
            help=FIELD_HELP["domain"],
        )
        st.session_state.autonomy_level = st.text_input(
            "Nivel de autonomia",
            st.session_state.autonomy_level,
            key="step2_autonomy",
            help=FIELD_HELP["autonomy_level"],
        )
        st.session_state.constraints = st.text_area(
            "Restricoes/guardrails",
            st.session_state.constraints,
            key="step2_constraints",
            help=FIELD_HELP["constraints"],
        )
        st.session_state.description = st.text_area(
            "Descricao de alto nivel",
            st.session_state.description,
            height=180,
            key="step2_description",
            help=FIELD_HELP["description"],
        )

        left_col, right_col = st.columns(2)
        with left_col:
            if st.button("Voltar para passo 1", key="step2_back"):
                go_to(1)
        with right_col:
            is_valid = (
                bool(st.session_state.skill_name.strip())
                and bool(st.session_state.objective.strip())
                and len(st.session_state.description.strip()) >= 20
            )
            if st.button("Continuar para passo 3", key="step2_next", disabled=not is_valid):
                go_to(3)

    elif st.session_state.step == 3:
        st.subheader("Passo 3: Adicionar materiais")
        connector_ids = [item["id"] for item in connectors]
        selected_connector = st.selectbox(
            "Tipo de conector",
            options=connector_ids,
            key="step3_connector",
            help=FIELD_HELP["connector_type"],
        )
        name = st.text_input("Nome do material", key="step3_name", help=FIELD_HELP["material_name"])
        description = st.text_area(
            "Descricao obrigatoria",
            key="step3_description",
            help=FIELD_HELP["material_description"],
        )

        fields = next((item["fields"] for item in connectors if item["id"] == selected_connector), [])
        metadata: dict[str, str] = {}
        for field in fields:
            metadata[field] = st.text_input(
                field,
                key=f"step3_field_{field}",
                help=METADATA_HELP.get(field, "Campo tecnico de configuracao do conector."),
            )

        add_col, test_col = st.columns(2)
        with add_col:
            if st.button("Adicionar material", key="step3_add"):
                if not description.strip():
                    st.error("Descricao do material e obrigatoria.")
                else:
                    st.session_state.materials.append(
                        {
                            "connector_type": selected_connector,
                            "name": name,
                            "description": description,
                            "connection_metadata": metadata,
                        }
                    )
                    st.success("Material adicionado")
        with test_col:
            if st.button("Testar conexao", key="step3_test"):
                result = client.test_connection(selected_connector, metadata)
                st.info(result.get("detail", "Sem detalhe"))

        st.write("Materiais adicionados:")
        st.json(st.session_state.materials)

        left_col, right_col = st.columns(2)
        with left_col:
            if st.button("Voltar para passo 2", key="step3_back"):
                go_to(2)
        with right_col:
            if st.button("Continuar para passo 4", key="step3_next"):
                go_to(4)

    elif st.session_state.step == 4:
        st.subheader("Passo 4: Revisar e gerar")
        payload = {
            "skill_name": st.session_state.skill_name,
            "objective": st.session_state.objective,
            "domain": st.session_state.domain,
            "autonomy_level": st.session_state.autonomy_level,
            "constraints": st.session_state.constraints,
            "high_level_description": st.session_state.description,
            "target_agents": st.session_state.selected_agents,
            "materials": st.session_state.materials,
        }
        st.json(payload)

        left_col, right_col = st.columns(2)
        with left_col:
            if st.button("Voltar para passo 3", key="step4_back"):
                go_to(3)
        with right_col:
            if st.button("Gerar artefatos", type="primary", key="step4_generate"):
                with st.status("Gerando...", expanded=True) as status:
                    status.write("Enviando requisicao para API")
                    response = client.generate(payload)
                    st.session_state.result = response.get("items", [])
                    status.update(label="Concluido", state="complete")

                st.rerun()

if st.session_state.result:
    st.divider()
    st.subheader("Resultado")
    for item in st.session_state.result:
        st.markdown(f"### {item['target_agent']}")
        st.write("Arquivos:", ", ".join(item.get("generated_files", [])))
        st.markdown(f"[Baixar pacote (.zip)]({client.download_url(item['download_token'])})")
        st.markdown("#### Preview")
        st.code(item.get("preview_markdown", ""), language="markdown")
        st.markdown("#### Prompt sugerido")
        st.code(item.get("suggested_prompt", ""), language="markdown")

    if st.button("Nova geracao", key="result_new_generation"):
        clear_for_new_run()
