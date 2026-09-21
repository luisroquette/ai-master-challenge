# Diário de processo — Challenge 004: Estratégia Social Media

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:27 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir qualquer ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** seis passadas concluídas; as passadas 5 e 6 não produziram novas descobertas. O arquivo local e o `main` remoto eram idênticos no blob Git `52b10db595fb2a3f50c8a7cc73573fa53f5db087`.
- **Julgamento humano:** a técnica de leitura em loop e o critério de parada foram decisões criativas de Luis. A IA executou e documentou o protocolo.
- **Verificação:** checklist reverso localizou 18 de 18 requisitos críticos; duas releituras consecutivas encerraram sem novos achados.
- **Evidência:** este ledger e o histórico Git do arquivo.
- **Limitação:** os dados ainda não foram inspecionados; nenhuma hipótese de performance foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal | contexto, dados, quatro entregáveis, critérios de qualidade, dicas e público executivo |
| 2 | contradições e exigências implícitas | ausência de gasto impede ROI financeiro verdadeiro; Bilibili e RedNote aparecem nos dados, mas não no contexto inicial; frequência e thresholds exigem cautela causal |
| 3 | documentos obrigatórios vinculados | process log é eliminatório e deve mostrar decomposição, iterações, erros da IA, correções e contribuição humana |
| 4 | template e regras de submissão | resumo executivo curto, resultados com evidência, recomendações priorizadas, limitações, instruções de uso e alterações restritas à pasta da submissão |
| 5 | conferência integral por seção | nenhum |
| 6 | checklist reverso dos requisitos | nenhum |

**Gate atingido:** duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O desafio pede uma análise controlada, não médias gerais. A comparação entre conteúdo orgânico e patrocinado precisa considerar pelo menos plataforma, categoria e tamanho do creator, além de contextualizar engagement rate com alcance. Sem dados de gasto, não existe base para declarar ROI financeiro.

A estratégia deve dizer onde concentrar esforço, o que produzir, para quem, quando, com qual faixa de creator e qual evidência sustenta a decisão. Também precisa apontar o que parar, ordenar prioridades e propor quick wins executáveis na mesma semana.

O diferencial deve transformar os achados em decisão recorrente sem aumentar o escopo antes da evidência. A escolha entre dashboard, recomendador ou outra ferramenta será feita somente após pesquisa de soluções existentes e inspeção dos dados.

## I02 — SDD adotado antes da construção — 2026-09-21 14:31 BRT

- **Objetivo:** transformar o desafio em especificação verificável antes de implementar análise ou ferramenta.
- **IA/ferramenta:** skills `add-task`, `plan-task` e `implement-task` do Context Engineering Kit, instaladas para Claude Code via `npx skills`.
- **Ação ou prompt:** Luis decidiu usar Spec-Driven Development e indicou a skill SDD do repositório `NeoLabHQ/context-engineering-kit`.
- **Resultado:** a versão atual não expõe uma skill única chamada `sdd`; o fluxo foi instalado pelos três componentes publicados. Nenhuma SPEC foi criada: ela dependerá da descoberta socrática e da arquitetura aprovadas por Luis.
- **Julgamento humano:** adotar SDD foi decisão de Luis. O planejamento deve passar por revisão humana antes de qualquer implementação; a SPEC não substitui a Regra zero de pesquisa e evidência.
- **Verificação:** o instalador confirmou as três skills para Claude Code e classificou todas como seguras.
- **Evidência:** este registro, `skills-lock.json` e os diretórios locais `.claude/skills/`.
- **Limitação:** `npx skills` instala skills, mas não os subagentes do plugin completo. Os artefatos de ferramenta ficam locais e não entrarão no Pull Request, que aceita apenas `submissions/luis-roquette/`.

**Fluxo adotado:** `descoberta socrática → arquitetura aprovada → add-task → plan-task → revisão humana da SPEC → implement-task`, sempre subordinado às regras de pesquisa, Ponytail, testes e integridade do desafio.

## I03 — Documentação como parte central da entrega — 2026-09-21 14:34 BRT

- **Decisão de Luis:** documentar todo o processo é tão importante quanto — ou mais importante que — o resultado final. Ganha quem documenta.
- **Forma:** registrar continuamente fragmentos curtos, objetivos e diretos, com destaque para os pontos que Luis sinalizar durante o trabalho.
- **Regra editorial:** corrigir erros de português antes de incorporar qualquer fala ou decisão ao diário, preservando o sentido original.
- **Princípio:** como dizia Silvio Santos: “Sabe por que o ovo de galinha vende mais que o de pata? Porque a galinha canta quando bota!”
- **Aplicação:** cada decisão, hipótese, correção, evidência, limitação e contribuição humana relevante será registrada no momento em que ocorrer, sem reconstrução retroativa.

