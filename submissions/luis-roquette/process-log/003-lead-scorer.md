# Diário de processo — Challenge 003: Lead Scorer

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:28 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir a ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a fonte e a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** cinco passadas concluídas; as passadas 2 a 5 não produziram novas descobertas. O README local corresponde ao commit-fonte `d4c8fc7e20cc99370df5cc438aa553bb4a9789b2` e tem SHA-256 `0f88457c166c0b945ef645dfb25ae35021d38a6dab92e4af613ddcc8253dd466`.
- **Julgamento humano:** a leitura em loop e o critério de parada são um diferencial criativo de Luis. A IA executou e documentou o protocolo, sem apresentar a técnica como sugestão própria.
- **Verificação:** releitura integral normal e reversa, conferência estrutural das 100 linhas e teste de 11 invariantes textuais; a fonte local não apresentou diferença contra o commit do challenge.
- **Evidência:** este ledger, o hash do arquivo e o histórico Git do README avaliado.
- **Limitação:** os dados ainda não foram inspecionados e nenhuma hipótese de scoring foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal e documentos vinculados | problema comercial, quatro tabelas, solução funcional, documentação, process log, critérios, dicas, template e regras do PR |
| 2 | requisitos normativos | nenhum |
| 3 | conferência linha a linha | nenhum |
| 4 | conferência integral em ordem reversa | nenhum |
| 5 | identidade da fonte e matriz de invariantes | nenhum |

**Gate atingido:** pelo menos duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O problema não é prever fechamento em abstrato. É substituir a priorização “no feeling” por uma fila diária que ajude 35 vendedores a decidir onde agir dentro de aproximadamente 8.800 oportunidades. O software precisa funcionar com os dados reais, ir além de ordenar por valor e explicar por que cada deal recebeu prioridade alta ou baixa.

O `sales_pipeline.csv` é a tabela central e se conecta a contas, produtos e equipe comercial. Antes de definir qualquer score, as chaves, cardinalidades, ausências e distribuição temporal precisam ser medidas. O briefing comum adiciona um limite decisivo: deals ativos não podem usar `close_date`, `close_value` nem estágio final como features, pois isso vazaria o resultado futuro.

Complexidade de modelo não é o objetivo. Regras ou heurísticas bem validadas e explicáveis podem superar um modelo opaco se ajudarem o vendedor a tomar uma ação na segunda-feira de manhã. Filtros por vendedor, manager e região são um bônus de alto valor, não substitutos dos requisitos mínimos.

A entrega precisa incluir setup reproduzível, lógica e limitações, além de evidências do processo. A pesquisa externa e a inspeção dos dados decidirão a tecnologia, os critérios do score e se o diferencial proposto — fila por vendedor com motivos, risco de esfriar e próxima ação — é sustentado pelos dados.

### Erro registrado nesta etapa

No primeiro verificador local, a variável de shell `path` sobrescreveu o `PATH` especial do `zsh`, e o comando `git` deixou de ser localizado. A variável foi renomeada para `challenge_file`; o verificador passou sem alterar arquivos.

## I02 — SDD adotado antes da construção — 2026-09-21 14:36 BRT

- **Objetivo:** tornar a especificação verificável o contrato de entrada para pesquisa, arquitetura e implementação do Lead Scorer.
- **IA/ferramenta:** plugin SDD `3.6.0` do `NeoLabHQ/context-engineering-kit`, baseado em GitHub Spec Kit, OpenSpec e arc42 adaptado.
- **Ação ou prompt:** Luis decidiu seguir Spec-Driven Development e indicou a instalação `npx skills add NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code`.
- **Resultado:** o plugin já estava instalado, habilitado e atualizado no Claude Code. O estágio `add-task` criou somente um rascunho da intenção em `solution/003-lead-scorer/.specs/tasks/draft/`; isso ainda não é uma SPEC. Nenhum planejamento ou código foi iniciado.
- **Julgamento humano:** a escolha de SDD é de Luis. A metodologia será combinada com a Regra zero, Ponytail `full` e os gates de evidência do briefing; não substitui pesquisa, validação humana ou limites contra leakage.
- **Verificação:** `claude plugin details sdd@context-engineering-kit` confirmou versão `3.6.0`, cinco skills, oito agentes e status habilitado; `claude plugin update` confirmou a versão mais recente.
- **Evidência:** `solution/003-lead-scorer/.specs/tasks/draft/implement-explainable-lead-scorer.feature.md` e este registro.
- **Limitação:** a SPEC ainda não existe. `/plan-task` e `/implement-task` não foram executados; antes deles, o projeto será discutido e arquitetado com Luis.

