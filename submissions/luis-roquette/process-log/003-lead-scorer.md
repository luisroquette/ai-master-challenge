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

#### Resposta de Luis

**A, seguida de B:** primeiro eliminar a priorização subjetiva, feita “no feeling”; depois reduzir o esforço causado pelo volume excessivo de oportunidades.

#### Decisão registrada

A solução deve primeiro instituir um critério comum, explicável e auditável. A redução de carga cognitiva vem em seguida: o sistema usa esse critério para transformar o pipeline extenso em uma fila curta e acionável. Filtrar volume sem padronizar a decisão apenas automatizaria o “feeling”.

#### Pergunta 2

Em que momento do fluxo a ferramenta deve intervir primeiro?

#### Resposta de Luis

**B:** continuamente, reordenando a fila quando os dados mudarem.

Luis escolheu a opção depois de comparar fila diária, atualização contínua, publicação pelo manager e análise sob demanda.

#### Decisão registrada

O comportamento-alvo é uma fila continuamente recalculada a partir de novas informações do CRM. Como o dataset do challenge é estático, a entrega atual demonstrará o mesmo mecanismo ao recalcular após atualização ou recarga dos dados; não alegará possuir uma integração em tempo real que não foi construída nem validada.

#### Pergunta 3

Como evitar que a reordenação contínua torne a fila instável ou difícil de confiar?

#### Resposta de Luis

**B:** reordenar somente quando a mudança ultrapassar um limite relevante.

#### Decisão registrada

A atualização dos dados pode ser contínua, mas uma alteração pequena não deve mudar a ordem exibida. A fila terá um mecanismo de estabilidade: somente variações materiais atravessam o limite de reordenação. O valor e a unidade desse limite ainda não foram definidos e não serão inventados antes da análise dos dados.

#### Pergunta 4

Como o limite de mudança relevante deve ser definido?

#### Recomendação da IA

Combinar **B + D**: medir a mudança pela variação percentual da receita esperada e calibrar o percentual com dados reais, mantendo-o configurável. No protótipo estático, recalcular toda a fila quando os dados forem atualizados; no produto integrado, aplicar o limite calibrado.

#### Decisão de Luis

Recomendação aprovada sem alterações.

#### Decisão registrada

O protótipo fará recálculo completo após nova carga de dados. O produto real usará variação percentual da receita esperada, com limite configurável e calibrado durante o piloto. Nenhum percentual será inventado com o dataset estático, que não contém snapshots sucessivos suficientes para validar instabilidade da fila.

#### Pergunta 5

Como uma repriorização manual feita pelo manager deve conviver com o recálculo automático?

#### Resposta de Luis

**A:** a repriorização manual desaparece no próximo recálculo.

#### Decisão registrada

A intervenção do manager será temporária e não modificará score, pesos ou fórmula. O próximo recálculo restabelece integralmente a ordem derivada dos dados. Essa escolha mantém uma única fonte de verdade para o ranking, mas exige comunicar claramente ao manager que a mudança não é persistente.

#### Pergunta 6

Mesmo sendo temporária, a intervenção do manager deve deixar qual evidência?

#### Resposta de Luis

**B:** registrar apenas quem alterou e quando.

#### Decisão registrada

A auditoria mínima da repriorização guardará identidade do manager e horário. Justificativa, comparação antes/depois e resultado posterior do deal não serão obrigatórios na primeira versão.

### Síntese da Onda 2 — aprovada

- **Problema primário:** substituir priorização subjetiva; depois reduzir o volume analisado.
- **Atualização:** recalcular continuamente quando os dados mudarem, mas reordenar apenas após mudança material.
- **Protótipo:** recalcular toda a fila após nova carga; sem alegar integração em tempo real.
- **Produto real:** usar variação percentual configurável, calibrada no piloto.
- **Intervenção do manager:** repriorização temporária até o próximo recálculo, auditando apenas quem e quando.

Permanecem para ondas posteriores: persistência de redistribuições, definição da probabilidade, eventos disponíveis no tempo, interface e limites operacionais.

#### Aprovação de Luis

Onda 2 aprovada sem alterações em 21 de setembro de 2026. O gate de fluxo comercial foi concluído.

