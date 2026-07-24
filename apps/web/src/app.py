from __future__ import annotations

import streamlit as st

from api_client import SkillForgeApiClient

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Skill Forge — Stefanini",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS customizado — visual profissional
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
/* Fonte e fundo */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

:root {
    --sf-bg: #f3f6fb;
    --sf-surface: #ffffff;
    --sf-text: #0f172a;
    --sf-muted: #475569;
    --sf-border: #dbe4ee;
}

/* Contraste global para evitar texto claro em fundo claro */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fbff 0%, #edf3f9 100%);
}
[data-testid="stAppViewContainer"] .main,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6 {
    color: var(--sf-text);
}

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {
    color: var(--sf-muted) !important;
}

/* Formulários com fundo branco e texto escuro */
.stTextInput > div > div > input,
.stTextArea textarea,
div[data-baseweb="select"] > div {
    background: var(--sf-surface) !important;
    color: var(--sf-text) !important;
    border-color: var(--sf-border) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea textarea::placeholder {
    color: #64748b !important;
}

[data-testid="stExpander"] {
    background: var(--sf-surface);
    border: 1px solid var(--sf-border);
    border-radius: 10px;
}

/* Header */
.sf-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}
.sf-header h1 { margin: 0; font-size: 2rem; letter-spacing: -0.5px; }
.sf-header p  { margin: 0.25rem 0 0; color: #cbd5e1; font-size: 0.95rem; }

/* Steps */
.sf-steps {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.sf-step {
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 2px solid #e2e8f0;
    color: #475569;
    background: white;
}
.sf-step.active {
    background: #1e3a5f;
    color: white;
    border-color: #1e3a5f;
}
.sf-step.done {
    background: #f0fdf4;
    color: #16a34a;
    border-color: #86efac;
}

/* Cards de agente */
.sf-agent-card {
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    color: #0f172a;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.15s;
}
.sf-agent-card:hover { border-color: #1e3a5f; }

/* Alerta de cache */
.sf-cache-badge {
    background: #fef9c3;
    border: 1px solid #fde047;
    border-radius: 6px;
    padding: 0.4rem 0.8rem;
    font-size: 0.82rem;
    color: #713f12;
    display: inline-block;
    margin-bottom: 0.5rem;
}

/* Resultado */
.sf-result-card {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

/* Botão primário */
.stButton > button[kind="primary"] {
    background: #1e3a5f !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2d5a8e !important;
    color: #ffffff !important;
}

/* Botões padrão (ex.: Voltar) com texto claro */
.stButton > button[kind="secondary"] {
    background: #475569 !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #334155 !important;
    color: #ffffff !important;
}

/* Deploy success */
.sf-deploy-success {
    background: #f0fdf4;
    border: 2px solid #86efac;
    border-radius: 10px;
    padding: 1.25rem;
    margin-top: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cliente e dados do catálogo
# ---------------------------------------------------------------------------
client = SkillForgeApiClient()

TOTAL_STEPS = 5

STEP_LABELS = [
    "1 · Agente",
    "2 · Descrição",
    "3 · Materiais",
    "4 · Revisar",
    "5 · Instalar",
]

FIELD_HELP: dict[str, str] = {
    "agents": (
        "Escolha para quais agentes o artefato será gerado. "
        "Você pode selecionar mais de um."
    ),
    "skill_name": "Nome interno da skill. Ex: Revisor Backend Node.",
    "objective": "1 frase com o resultado esperado. Ex: Revisar PRs com foco em segurança.",
    "domain": "Área principal. Ex: backend, dados, QA, DevOps.",
    "autonomy_level": (
        "Nível de autonomia: suggest_only (só sugerir), "
        "apply_changes (propor/aplicar), run_commands (executar comandos)."
    ),
    "constraints": "Guardrails obrigatórios. Ex: não mexer em migrations.",
    "description": "Descrição detalhada do que a skill deve fazer (mínimo 20 caracteres).",
    "connector_type": "Tipo da fonte de contexto que o agente deve consultar.",
    "material_name": "Nome curto para identificar o material.",
    "material_description": "Explique por que este material é importante para a geração.",
}

METADATA_HELP: dict[str, str] = {
    "path": "Caminho do arquivo ou pasta relevante.",
    "host": "Servidor do serviço (sem protocolo).",
    "port": "Porta de conexão.",
    "database": "Nome do banco/schema principal.",
    "schema": "Schema alvo (ex.: public).",
    "username": "Usuário técnico de acesso.",
    "password": "Senha/segredo. Usada apenas para teste; não é persistida.",
    "base_url": "URL base da API REST.",
    "endpoint": "Endpoint da API GraphQL.",
    "auth_type": "Tipo de autenticação (none, bearer, basic etc.).",
    "token": "Token temporário para teste de conectividade.",
    "provider": "Provedor de storage (s3, gcs, azure).",
    "bucket": "Bucket/container da origem.",
    "region": "Região do serviço de storage.",
    "access_key": "Credencial de acesso. Não persistida.",
    "secret_key": "Segredo da credencial. Não persistido.",
    "folder_id": "Identificador da pasta remota (Drive).",
    "service_account_json": "JSON de service account para teste (não persistido).",
    "workspace": "Workspace da ferramenta conectada.",
    "space_key": "Space key do Confluence.",
    "url": "URL do repositório Git.",
    "branch": "Branch principal para leitura de contexto.",
}

# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------
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
        # Deploy
        "deploy_item_idx": None,
        "deploy_done": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def clear_for_new_run() -> None:
    for key in [
        "step", "result", "materials", "selected_agents", "skill_name",
        "objective", "domain", "autonomy_level", "constraints", "description",
        "deploy_item_idx", "deploy_done",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


initialize_state()

# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------
try:
    catalog = client.catalog()
except Exception:
    st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
    st.stop()

agents = catalog.get("agents", [])
connectors = catalog.get("connectors", [])

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="sf-header">
    <h1>⚡ Skill Forge</h1>
    <p>Fábrica de SKILL.md e instruções de agente para os processos Stefanini</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Barra de progresso (steps)
# ---------------------------------------------------------------------------
current_step: int = st.session_state.step

steps_html = '<div class="sf-steps">'
for i, label in enumerate(STEP_LABELS, start=1):
    if i < current_step:
        css = "sf-step done"
        icon = "✓ "
    elif i == current_step:
        css = "sf-step active"
        icon = ""
    else:
        css = "sf-step"
        icon = ""
    steps_html += f'<span class="{css}">{icon}{label}</span>'
steps_html += "</div>"
st.markdown(steps_html, unsafe_allow_html=True)

# barra de progresso nativa do Streamlit
st.progress((current_step - 1) / (TOTAL_STEPS - 1))

# ---------------------------------------------------------------------------
# PASSO 1 — Selecionar agentes
# ---------------------------------------------------------------------------
with st.container(border=True):
    if st.session_state.step == 1:
        st.subheader("Passo 1 — Selecionar agente-alvo")
        st.caption(
            "Escolha para qual IDE ou ambiente a skill será gerada. "
            "Pode selecionar mais de um."
        )

        # Grade de cards informativos
        agent_cols = st.columns(2)
        for idx, agent in enumerate(agents):
            with agent_cols[idx % 2]:
                files_str = ", ".join(f"`{f}`" for f in agent.get("files", []))
                st.markdown(
                    f"""<div class="sf-agent-card">
                    <strong>{agent['label']}</strong><br>
                    <small style="color:#64748b">Arquivo(s): {files_str}</small>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.session_state.selected_agents = st.multiselect(
            "Agentes selecionados",
            options=[a["id"] for a in agents],
            format_func=lambda v: next((a["label"] for a in agents if a["id"] == v), v),
            default=st.session_state.selected_agents,
            key="step1_agents",
            help=FIELD_HELP["agents"],
        )

        _, right = st.columns([3, 1])
        with right:
            st.button(
                "Continuar →",
                key="step1_next",
                type="primary",
                disabled=len(st.session_state.selected_agents) == 0,
                on_click=lambda: go_to(2),
                use_container_width=True,
            )

# ---------------------------------------------------------------------------
# PASSO 2 — Descrever artefato
# ---------------------------------------------------------------------------
    elif st.session_state.step == 2:
        st.subheader("Passo 2 — Descrever o artefato")
        st.caption("Preencha as informações da skill que será gerada.")

        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.skill_name = st.text_input(
                "Nome da skill *",
                st.session_state.skill_name,
                key="step2_skill_name",
                help=FIELD_HELP["skill_name"],
                placeholder="Ex: Revisor Backend Node",
            )
            st.session_state.domain = st.text_input(
                "Domínio *",
                st.session_state.domain,
                key="step2_domain",
                help=FIELD_HELP["domain"],
                placeholder="Ex: backend, dados, QA",
            )
        with col_b:
            st.session_state.objective = st.text_input(
                "Objetivo (1 frase) *",
                st.session_state.objective,
                key="step2_objective",
                help=FIELD_HELP["objective"],
                placeholder="Ex: Revisar PRs com foco em segurança",
            )
            st.session_state.autonomy_level = st.selectbox(
                "Nível de autonomia *",
                options=["suggest_only", "apply_changes", "run_commands"],
                index=["suggest_only", "apply_changes", "run_commands"].index(
                    st.session_state.autonomy_level
                )
                if st.session_state.autonomy_level in ["suggest_only", "apply_changes", "run_commands"]
                else 0,
                key="step2_autonomy",
                help=FIELD_HELP["autonomy_level"],
            )
        st.session_state.constraints = st.text_area(
            "Restrições / Guardrails",
            st.session_state.constraints,
            key="step2_constraints",
            help=FIELD_HELP["constraints"],
            placeholder="Ex: não mexer em migrations, não alterar contratos de API",
            height=80,
        )
        st.session_state.description = st.text_area(
            "Descrição de alto nível *",
            st.session_state.description,
            height=160,
            key="step2_description",
            help=FIELD_HELP["description"],
            placeholder="Descreva detalhadamente o que a skill deve fazer (mín. 20 caracteres).",
        )

        is_valid = (
            bool(st.session_state.skill_name.strip())
            and bool(st.session_state.objective.strip())
            and len(st.session_state.description.strip()) >= 20
        )

        left, right = st.columns(2)
        with left:
            if st.button("← Voltar", key="step2_back"):
                go_to(1)
        with right:
            if st.button(
                "Continuar →",
                key="step2_next",
                type="primary",
                disabled=not is_valid,
                use_container_width=True,
            ):
                go_to(3)
        if not is_valid:
            st.caption("⚠️ Preencha os campos obrigatórios (*) para continuar.")

# ---------------------------------------------------------------------------
# PASSO 3 — Materiais
# ---------------------------------------------------------------------------
    elif st.session_state.step == 3:
        st.subheader("Passo 3 — Adicionar materiais de contexto")
        st.caption(
            "Materiais são as fontes de informação que o agente deve consultar. "
            "Você pode adicionar vários."
        )

        connector_ids = [c["id"] for c in connectors]
        selected_connector = st.selectbox(
            "Tipo de conector",
            options=connector_ids,
            format_func=lambda v: next((c["label"] for c in connectors if c["id"] == v), v),
            key="step3_connector",
            help=FIELD_HELP["connector_type"],
        )
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input(
                "Nome do material",
                key="step3_name",
                help=FIELD_HELP["material_name"],
                placeholder="Ex: API de Pedidos",
            )
        with col_b:
            description = st.text_area(
                "Por que este material importa? *",
                key="step3_description",
                help=FIELD_HELP["material_description"],
                placeholder="Ex: Contém os contratos dos endpoints de pedidos",
                height=80,
            )

        fields = next((c["fields"] for c in connectors if c["id"] == selected_connector), [])
        if fields:
            st.markdown("**Configuração do conector:**")
            meta_cols = st.columns(min(len(fields), 3))
            metadata: dict[str, str] = {}
            for i, field in enumerate(fields):
                with meta_cols[i % 3]:
                    metadata[field] = st.text_input(
                        field,
                        key=f"step3_field_{field}",
                        help=METADATA_HELP.get(field, "Campo de configuração do conector."),
                    )
        else:
            metadata = {}

        add_col, test_col, _ = st.columns([1, 1, 2])
        with add_col:
            if st.button("➕ Adicionar material", key="step3_add"):
                if not description.strip():
                    st.error("A descrição do material é obrigatória.")
                elif not name.strip():
                    st.error("O nome do material é obrigatório.")
                else:
                    st.session_state.materials.append(
                        {
                            "connector_type": selected_connector,
                            "name": name,
                            "description": description,
                            "connection_metadata": metadata,
                        }
                    )
                    st.success(f"✅ Material **{name}** adicionado.")
                    st.rerun()
        with test_col:
            if st.button("🔌 Testar conexão", key="step3_test"):
                result = client.test_connection(selected_connector, metadata)
                if result.get("ok"):
                    st.success(f"✅ {result.get('detail', 'Conexão válida.')}")
                else:
                    st.warning(f"⚠️ {result.get('detail', 'Parâmetros inválidos.')}")

        if st.session_state.materials:
            st.markdown("**Materiais adicionados:**")
            for i, mat in enumerate(st.session_state.materials):
                with st.expander(f"📄 {mat['name']} — `{mat['connector_type']}`"):
                    st.write(mat["description"])
                    if st.button("🗑️ Remover", key=f"step3_remove_{i}"):
                        st.session_state.materials.pop(i)
                        st.rerun()
        else:
            st.info("ℹ️ Nenhum material adicionado ainda. Materiais são opcionais.")

        left, right = st.columns(2)
        with left:
            if st.button("← Voltar", key="step3_back"):
                go_to(2)
        with right:
            if st.button(
                "Continuar →",
                key="step3_next",
                type="primary",
                use_container_width=True,
            ):
                go_to(4)

# ---------------------------------------------------------------------------
# PASSO 4 — Revisar e gerar
# ---------------------------------------------------------------------------
    elif st.session_state.step == 4:
        st.subheader("Passo 4 — Revisar e gerar")
        st.caption("Confira as informações antes de gerar os artefatos.")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Projeto**")
            st.markdown(f"- **Nome:** {st.session_state.skill_name}")
            st.markdown(f"- **Objetivo:** {st.session_state.objective}")
            st.markdown(f"- **Domínio:** {st.session_state.domain}")
            st.markdown(f"- **Autonomia:** `{st.session_state.autonomy_level}`")
            if st.session_state.constraints:
                st.markdown(f"- **Restrições:** {st.session_state.constraints}")
        with col_b:
            st.markdown("**Agentes selecionados**")
            for ag in st.session_state.selected_agents:
                label = next((a["label"] for a in agents if a["id"] == ag), ag)
                st.markdown(f"- {label}")
            st.markdown(f"**Materiais:** {len(st.session_state.materials)} adicionado(s)")

        with st.expander("Ver descrição completa"):
            st.write(st.session_state.description)

        st.divider()

        left, right = st.columns(2)
        with left:
            if st.button("← Voltar", key="step4_back"):
                go_to(3)
        with right:
            if st.button("⚡ Gerar artefatos", type="primary", key="step4_generate", use_container_width=True):
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
                with st.status("⚙️ Gerando artefatos...", expanded=True) as status:
                    status.write("Enviando requisição para a API...")
                    try:
                        response = client.generate(payload)
                        st.session_state.result = response.get("items", [])
                        st.session_state.step = 5
                        status.update(label="✅ Artefatos gerados com sucesso!", state="complete")
                    except Exception as exc:
                        status.update(label="❌ Erro na geração", state="error")
                        st.error(f"Erro: {exc}")
                st.rerun()

# ---------------------------------------------------------------------------
# PASSO 5 — Resultados + wizard de instalação automatizada
# ---------------------------------------------------------------------------
    elif st.session_state.step == 5:
        st.subheader("Passo 5 — Artefatos gerados")

        if not st.session_state.result:
            st.warning("Nenhum resultado disponível. Volte e gere novamente.")
        else:
            for idx, item in enumerate(st.session_state.result):
                agent_id = item["target_agent"]
                agent_label = next((a["label"] for a in agents if a["id"] == agent_id), agent_id)

                with st.container():
                    st.markdown(f"### ⚡ {agent_label}")

                    if item.get("used_cached_job"):
                        st.markdown(
                            '<div class="sf-cache-badge">♻️ Resultado do cache — '
                            "mesmas entradas já processadas anteriormente.</div>",
                            unsafe_allow_html=True,
                        )

                    files_list = ", ".join(f"`{f}`" for f in item.get("generated_files", []))
                    st.caption(f"Arquivos: {files_list}")

                    col_dl, col_prev, col_prompt = st.columns(3)
                    with col_dl:
                        dl_url = client.download_url(item["download_token"])
                        st.link_button("⬇️ Baixar pacote (.zip)", dl_url, use_container_width=True)
                    with col_prev:
                        with st.expander("👁️ Preview SKILL.md"):
                            st.code(item.get("preview_markdown", ""), language="markdown")
                    with col_prompt:
                        with st.expander("💬 Prompt sugerido"):
                            st.code(item.get("suggested_prompt", ""), language="markdown")

                    # -------------------------------------------------------
                    # Sub-wizard de instalação automatizada
                    # -------------------------------------------------------
                    st.markdown("#### 🚀 Instalar automaticamente")
                    st.caption(
                        "Informe o diretório raiz do seu projeto e o Skill Forge "
                        "copiará os artefatos para os locais corretos."
                    )

                    deploy_key = f"deploy_{idx}"
                    project_path = st.text_input(
                        "Diretório do projeto (caminho completo)",
                        key=f"{deploy_key}_path",
                        placeholder="Ex: C:\\Projetos\\meu-projeto  ou  /home/user/meu-projeto",
                        help=(
                            "Cole aqui o caminho da pasta raiz do seu projeto. "
                            "Os arquivos serão copiados para dentro dela."
                        ),
                    )

                    deploy_done_key = f"{agent_id}_{idx}"
                    already_deployed = st.session_state.deploy_done.get(deploy_done_key)

                    if already_deployed:
                        st.markdown(
                            f"""<div class="sf-deploy-success">
                            ✅ <strong>Instalado com sucesso!</strong><br>
                            📁 {already_deployed['project_path']}<br>
                            <small>{already_deployed['message']}</small>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                        st.markdown("**Próximo passo:**")
                        st.info(already_deployed["instructions"])
                    else:
                        if st.button(
                            f"🚀 Instalar em `{project_path or '...'}`",
                            key=f"{deploy_key}_btn",
                            type="primary",
                            disabled=not project_path.strip(),
                            use_container_width=False,
                        ):
                            with st.spinner("Copiando artefatos..."):
                                try:
                                    deploy_result = client.deploy(
                                        download_token=item["download_token"],
                                        target_agent=agent_id,
                                        project_path=project_path.strip(),
                                    )
                                    st.session_state.deploy_done[deploy_done_key] = deploy_result
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"❌ Erro ao instalar: {exc}")

                    st.divider()

        # Botão para nova geração
        if st.button("🔄 Nova geração", key="step5_new"):
            clear_for_new_run()