## I04 — Descoberta socrática em ondas adaptativas — 2026-09-21 14:41 BRT

- **Decisão de Luis:** a SPEC não será presumida nem escrita antes de discutirmos exaustivamente o projeto e arquitetarmos a solução sobre bases sólidas.
- **Método:** conduzir pelo menos cinco ondas socráticas, com uma pergunta de múltipla escolha por vez. Cada onda posterior dependerá das respostas e descobertas das ondas anteriores.
- **Objetivo:** explicitar problema, decisão de negócio, usuários, restrições, hipóteses, alternativas, riscos, dados, arquitetura, critérios de sucesso e definição de pronto antes da especificação.
- **Adaptação:** não existe roteiro rígido. As respostas de Luis determinam a próxima pergunta, e ondas adicionais serão abertas se permanecer qualquer ambiguidade material.
- **Gate:** somente após encerrar as ondas, comparar abordagens, validar a arquitetura em blocos e obter concordância de Luis será criada a SPEC SDD.
- **Correção de processo:** o placeholder criado prematuramente foi removido sem entrar no Git. Nenhuma SPEC existe neste momento.
- **Formato definido por Luis:** todas as perguntas serão de múltipla escolha, com opções claras, mutuamente distintas e recomendação explícita quando houver base para recomendá-la.

## I05 — Ledger da descoberta socrática — 2026-09-21 14:49 BRT

Este ledger registra todas as perguntas, respostas, correções e decisões da descoberta nesta sessão.

### Tentativa anterior à Onda 1 — descartada

- **Pergunta:** se a entrega estivesse pronta amanhã, qual seria a única decisão de maior valor que o Head de Marketing deveria conseguir tomar com confiança?
- **Resposta de Luis:** a pergunta deveria ser de múltipla escolha.
- **Efeito:** pergunta descartada sem resposta de conteúdo; todas as ondas passaram a usar múltipla escolha.

### Onda 1 — decisão central

- **Pergunta:** qual decisão principal a solução deve permitir?
- **Opções:** A) realocar esforço e patrocínio; B) definir o calendário editorial; C) criar um sistema operacional recorrente para planejar, acompanhar e corrigir a estratégia.
- **Resposta de Luis:** **C — criar um sistema operacional recorrente**.
- **Implicação:** a solução não será apenas uma análise estática. Ela deverá sustentar um ciclo repetível de decisão, acompanhamento e correção; o escopo desse ciclo será definido nas próximas ondas.

### Onda 2 — operador principal

- **Pergunta:** quem deve operar o sistema recorrente no cotidiano?
- **Opções:** A) Gestor de Social Media, no planejamento e acompanhamento diário; B) Head de Marketing, na revisão semanal de estratégia e investimento; C) Analista de Marketing, no diagnóstico mensal e preparação das recomendações.
- **Resposta de Luis:** **A, B e C**, tendo o **Gestor de Social Media como operador principal**.
- **Implicação:** a arquitetura deverá atender três níveis de uso sem confundir responsabilidades: operação diária pelo Gestor de Social Media, decisão executiva pelo Head de Marketing e análise periódica pelo Analista de Marketing. O fluxo principal será desenhado para o gestor; os demais receberão visões derivadas.

### Onda 3 — cadência central

- **Pergunta:** qual cadência deve comandar o sistema?
- **Opções:** A) ciclo diário, com consolidações semanais e mensais automáticas; B) ciclo semanal, com dados diários usados apenas como entrada; C) ciclo mensal, orientado principalmente à revisão estratégica.
- **Resposta de Luis:** **A — ciclo diário, com consolidações semanais e mensais automáticas**.
- **Implicação:** o produto deverá gerar utilidade operacional todos os dias e agregar os mesmos dados em visões semanais e mensais, sem criar três fluxos independentes.

### Onda 4 — entrega diária principal

- **Pergunta:** qual deve ser a primeira entrega que o Gestor de Social Media vê diariamente?
- **Opções:** A) fila priorizada de ações; B) painel de monitoramento com desempenho recente, alertas e desvios; C) quadro de experimentos.
- **Resposta de Luis:** **B — painel de monitoramento**.
- **Implicação:** a experiência principal começa pela observação objetiva do desempenho e das mudanças relevantes. Recomendações e experimentos poderão derivar do painel, mas não substituirão a leitura dos dados como porta de entrada.