### Onda 3 — Dados e verdade temporal

#### Pergunta 1

Quais oportunidades devem receber score e aparecer na fila operacional?

#### Resposta de Luis

**A:** somente deals ativos — `Prospecting` e `Engaging`. Deals `Won` e `Lost` servem apenas para aprendizado e validação.

#### Decisão registrada

A fila operacional excluirá oportunidades encerradas. O histórico de `Won` e `Lost` poderá ensinar e testar a probabilidade de fechamento, mas seus campos de resultado não poderão vazar para as features usadas nos deals ativos.

#### Pergunta 2

Como devemos separar os deals históricos para estimar e validar a probabilidade de fechamento?

#### Resposta de Luis

**B:** divisão temporal — deals antigos treinam; deals mais recentes validam.

#### Decisão registrada

A validação deverá simular o futuro: nenhum deal com fechamento posterior poderá informar o treinamento usado para avaliar um período anterior. O ponto de corte será escolhido somente após medir a distribuição das datas; não será definido arbitrariamente nesta conversa.

#### Evidência inspecionada antes da próxima pergunta

O arquivo real possui 8.800 oportunidades: 500 `Prospecting`, 1.589 `Engaging`, 4.238 `Won` e 2.473 `Lost`. Todos os `Prospecting` não têm `engage_date`; todos os `Engaging` têm `engage_date`, mas ainda não têm `close_date`. Os deals encerrados têm ambas as datas. O ZIP consultado tem SHA-256 `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c`.

#### Pergunta 3

Como devemos estimar a probabilidade dos `Prospecting`, já que o histórico encerrado contém apenas deals que chegaram ao engajamento?

#### Resposta de Luis

**B:** usar uma heurística baseada em produto, vendedor e conta, com o objetivo de eliminar viés.

#### Decisão registrada

`Prospecting` não usará diretamente o modelo probabilístico dos deals que já chegaram a `Engaging`. Terá uma heurística própria baseada apenas em atributos disponíveis nesse estágio. Essa separação reduz o viés de seleção, mas não autoriza afirmar que o eliminou: sem resultados históricos de oportunidades que não chegaram ao engajamento, a heurística não pode ser tratada como probabilidade calibrada.

#### Pergunta 4

Como a ferramenta deve apresentar o resultado dessa heurística de `Prospecting` sem prometer uma probabilidade que os dados não sustentam?

#### Resposta de Luis

**D:** mostrar faixa de prioridade e receita potencial, separadas da receita esperada dos `Engaging`.

#### Decisão registrada

Deals em `Prospecting` terão classificação de prioridade e preço potencial do produto. Deals em `Engaging` poderão exibir probabilidade calibrada e receita esperada. A interface deverá distinguir visualmente potencial de expectativa para evitar comparação enganosa entre métricas de naturezas diferentes.

#### Pergunta 5

Quais informações devem ser proibidas como features do modelo de `Engaging` para impedir leakage?

#### Resposta inicial de Luis

**D:** permitir campos finais durante o treinamento e removê-los apenas no uso.

#### Contestação da IA

A opção D produz leakage e diferença entre treino e uso. O modelo aprenderia atalhos a partir de `close_value`, `close_date` ou estágio final — informações que não existem quando um deal ativo recebe score. A validação pareceria melhor do que o desempenho possível em produção, contrariando o risco central explícito do challenge.

#### Recomendação corretiva — aprovada por Luis

Adotar **C**: proibir `close_value`, `close_date`, estágio final e derivados como preditores. `Won/Lost` pode ser usado somente como rótulo; `close_date`, somente para corte temporal e avaliação; `close_value`, somente para medir resultado financeiro histórico.

#### Decisão final

Luis substituiu a resposta inicial pela opção **C**. O contrato contra leakage passa a ser obrigatório no código, nos testes e na documentação do modelo.

#### Evidência de qualidade dos dados

Entre os deals ativos, 337 de 500 `Prospecting` e 1.088 de 1.589 `Engaging` não têm conta: 1.425 de 2.089, ou 68,2%. Em contraste, todos os 6.711 deals encerrados têm conta. Usar atributos da conta sem fallback criaria forte diferença entre treino e uso. Também existe `GTXPro` no pipeline, enquanto o catálogo registra `GTX Pro`; essa chave precisa de normalização explícita e testada.

