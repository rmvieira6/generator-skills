---
name: {{PROJECT_NAME}}
description: {{OBJECTIVE}}
version: 1.0.0
---

# Contexto
- Agente alvo: {{TARGET_AGENT}}
- Dominio: {{DOMAIN}}
- Nivel de autonomia: {{AUTONOMY_LEVEL}}

# Escopo
{{HIGH_LEVEL_DESCRIPTION}}

# Restricoes
{{CONSTRAINTS}}

# Materiais
{{MATERIALS_TABLE}}

# Regras de Economia de Tokens
1. Aplique progressive disclosure: mantenha o corpo principal minimo e referencie arquivos auxiliares quando houver detalhe extenso.
2. Mantenha frontmatter enxuto e sem repeticoes no corpo.
3. Elimine redundancias; referencie secoes existentes em vez de duplicar texto.
4. Use linguagem imperativa, curta e telegráfica.
5. Use tabelas para comparativos e checklists.
6. Referencie caminhos de arquivos, nao copie conteudo inteiro.
7. Limite exemplos a um exemplo minimo por regra.
8. Use chunking por topicos com headers ancoraveis.
9. Evite meta-comentario; execute a instrucao diretamente.
10. Numere apenas o necessario; sem subniveis excessivos.
11. Preserve placeholders explicitos para trechos dinamicos.
12. Defina quando parar: nao expandir alem do escopo solicitado.

# Protocolo Anti-Duplicacao e Continuidade (literal)
1. Antes de implementar algo, ler o historico de implementacao (changelog, commits recentes, IMPLEMENTATION_LOG.md ou equivalente do projeto-alvo) para saber o que ja existe.
2. Antes de criar uma funcao/modulo/endpoint, buscar no codigo-base se algo equivalente ja existe (grep semantico por nome/responsabilidade) - se existir, reutilizar ou estender, nunca duplicar.
3. Fazer apenas a menor mudanca necessaria (principio do diff minimo): nao reescrever arquivos inteiros quando um ajuste pontual resolve.
4. Avaliar qualidade olhando o todo, nao so o diff: antes de finalizar, revisar se a mudanca e consistente com os padroes ja estabelecidos no restante do projeto (nomenclatura, arquitetura, testes).
5. Registrar a mudanca ao final em um log de implementacao (IMPLEMENTATION_LOG.md), com data, resumo e arquivos tocados - isso alimenta o passo 1 da proxima execucao, criando memoria incremental entre sessoes do agente.
6. Nunca gerar codigo morto ou por via das duvidas: se algo nao foi pedido e nao e pre-requisito direto, nao implementar.

# Padroes Senior Obrigatorios
- Preservar separacao de camadas (dominio/aplicacao/infraestrutura) quando existente; propor migracao gradual quando ausente.
- Exigir nomenclatura consistente e autoexplicativa.
- Exigir testes automatizados para nova logica de negocio.
- Exigir tratamento de erro explicito; proibir except pass ou catch silencioso.
- Exigir documentacao minima viavel (README atualizado e docstrings publicas).
- Exigir logs estruturados e evitar print solto em producao.
- Exigir seguranca basica: nunca commitar segredos e sempre validar entradas externas.

# Modo Incremental
Diff de materiais para atualizacao incremental:
{{INCREMENTAL_DIFF}}

# Formato de Saida Esperado
- Produza artefato no formato nativo do agente alvo.
- Produza instrucoes de uso curtas e acionaveis.
- Pare quando o objetivo e os artefatos solicitados forem entregues.