### Fluxo acordado

1. `add-task`: preservar a intenção original em `draft`.
2. `plan-task`: pesquisar, analisar negócio e código, definir arquitetura, critérios de aceitação, testes e subtarefas.
3. Revisar a especificação contra o briefing, a Regra zero e o risco de leakage.
4. `implement-task`: construir por fases, com revisão e evidência em cada gate.
5. Mover a tarefa para `done` somente após definição de pronto e validações reproduzíveis.

### Erro e correção desta etapa

O comando publicado pela página do recurso falhou com `No matching skills found for: sdd`: o CLI encontrou 68 skills individuais, mas `sdd` é um plugin composto, não uma skill isolada. A instalação oficial do próprio repositório foi conferida; `sdd@context-engineering-kit` já estava instalado e habilitado, então apenas o atualizamos e validamos em vez de duplicá-lo.

## I03 — Documentar é parte central da entrega — 2026-09-21 14:39 BRT

- **Objetivo:** preservar decisões, correções, evidências e contribuições humanas enquanto o trabalho acontece.
- **Decisão de Luis:** o diário é tão importante quanto — ou até mais importante que — o resultado final. Ganha quem documenta.
- **Formato:** fragmentos curtos, objetivos e diretos são suficientes, desde que registrem os destaques apontados por Luis e os marcos relevantes do processo.
- **Regra editorial:** corrigir ortografia, gramática e clareza antes de registrar, sem alterar a intenção original.
- **Disciplina:** registrar continuamente; não depender da memória nem reconstruir retroativamente prompts, horários, erros ou decisões.
- **Julgamento humano:** esta prioridade e a obsessão pelo registro foram definidas por Luis, não pela IA.

Luis resumiu o princípio com uma frase atribuída a Silvio Santos:

> “Sabe por que o ovo da galinha vende mais que o da pata? Porque a galinha canta quando bota!”

**Princípio permanente:** fazer um bom trabalho não basta; o processo precisa deixar evidência clara, fiel e útil. O diário é parte do produto.

## I04 — Deliberação socrática por ondas adaptativas — 2026-09-21 14:42 BRT

- **Objetivo:** construir entendimento e arquitetura sólidos antes de escrever a SPEC.
- **Correção de estado:** existe apenas um rascunho `add-task`; ainda não discutimos suficientemente o projeto e não há SPEC pronta para revisão.
- **Decisão de Luis:** conduzir a descoberta em pelo menos cinco ondas de perguntas socráticas. As ondas posteriores devem depender das respostas anteriores, não de um questionário fixo preparado de antemão.
- **Método:** fazer uma pergunta por vez, testar premissas, pedir exemplos concretos, expor tensões e registrar decisões, alternativas rejeitadas, dúvidas e evidências ao final de cada onda.
- **Gate:** não executar `/plan-task`, desenhar arquitetura definitiva ou implementar enquanto as ondas não convergirem e Luis não validar a síntese do desenho.
- **Julgamento humano:** objetivos, prioridades e escolhas finais pertencem a Luis; a IA organiza a investigação, desafia pressupostos e transforma decisões aprovadas em especificação verificável.

### Mapa provisório das ondas

1. **Resultado e usuário:** qual decisão precisa melhorar, para quem e em qual momento do trabalho.
2. **Fluxo comercial:** como a priorização funciona hoje, onde falha e qual mudança seria realmente adotada.
3. **Dados e verdade temporal:** quais sinais podem ser usados, quando ficam disponíveis e como impedir leakage.
4. **Score e explicação:** o que significa prioridade, como justificar o ranking e qual próxima ação deve aparecer.
5. **Experiência e operação:** interface, filtros, frequência, exceções, fallback e limites de manutenção.
6. **Arquitetura e prova:** alternativas técnicas, trade-offs, testes, critérios de aceitação e definição de pronto.

O mapa é intencionalmente provisório. Cada resposta pode reordenar, dividir, ampliar ou eliminar perguntas e ondas. Ao final da descoberta, serão comparadas alternativas de solução; o desenho escolhido será apresentado em partes curtas para validação antes de alimentar o `/plan-task`.

## I05 — Registro contínuo da sessão socrática — 2026-09-21 14:48 BRT