#### Pergunta 6

Como devemos tratar os deals ativos sem conta associada?

#### Resposta de Luis

**C:** usar modelo completo quando houver conta e modelo fallback sem atributos de conta quando não houver.

#### Decisão registrada

O roteamento será determinado pela disponibilidade da conta. O fallback será treinado deliberadamente sem atributos de conta, não com valores médios inventados. Os dois caminhos precisarão de validação temporal própria e a interface deverá informar qual deles produziu o score.

### Síntese da Onda 3 — aprovada

- **Universo operacional:** somente `Prospecting` e `Engaging`; encerrados servem para aprendizado e validação temporal.
- **Prospecting:** heurística própria; exibe prioridade e receita potencial, não probabilidade calibrada.
- **Engaging:** probabilidade e receita esperada, com divisão temporal entre treino e validação.
- **Antileakage:** campos finais e derivados proibidos como preditores; `Won/Lost` é somente rótulo.
- **Dados incompletos:** modelo completo com conta e fallback sem conta; normalização explícita de `GTXPro` para `GTX Pro`.

Permanecem abertos: features exatas, algoritmo, calibração da probabilidade, desempenho mínimo aceitável e tratamento de categorias novas.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 3 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 4 — Score e explicação

#### Pergunta 1

Qual componente deve comandar a prioridade dos deals em `Engaging`?

- **A.** Apenas receita esperada (`probabilidade × preço`).
- **B.** Apenas probabilidade de fechamento.
- **C.** Apenas urgência ou risco de esfriamento.
- **D.** Receita esperada como base, com urgência ou risco como modificador explícito; a próxima ação permanece separada.

**Recomendação da IA:** **D**. Preserva a métrica norteadora já aprovada sem deixar oportunidades valiosas e urgentes perderem prioridade. Os pesos não serão inventados agora: deverão ser simples, visíveis e validados com o histórico disponível.

#### Resposta de Luis

**Preferência:** **B > A >>> C** — probabilidade de fechamento acima da receita esperada, ambas muito acima de urgência ou risco de esfriamento. A opção D não foi incluída.

#### Interpretação provisória

A probabilidade deve comandar a prioridade. Ainda é necessário definir se a receita esperada será apenas informativa ou se funcionará como segundo critério, pois a decisão anterior adotou receita esperada por vendedor como métrica norteadora.

#### Pergunta 2

Na fila ordenada por probabilidade, qual deve ser o papel da receita esperada?

- **A.** Apenas exibição; nunca altera a ordem.
- **B.** Segundo critério: desempata probabilidades equivalentes ou muito próximas.
- **C.** Controle alternável: o usuário escolhe ordenar por probabilidade ou receita esperada.

**Recomendação da IA:** **B**. Respeita `B > A`, mantém uma única fila objetiva e ainda conecta a ordenação à métrica financeira aprovada.

#### Resposta de Luis

**B:** a receita esperada será o segundo critério para oportunidades com probabilidades equivalentes ou próximas.

#### Decisão registrada

A fila de `Engaging` será ordenada primeiro pela probabilidade de fechamento. A receita esperada será usada como desempate controlado, sem substituir o critério principal. O significado mensurável de “probabilidades próximas” ainda deverá ser definido e validado, sem tolerância arbitrária.

#### Pergunta 3

Como cada probabilidade de fechamento deve ser explicada ao vendedor?

- **A.** Mostrar os principais fatores favoráveis e desfavoráveis, com o valor observado e seu efeito em linguagem simples.
- **B.** Mostrar somente fatores favoráveis para tornar a orientação mais positiva.
- **C.** Gerar uma justificativa narrativa livre por IA.
- **D.** Exibir somente os coeficientes e detalhes técnicos completos do modelo.

**Recomendação da IA:** **A**. É fiel ao cálculo, acionável e auditável; evita esconder sinais negativos ou inventar causalidade em uma narrativa livre.

#### Resposta de Luis

**A:** mostrar os principais fatores favoráveis e desfavoráveis, com o valor observado e seu efeito em linguagem simples.

