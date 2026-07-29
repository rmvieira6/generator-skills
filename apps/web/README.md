# Skill Forge — Web App (Streamlit)

Interface web para geração e otimização de SKILLs usando Streamlit.

## 🚀 Execução Local

### Pré-requisitos

- Python 3.10+
- A API Skill Forge rodando (em outra janela/terminal)

### Setup

1. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

2. **Configure a URL da API:**

Se a API está em uma porta diferente de `8000`, edite `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
skill_forge_api_url = "http://localhost:8000"  # Altere a porta se necessário
```

Você também pode usar variável de ambiente:

```bash
export SKILL_FORGE_API_URL="http://localhost:58027"
streamlit run src/app.py
```

3. **Inicie o Streamlit:**

```bash
streamlit run src/app.py
```

A aplicação estará disponível em `http://localhost:8501`.

---

## ☁️ Deployment no Streamlit Cloud

### Passos para Deploy

1. **Faça push do seu código para GitHub** (certifique-se de que `.streamlit/secrets.toml` está em `.gitignore`)

2. **Acesse [Streamlit Cloud](https://share.streamlit.io)**

3. **Clique em "New app"** e conecte ao seu repositório

4. **Configure os Secrets:**
   
   Na dashboard de deploy do Streamlit Cloud:
   - Vá para **Settings → Secrets**
   - Adicione a chave `skill_forge_api_url` com a URL da sua API hospedada

   ```toml
   skill_forge_api_url = "https://seu-api-skill-forge.example.com"
   ```

---

## 📝 Estrutura

```
apps/web/
├── .streamlit/
│   ├── config.toml              # Configurações do Streamlit
│   ├── secrets.toml             # Secrets locais (NÃO comitar)
│   └── secrets.toml.example     # Template de secrets
├── src/
│   ├── app.py                   # Aplicação principal
│   └── api_client.py            # Cliente HTTP da API
├── tests/
│   └── test_api_client.py
├── pyproject.toml
└── requirements.txt
```

---

## 🔧 Resolução de Problemas

### Erro 404 ao otimizar

**Problema:** "404 Client Error: Not Found for url: http://127.0.0.1:58027/api/generation/optimize-skill"

**Solução:**

1. Verifique se a API está rodando na porta correta
2. Edite `.streamlit/secrets.toml` com a porta correta:
   ```toml
   skill_forge_api_url = "http://localhost:58027"
   ```
3. Reinicie o Streamlit

### API não disponível

**Problema:** "Connection refused" ao conectar na API

**Solução:**

1. Inicie a API em outro terminal:
   ```bash
   cd ../api
   python -m uvicorn src.main:app --reload
   ```
2. Verifique o endereço e porta
3. Configure `skill_forge_api_url` no `.streamlit/secrets.toml`

---

## 📚 Documentação

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Secrets](https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app#secrets-management)
