# Lean Challenge 001 Delivery Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** entregar a resposta do Challenge 001 em menos de dois minutos de navegação inicial, preservando profundidade técnica sob demanda.

**Architecture:** quatro links visíveis formam a entrega: Comece aqui, Veja funcionando, Entenda a construção e Audite. O vídeo obrigatório existente substitui qualquer Video Overview; o NotebookLM gera somente um infográfico. O relatório e o Process Log ficam como profundidade, não como porta de entrada.

**Tech Stack:** Markdown, DOCX, NotebookLM Infographic, Arcade Interactive Demo, vídeo H.264 existente, Git/GitHub e Streamlit.

**Spec:** `.specs/tasks/todo/package-challenge-001-deliverables.feature.md`

## Global Constraints

- O avaliador deve alcançar a resposta principal sem rolar um documento longo.
- O vídeo obrigatório tem 6min05s, 1920×1080, 60 fps, H.264/AAC e legendas queimadas.
- O MP4 de 232.879.349 bytes não será commitado no Git.
- Markdown é o formato para IA; DOCX é a cópia humana. Não produzir TXT redundante.
- Não gerar segundo vídeo, mapa mental, slide deck ou landing page.
- Publicação do vídeo, Arcade e PR upstream exige confirmação final de Luis.

## Review Focus

- O primeiro bloco do README demora mais de 30 segundos para revelar resposta e decisão.
- O vídeo obrigatório está inacessível sem login ou sem permissão pública adequada.
- Arcade repete metodologia em vez de demonstrar o sistema.
- Brief, vídeo ou infográfico introduzem números ou causalidade não sustentados.
- A quantidade de links devolve ao avaliador o trabalho de decidir por onde começar.

---

### Task 1: Criar a porta de entrada de duas páginas

**Files:**
- Create: `deliverables/delivery-brief.md`
- Generate: `deliverables/delivery-brief.docx`
- Create: `deliverables/delivery-manifest.md`
- Modify: `../../README.md`

**Interfaces:**
- Consumes: `artifacts/ceo_answer.json`, `docs/executive-answer-rubric.md` e `process-log/000-004`.
- Produces: brief canônico de até 1.200 palavras e índice de quatro links.

- [ ] **Step 1: escrever a abertura de 30 segundos**

Usar cinco blocos: resposta em seis linhas; decisão; três ações; método em oito etapas; links. A abertura deve conter 12,4%, +7,0 pp, US$ 1.622.337 e “Causa ainda não demonstrada”.

- [ ] **Step 2: mostrar a evolução sem contar toda a história**

Incluir uma única tabela `Momento | Problema encontrado | Decisão humana | Nota`, com `7,0 → 8,6 → 9,5 → 9,9`. Limitar prompts a quatro fragmentos decisivos.

- [ ] **Step 3: gerar o DOCX a partir do Markdown**

Usar a skill `documents`; o Markdown permanece a fonte editável. O DOCX deve caber em duas páginas A4, com links clicáveis e sem anexos incorporados.

- [ ] **Step 4: validar o brief**

Run:

```bash
test "$(wc -w < deliverables/delivery-brief.md)" -le 1200
rg -n "12,4%|7,0 pp|1\.622\.337|Causa ainda não demonstrada|7,0 → 8,6 → 9,5 → 9,9" deliverables/delivery-brief.md
```

Expected: limite e cinco âncoras atendidos.

- [ ] **Step 5: checkpoint**

```bash
git add -f deliverables/delivery-brief.md deliverables/delivery-brief.docx deliverables/delivery-manifest.md ../../README.md
git commit -m "docs(churn): create lean delivery entrypoint"
```

### Task 2: Incorporar o vídeo obrigatório de arquitetura

**Files:**
- Source: `2026-09-22 18-24-32_LEGENDADO_1,25x.mp4`
- Create: `deliverables/video/README.md`
- Create: `deliverables/video/poster.png`

**Interfaces:**
- Consumes: MP4 local de 6min05s.
- Produces: link acessível, capítulos, metadados, poster e SHA-256; nunca o binário no Git.

- [ ] **Step 1: assistir integralmente e registrar capítulos**

Marcar timestamps reais para: problema; arquitetura; metodologia; implementação; validação; conclusão. Não deduzir capítulos apenas pelo nome do arquivo.

- [ ] **Step 2: validar mídia e legendas**

Conferir áudio do início ao fim, legibilidade das legendas queimadas, ausência de segredo/tela privada e sincronia a 1,25×. Registrar duração exata `365,533 s`.

- [ ] **Step 3: gerar poster e checksum**

Extrair um quadro representativo sem informação privada e registrar `shasum -a 256` no README do vídeo.

- [ ] **Step 4: preparar hospedagem externa**