#### Decisão registrada

A explicação será derivada do cálculo real do score, não gerada livremente. Ela deverá mostrar evidências dos dois sentidos e evitar linguagem causal quando os dados sustentarem apenas associação.

#### Pergunta 4

Qual estratégia deve decidir o modelo probabilístico de `Engaging`?

- **A.** Regressão logística como escolha fixa: máxima transparência e menor complexidade.
- **B.** Árvore de decisão rasa: regras visuais, mas divisões potencialmente instáveis.
- **C.** Gradient boosting com explicações SHAP: maior capacidade não linear, porém mais complexidade.
- **D.** Comparar regressão logística e gradient boosting na validação temporal; usar o modelo complexo somente se entregar ganho relevante, probabilidade bem calibrada e explicações fiéis.

**Recomendação da IA:** **D**, com a regressão logística como padrão em caso de desempenho equivalente. Isso mede se a complexidade se paga antes de adotá-la.

#### Resposta de Luis

**D:** comparar regressão logística e gradient boosting na validação temporal; adotar o modelo complexo somente com ganho comprovado.

#### Decisão registrada

A regressão logística será o baseline obrigatório. O gradient boosting será apenas um concorrente. Complexidade, SHAP e dependências adicionais só entram se o concorrente superar o baseline nos critérios aprovados, mantiver calibração adequada e produzir explicações fiéis. Em desempenho equivalente, vence o modelo simples.

#### Pergunta 5

Qual critério deve selecionar o vencedor entre os modelos?

- **A.** Melhor separação entre `Won` e `Lost`, independentemente da calibração.
- **B.** Menor erro das probabilidades, independentemente da qualidade da ordenação.
- **C.** Maior resultado financeiro no topo da fila histórica, mesmo com probabilidades mal calibradas.
- **D.** Gate em duas etapas: primeiro exigir probabilidades calibradas; depois comparar a qualidade da ordenação e o resultado financeiro no topo da fila. Sem ganho relevante, vence o modelo simples.

**Recomendação da IA:** **D**. A fila precisa ordenar bem, mas o número exibido como probabilidade também precisa ser confiável.

#### Resposta de Luis

**D:** aplicar um gate de calibração e, entre os modelos aprovados, comparar ordenação e resultado financeiro; sem ganho relevante, vence o modelo simples.

#### Decisão registrada

Nenhum modelo poderá vencer apenas por discriminar bem se suas probabilidades forem pouco confiáveis. Após o gate de calibração, a seleção considerará a capacidade de priorizar `Won` e concentrar resultado financeiro no topo da fila. A magnitude mínima de ganho relevante será definida a partir da variabilidade observada na validação, não por um número arbitrário.

#### Pergunta 6

Quando duas probabilidades devem ser consideradas “próximas” para permitir o desempate por receita esperada?

- **A.** Quando forem iguais após arredondamento para percentual inteiro.
- **B.** Quando estiverem a até 5 pontos percentuais, como regra fixa.
- **C.** Quando pertencerem à mesma faixa de probabilidade cuja confiabilidade foi confirmada na validação temporal.
- **D.** Nunca; receita esperada só desempata probabilidades exatamente iguais.

**Recomendação da IA:** **C**. Evita precisão falsa e deriva o desempate da resolução que os dados realmente sustentam.

#### Resposta de Luis

**C:** probabilidades serão consideradas próximas quando pertencerem à mesma faixa cuja confiabilidade foi confirmada na validação temporal.

#### Decisão registrada

A interface não tratará diferenças menores do que a resolução sustentada pelos dados como precisão real. Dentro da mesma faixa validada, a receita esperada poderá desempatar; entre faixas distintas, prevalecerá a probabilidade. As faixas deverão ser derivadas e reportadas pela validação.

#### Pergunta 7

Como transformar produto, vendedor e conta em uma prioridade explicável para `Prospecting`, sem chamar o resultado de probabilidade?

- **A.** Usar taxas históricas brutas de sucesso para cada combinação.
- **B.** Usar evidências históricas suavizadas: combinações com poucos casos recuam progressivamente para grupos mais gerais, e a interface informa a força da evidência.
- **C.** Definir pesos manuais fixos para produto, vendedor e conta.
- **D.** Reutilizar o modelo de `Engaging`, mas ocultar a probabilidade.