- **Decisão de Luis:** registrar no diário todas as perguntas e respostas desta sessão de descoberta.
- **Forma de registro:** corrigir o português, preservar o sentido e anotar a decisão resultante sem transformar resposta parcial em requisito definitivo.
- **Estado:** Onda 1 em andamento; uma decisão aprovada e seus detalhes ainda em investigação.

### Onda 1 — Resultado e usuário

#### Pergunta 1

Na segunda-feira de manhã, qual decisão principal o vendedor deve conseguir tomar em até 60 segundos ao abrir a ferramenta?

#### Resposta de Luis

**D:** uma fila única que combine prioridade, risco, valor e próxima ação.

#### Decisão registrada

A experiência principal será uma fila unificada de trabalho, não quatro relatórios separados. A resposta ainda não define pesos, regras de desempate, público secundário ou forma de cálculo; esses pontos permanecem abertos para as próximas perguntas.

#### Pergunta 2

Quem precisa usar a primeira versão?

#### Resposta de Luis

**B:** vendedor e manager, com visão individual e da equipe.

#### Decisão registrada

A primeira versão terá dois públicos. O vendedor precisa operar a própria fila; o manager precisa enxergar o desempenho e as prioridades da equipe. Permissões de alteração, intervenção e redistribuição ainda não foram definidas.

#### Pergunta 3

O que o manager poderá fazer na primeira versão?

#### Resposta de Luis

**D:** visualizar, orientar, repriorizar e redistribuir deals.

#### Decisão registrada

O manager será um usuário operacional, não apenas observador. A solução deverá permitir visão da equipe, orientação ao vendedor, alteração de prioridade e redistribuição de oportunidades. Regras de permissão, histórico de alterações, conflitos e reversão permanecem abertas e precisarão ser tratadas em ondas posteriores.

#### Pergunta 4

Qual será a métrica principal de sucesso?

#### Resposta de Luis

**D:** aumento da receita esperada por vendedor.

Luis descartou “percentual de deals prioritários trabalhados em até 24 horas” como métrica norteadora porque isso deixaria uma análise importante e ambígua para a IA decidir. Considera a receita esperada por vendedor uma referência mais confiável.

#### Decisão registrada

A receita esperada por vendedor será a métrica norteadora; velocidade de ação, redução de deals frios e taxa de fechamento poderão funcionar como métricas auxiliares. A escolha reduz o risco de otimizar mera atividade, mas ainda exige uma fórmula independente, auditável e baseada apenas em informações disponíveis no momento do score. Sem isso, “receita esperada” poderia se tornar uma estimativa circular produzida pelo próprio modelo.

#### Pergunta 5

O que “receita esperada” deve significar na primeira versão?

#### Resposta final de Luis

**A:** probabilidade de fechamento × preço do produto.

#### Correção registrada

Uma mensagem intermediária respondeu apenas “C”, mas Luis a substituiu explicitamente pela opção A. A resposta final acima prevalece; a opção C não foi tratada como decisão aprovada.

#### Decisão registrada

A receita esperada de cada deal será calculada como `probabilidade de fechamento × preço do produto`. O preço vem do catálogo; a probabilidade ainda precisa ser definida, calibrada e validada somente com informação disponível no momento do score. O cálculo deverá mostrar os dois componentes ao usuário.

#### Pergunta 6

Como devemos provar que a fila melhora a receita por vendedor?

#### Resposta de Luis

**D:** duas etapas — backtest agora e piloto operacional depois.

#### Decisão registrada

A entrega atual deverá comparar retrospectivamente o ranking com resultados reais sem leakage. Como o dataset não prova adoção nem impacto causal em produção, a validação definitiva ficará para um piloto posterior com vendedores, ações e receita observadas.

### Síntese da Onda 1 — aprovada

- **Experiência principal:** fila única com prioridade, risco, valor e próxima ação.
- **Usuários:** vendedor e manager; o manager visualiza, orienta, reprioriza e redistribui.
- **Métrica norteadora:** receita esperada por vendedor.
- **Fórmula-base:** `probabilidade de fechamento × preço do produto`, com componentes visíveis.
- **Prova:** backtest sem leakage na entrega; piloto operacional como validação posterior.

Continuam abertos: definição da probabilidade, fluxo comercial real, auditoria das ações do manager e desenho da interface.

#### Aprovação de Luis

Onda 1 aprovada sem alterações em 21 de setembro de 2026. O gate de resultado e usuários foi concluído.

### Onda 2 — Fluxo comercial

#### Pergunta 1

Qual falha do fluxo atual deve ser eliminada primeiro?

**Resposta:** aguardando Luis.