Recomendação: YouTube não listado, por reprodução imediata sem download de 222 MiB. Parar antes do upload/publicação e solicitar confirmação de Luis.

- [ ] **Step 5: validar o link publicado**

Depois da confirmação, abrir o link em sessão anônima, reproduzir início/meio/fim e verificar título, legenda, capítulos e acesso sem login.

### Task 3: Criar o Arcade de até 90 segundos

**Files:**
- Create: `deliverables/arcade/arcade-script.md`
- Create: `deliverables/arcade/README.md`

**Interfaces:**
- Consumes: dashboard validado em `127.0.0.1:8503`.
- Produces: demo interativa focada no produto, com oito passos.

- [ ] **Step 1: roteirizar os oito passos**

1. A pergunta e a resposta curta.
2. Churn e impacto econômico.
3. Produto: agregado versus coorte.
4. CS: respondentes versus coorte.
5. Sem concentração material.
6. Causa ainda não demonstrada.
7. Três validações com donos e prazos.
8. Evidência, `analysis_id` e chamada para o brief.

- [ ] **Step 2: limitar a carga cognitiva**

Cada instrução possui até 22 palavras; nenhum passo mostra mais de uma ideia; o tour completo deve caber em 60–90 segundos.

- [ ] **Step 3: capturar e revisar o rascunho**

Usar screenshots do dashboard e no máximo um trecho de vídeo de interação. Conferir números, foco, desktop/mobile e ausência de caminhos locais.

- [ ] **Step 4: preparar publicação**

Parar antes do compartilhamento público. Após confirmação de Luis, salvar URL, data e acesso anônimo no README do Arcade.

### Task 4: Gerar somente um infográfico no NotebookLM

**Files:**
- Create: `deliverables/notebooklm/source-pack.md`
- Create: `deliverables/notebooklm/infographic-prompt.md`
- Receive: `deliverables/visuals/method-evolution-infographic.png`

**Interfaces:**
- Consumes: brief e diários públicos.
- Produces: uma única peça visual sobre método e evolução.

- [ ] **Step 1: montar fonte curta e fechada**

Incluir somente oito etapas metodológicas, quatro notas, três viradas humanas e seis fatos do diagnóstico. Excluir logs extensos, código e dados brutos.

- [ ] **Step 2: usar o prompt editorial**

```text
Crie um infográfico vertical em português brasileiro: “De uma pergunta confusa a uma decisão confiável”. Mostre oito etapas, a evolução 7,0 → 8,6 → 9,5 → 9,9 e três viradas humanas: separar agregados de coortes; recusar causalidade frágil; converter incerteza em validação. Use somente as fontes e não acrescente números.
```

- [ ] **Step 3: revisar e exportar**

Conferir texto, notas, números, autoria e ausência de causa inventada. Se a primeira geração falhar, corrigir o prompt uma vez; depois, editar a fonte em vez de iterar indefinidamente.

- [ ] **Step 4: checkpoint**

```bash
git add -f deliverables/notebooklm deliverables/visuals
git commit -m "docs(churn): add one-page methodology infographic"
```

### Task 5: Fechar a entrega em quatro links

**Files:**
- Modify: `deliverables/delivery-manifest.md`
- Modify: `../../README.md`
- Modify: `../../process-log/004-planejamento-entregaveis.md`

**Interfaces:**
- Consumes: brief, vídeo, Arcade, infográfico e evidências existentes.
- Produces: entrada final do avaliador e PR pronto para revisão.

- [ ] **Step 1: ordenar a abertura**

Mostrar somente: `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Audite o processo`. Relatório e código ficam dentro de “Audite”.

- [ ] **Step 2: validar tudo como avaliador anônimo**

Abrir cada link sem sessão; confirmar que nenhum exige permissão; assistir Arcade e vídeo; abrir DOCX; verificar o infográfico em mobile.

- [ ] **Step 3: reconciliar fatos e limites**

Comparar as seis verdades em brief, Arcade, vídeo e infográfico. Qualquer divergência bloqueia a entrega; corrigir o derivado, nunca a fonte canônica.

- [ ] **Step 4: atualizar manifesto e diário**

Registrar URL, checksum, data, formato, status e limitação. Itens não produzidos não aparecem como entrega.

- [ ] **Step 5: preparar o PR sem submeter**

Montar descrição com a resposta em seis linhas e os quatro links. Parar antes do envio ao upstream para confirmação final de Luis.

## Self-review

- Escopo reduzido de onze artefatos destacados para quatro entradas visíveis.
- Video Overview, mapa mental e TXT foram removidos por redundância.
- O vídeo obrigatório existente virou a peça central da construção.
- Arcade demonstra o produto; vídeo explica arquitetura; brief responde; Process Log prova.
- Nenhum binário de 222 MiB entra no Git.