**Recomendação da IA:** **B**. Evita que grupos pequenos pareçam conclusivos, mantém o cálculo auditável e lida com categorias raras ou novas sem inventar certeza.

#### Resposta de Luis

**B:** usar evidências históricas suavizadas, com recuo progressivo para grupos mais gerais e indicação da força da evidência.

#### Decisão registrada

A prioridade de `Prospecting` não usará taxas brutas de grupos pequenos nem pesos arbitrários. O cálculo deverá reduzir o efeito de amostras escassas, recorrer a evidências mais gerais quando necessário e declarar a sustentação disponível. O resultado continuará sendo faixa de prioridade, não probabilidade calibrada.

### Síntese da Onda 4 — aprovada

- **Ordem de `Engaging`:** probabilidade primeiro; receita esperada desempata somente dentro da mesma faixa validada.
- **Explicação:** fatores favoráveis e desfavoráveis derivados do cálculo real, com evidência observada, efeito simples e sem alegação causal indevida.
- **Modelos:** regressão logística como baseline e gradient boosting como concorrente; complexidade só entra com ganho relevante e explicação fiel.
- **Seleção:** calibração é gate; depois são avaliadas ordenação e concentração de resultado financeiro; empate favorece simplicidade.
- **`Prospecting`:** prioridade por evidências históricas suavizadas, com recuo para grupos gerais e força da evidência visível; nunca apresentada como probabilidade.

Permanecem para as ondas seguintes: interação e estados da interface, tratamento operacional de dados fora do domínio, arquitetura executável e critérios finais de prova.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 4 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 5 — Experiência e operação

#### Pergunta 1

Como a experiência deve permanecer unificada sem misturar a probabilidade calibrada de `Engaging` com a faixa heurística de `Prospecting`?

- **A.** Uma única lista intercalada, ordenando os dois tipos por um score comum.
- **B.** Uma única tela com duas filas ou abas: `Engaging` e `Prospecting`, cada uma com sua própria ordenação e linguagem.
- **C.** Uma única lista agrupada primeiro por estágio e depois pelo score de cada estágio.
- **D.** Exibir apenas `Engaging` na fila principal e deixar `Prospecting` em uma tela secundária.

**Recomendação da IA:** **B**. Mantém um ponto operacional único sem fabricar equivalência entre probabilidade e heurística.

#### Resposta de Luis

**B:** uma única tela com duas filas ou abas, uma para `Engaging` e outra para `Prospecting`.

#### Decisão registrada

A ferramenta terá uma entrada operacional única, mas preservará dois contextos de decisão. Cada aba terá ordenação, rótulos e explicações compatíveis com a evidência disponível naquele estágio. Não existirá score comum para intercalar as duas filas.

#### Pergunta 2

Qual escopo deve abrir por padrão para cada perfil?

- **A.** Vendedor e gestor sempre veem toda a equipe.
- **B.** Vendedor abre apenas sua carteira; gestor abre a equipe e pode filtrar por vendedor.
- **C.** Ambos abrem apenas a própria carteira.
- **D.** A tela sempre restaura o último filtro usado, independentemente do perfil.

**Recomendação da IA:** **B**. Reduz ruído para o vendedor e entrega visão de gestão sem criar duas experiências separadas.

#### Resposta de Luis

**B:** vendedor abre apenas sua carteira; gestor abre a equipe e pode filtrar por vendedor.

#### Decisão registrada

O escopo inicial será orientado ao papel. A visão do vendedor reduz a carga à carteira sob sua responsabilidade. A visão do gestor oferece panorama da equipe e recorte por vendedor, preservando a mesma estrutura de filas e métricas.

#### Pergunta 3

Como equilibrar leitura rápida e explicação detalhada em cada fila?

- **A.** Exibir todos os fatores e dados diretamente em cada linha.
- **B.** Usar linha compacta com prioridade, valor e principal motivo; ao selecionar, abrir painel lateral com explicação completa e próxima ação.
- **C.** Mostrar somente cartões grandes, um deal por bloco.
- **D.** Exibir uma tabela de dados brutos e deixar a interpretação para o usuário.

