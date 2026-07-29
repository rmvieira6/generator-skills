# ============================================================================
# Configuração para Streamlit Cloud
# ============================================================================
#
# Este arquivo contém instruções para deploy na Streamlit Cloud
#
# ============================================================================

## 📋 Checklist de Deploy

- [ ] A API está hospedada em um servidor remoto (ex: AWS, Azure, GCP, etc)
- [ ] Você tem a URL remota da API (ex: https://skill-forge-api.example.com)
- [ ] O código foi feito push para GitHub
- [ ] `.streamlit/secrets.toml` está em `.gitignore` (local only)

## 🚀 Passos para Deploy

### 1. Prepare a API Remota

A API deve estar hospedada e acessível pela internet. Configure o CORS:

```python
# Em src/main.py, verifique que os allowed_origins incluem seu domínio do Streamlit Cloud
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Deve incluir *.streamlit.app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Faça Push para GitHub

```bash
git add .
git commit -m "Deploy Skill Forge Web"
git push origin main
```

**Certifique-se de que NÃO fez push de:**
- `.streamlit/secrets.toml` (deve estar em .gitignore)
- `.env` (deve estar em .gitignore)

### 3. Acesse Streamlit Cloud

- Vá para https://share.streamlit.io
- Clique em "New app"
- Conecte seu repositório GitHub
- Preencha:
  - **Repository:** seu-usuario/seu-repo
  - **Branch:** main
  - **Main file path:** apps/web/src/app.py

### 4. Configure Secrets

Na dashboard de deploy, vá para **Settings → Secrets** e adicione:

```toml
# Copie tudo abaixo (sem comentários no TOML real)
skill_forge_api_url = "https://sua-api-skill-forge.example.com"
```

Substitua `https://sua-api-skill-forge.example.com` pela URL real da sua API.

### 5. Deploy

Clique em "Deploy" e aguarde!

---

## 🔗 Variáveis de Ambiente

O app usa esta ordem de prioridade para obter a URL da API:

1. **Parâmetro direto** (ao instanciar `SkillForgeApiClient(base_url="...")`)
2. **Variável de ambiente** `SKILL_FORGE_API_URL`
3. **Streamlit Secrets** `skill_forge_api_url`
4. **Default** `http://localhost:8000`

Para Streamlit Cloud, use sempre **Secrets** (opção 3).

---

## ✅ Verificação

Após deploy, teste a aplicação:

1. Clique no link gerado pela Streamlit Cloud (ex: https://seu-app.streamlit.app)
2. Vá para a aba "Otimizar"
3. Upload um SKILL.md
4. Selecione uma otimização
5. Clique em "Gerar SKILL.md otimizada"

Se receber erro 404 ou connection error:

1. Verifique se a URL da API foi configurada corretamente em Secrets
2. Verifique se a API remota está online
3. Verifique CORS na API (deve aceitar requisições do seu app)
4. Verifique logs: em Settings → App logs

---

## 🐛 Troubleshooting

### "404 Not Found" ao chamar `/api/generation/optimize-skill`

- [ ] Verifique se `skill_forge_api_url` em Secrets está correto
- [ ] Teste a URL manualmente: `curl https://sua-api/health`
- [ ] Verifique logs da API remota

### "Connection refused"

- [ ] A API remota está online?
- [ ] Firewall/Security Groups permitem acesso?
- [ ] DNS está resolvendo o domínio?

### CORS error

A API deve ter CORS configurado:

```toml
# Em .env da API:
ALLOWED_ORIGINS=["https://seu-app.streamlit.app", "http://localhost:3000"]
```

---

## 📚 Documentação Adicional

- [Streamlit Cloud Docs](https://docs.streamlit.io/deploy/streamlit-cloud)
- [Streamlit Cloud Secrets](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app#secrets-management)