**Recomendação da IA:** **B**. Permite percorrer a fila rapidamente e mantém a justificativa acessível sem poluir a comparação.

#### Resposta de Luis

**B:** linha compacta com prioridade, valor e principal motivo; painel lateral com explicação completa e próxima ação.

#### Decisão registrada

A fila otimizará varredura visual. A linha exibirá apenas os elementos necessários à comparação; o painel lateral preservará contexto, fatores favoráveis e desfavoráveis, origem do score, força da evidência e próxima ação. A abertura do detalhe não mudará de página.

#### Pergunta 4

Como a ferramenta deve produzir a próxima ação recomendada?

- **A.** Texto livre gerado por IA para cada deal.
- **B.** Playbook determinístico: regras explícitas combinam estágio e principal fator acionável, mostrando por que a ação foi sugerida.
- **C.** Campo preenchido manualmente pelo gestor.
- **D.** Não recomendar ação; mostrar apenas o score.

**Recomendação da IA:** **B**. É auditável, funciona sem API paga e evita recomendações inventadas; o playbook mínimo pode ser validado por testes diretos.

#### Resposta de Luis

**B:** usar um playbook determinístico baseado no estágio e no principal fator acionável.

#### Decisão registrada

A recomendação será produzida por regras versionadas e testáveis, sem chamada a modelo generativo. Cada ação deverá apontar o sinal que a ativou. Na ausência de sinal acionável suficiente, a interface declarará isso em vez de inventar uma recomendação.

#### Pergunta 5

Como o gestor deve fazer a repriorização manual temporária já aprovada?

- **A.** Arrastar qualquer deal para uma posição arbitrária na fila.
- **B.** Usar uma ação “Priorizar temporariamente”, que fixa o deal no topo, identifica a intervenção e expira na próxima recalculação.
- **C.** Digitar manualmente um número de posição.
- **D.** Alterar diretamente a probabilidade calculada.

**Recomendação da IA:** **B**. Entrega a intervenção necessária com uma regra simples, auditável e sem confundir decisão humana com previsão do modelo.

#### Resposta de Luis

**B:** usar a ação “Priorizar temporariamente”, fixando o deal no topo até a próxima recalculação.

#### Decisão registrada

A intervenção manual não mudará probabilidade, faixa ou receita esperada. O deal será destacado e fixado no topo da respectiva fila, com autor e horário visíveis. Ao recarregar ou recalcular o conjunto de dados, a intervenção expira e a ordenação calculada volta a valer.

#### Pergunta 6

Como tratar um deal ativo cujos dados não permitem score confiável, por exemplo uma categoria realmente desconhecida e sem fallback validado?

- **A.** Aplicar silenciosamente o valor médio e manter um score numérico.
- **B.** Manter o deal na fila com estado “Dados insuficientes”, sem score enganoso, e indicar quais campos precisam de correção.
- **C.** Remover o deal da interface.
- **D.** Colocá-lo automaticamente no fim, sem explicar o motivo.

**Recomendação da IA:** **B**. Nenhuma oportunidade desaparece, e a interface transforma incerteza em uma ação concreta de qualidade de dados.

#### Resposta de Luis

**B:** manter o deal na fila com estado “Dados insuficientes”, sem score, indicando os campos que precisam de correção.

#### Decisão registrada

Deals sem suporte de dados permanecerão visíveis, mas não receberão número ou faixa que sugira confiança inexistente. A interface explicará o bloqueio e os dados a corrigir. O fallback sem conta continua válido quando aplicável; “Dados insuficientes” cobre somente casos fora dos caminhos validados.

### Síntese da Onda 5 — aprovada

- **Estrutura:** uma tela com filas separadas de `Engaging` e `Prospecting`, sem score comum entre estágios.
- **Papéis:** vendedor abre sua carteira; gestor abre a equipe e pode filtrar por vendedor.
- **Leitura:** linhas compactas para comparação e painel lateral com explicação, origem, evidência e próxima ação.
- **Operação:** próxima ação vem de playbook determinístico; gestor pode fixar temporariamente um deal no topo sem alterar o score.
- **Incerteza:** dados fora dos caminhos validados permanecem visíveis como “Dados insuficientes”, com correção indicada e sem score enganoso.

Permanecem para a Onda 6: arquitetura mínima, fronteira do protótipo, persistência, execução, testes e prova final.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 5 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 6 — Arquitetura e prova

#### Evidência antes da arquitetura

O repositório não prescreve stack nem possui aplicação-base. O challenge exige software funcional, dados reais, scoring explicável e setup reproduzível dentro de um orçamento sugerido de 4–6 horas. Portanto, a arquitetura deve minimizar integração acidental e concentrar esforço na qualidade do produto e da prova.

#### Pergunta 1

Qual arquitetura deve sustentar o protótipo funcional?

- **A.** Aplicação Python em Streamlit, com preparação de dados, scoring e interface no mesmo projeto.
- **B.** Frontend React e API Python separados.
- **C.** HTML/JavaScript estático consumindo scores pré-calculados.
- **D.** CLI Python que gera relatório priorizado.

**Recomendação da IA:** **A**. Entrega interface interativa, filtros, modelo e explicações com o menor número de partes, sem sacrificar nenhum requisito obrigatório.

#### Resposta de Luis

**A:** aplicação Python em Streamlit, com preparação de dados, scoring e interface no mesmo projeto.

#### Decisão registrada

O protótipo será uma aplicação Streamlit autocontida dentro da pasta da submissão. A separação interna será apenas a necessária para manter ingestão, scoring, interface e testes compreensíveis; não haverá frontend e API independentes.

#### Evidência das regras de submissão

O guia exige código-fonte, setup reproduzível e todos os arquivos da entrega dentro de `submissions/luis-roquette/`. Não há proibição de versionar o dataset CC0 dentro dessa pasta.

#### Pergunta 2

Como garantir que o avaliador rode a solução com os dados reais sem depender de credenciais externas?

- **A.** Versionar uma cópia dos quatro CSVs na solução, acompanhada de fonte, licença e checksums.
- **B.** Baixar os dados pela API do Kaggle durante o setup, exigindo credenciais do avaliador.
- **C.** Baixar automaticamente de uma URL externa não controlada na primeira execução.
- **D.** Pedir que o avaliador obtenha e copie os arquivos manualmente.

**Recomendação da IA:** **A**. O conjunto é pequeno, CC0 e fica reproduzível mesmo se Kaggle ou credenciais estiverem indisponíveis.

#### Resposta inicial e correção de Luis

Luis respondeu primeiro **“A com fallback em B”** e, em seguida, corrigiu para **“A com fallback em C”**. A segunda resposta substitui a primeira.

#### Decisão final

Os quatro CSVs reais serão versionados como fonte primária, com origem, licença e checksums. Um comando explícito de recuperação poderá baixar uma cópia de uma URL pública; ele não rodará silenciosamente na abertura do app e só substituirá arquivos após validar os checksums esperados. Falha de rede ou conteúdo divergente deverá preservar os dados existentes e encerrar com erro claro.

#### Pergunta 3

Quando o treinamento e a validação dos modelos devem acontecer no protótipo?

- **A.** Na primeira abertura do app, de forma determinística, com resultado armazenado em cache durante a execução.
- **B.** Antes da entrega; o app carrega um artefato pronto e um comando separado permite reproduzir o treino.
- **C.** Nunca no projeto; somente scores finais pré-calculados são versionados.
- **D.** A cada filtro ou interação da interface.

**Recomendação da IA:** **A**. Com cerca de 6,7 mil deals encerrados, o treino local é pequeno; executá-lo uma vez e manter em cache prova o pipeline completo sem artefato binário frágil.

#### Resposta de Luis

**A:** treinar e validar na primeira abertura, de forma determinística, mantendo o resultado em cache durante a execução.

#### Decisão registrada

O app executará o pipeline real uma vez por versão dos dados e da configuração, com seed fixa e cache por fingerprint. Filtros e navegação reutilizarão o resultado. Uma mudança nos dados ou na configuração invalidará o cache e provocará nova avaliação antes de publicar scores.

#### Pergunta 4

Onde a intervenção temporária do gestor deve persistir no protótipo?

- **A.** Apenas na sessão do navegador; um refresh apaga a intervenção.
- **B.** Em SQLite local, com autor, horário e fingerprint dos dados; uma nova versão dos dados invalida a intervenção.
- **C.** Alterando diretamente os CSVs originais.
- **D.** Em banco externo com autenticação completa.

#### Questionamento de Luis

“Como o README do projeto/desafio manda? Você é quem precisa averiguar e dizer.”

#### Verificação e correção da IA

O README não exige persistência, banco, autenticação nem auditoria durável. Ele exige solução funcional, dados reais, scoring explicável, setup, lógica e limitações; também orienta começar simples dentro de 4–6 horas. SQLite seria uma expansão criada pela IA, não uma exigência do desafio.

**Recomendação corrigida da IA:** **A**. Manter a intervenção em `session_state`, exibindo gestor e horário durante a sessão, satisfaz o comportamento temporário já aprovado. A ausência de persistência multiusuário será declarada como limitação e caminho de escala.

#### Resposta de Luis

**A:** persistência apenas na sessão do navegador.

#### Decisão registrada

A repriorização temporária usará `st.session_state`, com gestor selecionado e horário visíveis durante a sessão. Ela não será apresentada como auditoria persistente nem autenticação real. Refresh, nova sessão ou recalculação poderão removê-la; esse limite será documentado.

#### Pergunta 5

Qual conjunto de provas deve acompanhar a entrega funcional?

- **A.** Testes automatizados dos contratos críticos, smoke test de inicialização e evidência visual do fluxo principal executado com os dados reais.
- **B.** Apenas inspeção manual da interface.
- **C.** Apenas métricas do modelo em um relatório.
- **D.** Uma suíte extensa de testes ponta a ponta para todos os controles.

**Recomendação da IA:** **A**. Prova scoring, antileakage, fallbacks e execução sem transformar o challenge em um projeto de infraestrutura de testes.

#### Resposta de Luis

**A:** testes automatizados dos contratos críticos, smoke test e evidência visual do fluxo principal com os dados reais.

#### Decisão registrada

A entrega deverá provar, no mínimo, ingestão e joins, bloqueio de leakage, separação temporal, roteamento completo/fallback, ordenação, explicações e playbook. Também deverá iniciar o Streamlit em smoke test e registrar uma evidência visual do fluxo vendedor/gestor. Métricas isoladas não serão aceitas como prova de produto.

#### Pergunta 6

Qual contrato de ambiente deve ser oferecido ao avaliador?

- **A.** Python 3.11, ambiente virtual e `requirements.txt` com versões fixadas, além de comandos curtos para instalar, testar e executar.
- **B.** Docker como única forma de execução.
- **C.** `uv` obrigatório com lockfile.
- **D.** Conda obrigatório com arquivo de ambiente.

**Recomendação da IA:** **A**. Usa ferramentas amplamente disponíveis e reduz pré-requisitos; Docker ou outro gerenciador não resolve requisito adicional do brief.

#### Pergunta de Luis

“O que manda o desafio?”

#### Resposta verificada

O challenge declara que a tecnologia não importa, desde que a solução rode, use dados reais, aplique scoring e explique o resultado. Na documentação, exige setup com dependências e comandos. Não impõe Docker, `uv`, Conda nem uma versão de Python.

#### Decisão técnica

Adotar **A**: Python 3.11, `venv`, `requirements.txt` com versões fixadas e comandos curtos de instalação, teste e execução. É a opção com menos pré-requisitos que atende integralmente ao brief.

#### Pergunta 7

Qual deve ser o alcance de disponibilização da aplicação?

- **A.** Execução local reproduzível como única entrega.
- **B.** Execução local obrigatória e, após todos os gates, demo pública em Streamlit Community Cloud como conveniência adicional.
- **C.** Apenas demo pública, sem garantir execução local.
- **D.** Deploy obrigatório em infraestrutura própria com Docker.

**Recomendação da IA:** **B**. A prova local continua independente de terceiros, enquanto a demo pública reduz o atrito para o avaliador; publicação só ocorrerá após validação e autorização explícita.

**Resposta:** aguardando Luis.
