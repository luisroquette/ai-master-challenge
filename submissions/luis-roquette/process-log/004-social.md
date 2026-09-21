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

### Onda 5 — mecanismo de alerta

- **Pergunta:** o que deve fazer o painel chamar a atenção do gestor?
- **Opções:** A) desvio contextual em relação a plataforma, formato, categoria e faixa de creator; B) limites fixos; C) ranking absoluto do período.
- **Resposta de Luis:** **A com C** — desvio contextual como mecanismo recomendado, acompanhado por ranking absoluto.
- **Implicação:** o painel deverá priorizar anomalias contra grupos comparáveis e usar rankings como contexto secundário. Números absolutos não poderão, isoladamente, sustentar uma recomendação.
- **Estado das ondas:** o mínimo de cinco ondas foi atingido, mas a descoberta continuará porque ainda existem decisões de arquitetura, governança e validação em aberto.

### Onda 6 — resposta aos alertas

- **Pergunta:** após detectar um desvio, o sistema deve explicar e sugerir uma ação com decisão humana, alterar automaticamente o plano ou apenas mostrar os dados?
- **Opções:** A) explicar o sinal e sugerir uma ação, exigindo decisão humana; B) alterar automaticamente calendário, formato ou investimento; C) mostrar somente os dados, sem recomendar ação.
- **Resposta de Luis:** **A — explicar o sinal e sugerir uma ação, exigindo decisão humana**.
- **Implicação:** a IA terá papel assistivo e explicável. O sistema poderá recomendar, mas não executará mudanças de calendário ou investimento sem aprovação do gestor; evidência, incerteza e justificativa deverão acompanhar cada sugestão.

### Onda 7 — entrada de dados do MVP

- **Pergunta:** como o sistema deve receber novos dados?
- **Opções:** A) importação manual de CSV; B) integração direta com APIs das plataformas; C) modelo híbrido, com CSV funcional agora e arquitetura preparada para APIs futuras.
- **Resposta de Luis:** **C**, deixando claro que, para o MVP, foi escolhida uma solução simplificada e manual.
- **Implicação:** o MVP aceitará arquivos CSV com validação explícita. Integrações com APIs serão apenas uma possibilidade futura; não haverá conectores, autenticação ou sincronização automática no escopo inicial.
- **Simplificação deliberada:** a extensibilidade futura não autoriza abstrações ou infraestrutura especulativas. O código do MVP deverá permanecer mínimo e orientado ao formato de dados comprovado.

### Onda 8 — formato de uso do MVP

- **Pergunta:** onde os três perfis devem usar o sistema?
- **Opções:** A) dashboard web local; B) planilha enriquecida; C) notebook analítico.
- **Resposta de Luis:** **A — dashboard web local**.
- **Implicação:** o MVP deverá permitir importar o CSV e navegar visualmente por monitoramento, desvios contextuais, rankings e recomendações. A ferramenta deverá funcionar localmente e ser demonstrável sem infraestrutura remota obrigatória.

### Onda 9 — experiência dos três perfis

- **Pergunta:** como o dashboard deve atender Gestor, Head e Analista?
- **Opções:** A) cockpit principal para o Gestor, com resumos semanais e mensais exportáveis; B) três áreas separadas; C) interface única com seletor de perfil.
- **Resposta de Luis:** **A — cockpit principal para o Gestor, com resumos exportáveis para os demais**.
- **Implicação:** haverá uma única experiência operacional, centrada no Gestor de Social Media. Head e Analista consumirão sínteses derivadas da mesma fonte, evitando três produtos, permissões ou navegações independentes no MVP.

### Onda 10 — benchmark dos alertas

- **Pergunta:** como definir o desempenho esperado de cada post?
- **Opções:** A) mediana e distribuição de grupos comparáveis por plataforma, formato, categoria, faixa de creator e período; B) média global; C) modelo preditivo desde o MVP.
- **Resposta de Luis:** **A — grupo comparável**.
- **Implicação:** alertas serão baseados em referências robustas e contextuais. A granularidade final dependerá do tamanho real das amostras; quando um grupo for pequeno, o sistema deverá recuar para um nível comparável mais amplo e declarar essa limitação.

### Onda 11 — avaliação de patrocínios

- **Pergunta:** como o MVP deve avaliar posts patrocinados?
- **Opções:** A) comparação controlada de alcance e engajamento contra orgânicos comparáveis, sem alegar ROI financeiro sem custo; B) comparação direta de médias gerais; C) ROI calculado com custos hipotéticos.
- **Resposta de Luis:** **A — comparação controlada, sem alegação indevida de ROI financeiro**.
- **Implicação:** patrocínio será avaliado como diferença observacional de desempenho dentro de contextos comparáveis. O sistema deverá separar associação de causalidade, mostrar incerteza e declarar que retorno financeiro exige dados reais de investimento e receita.

### Onda 12 — sucesso principal do MVP

- **Pergunta:** qual prova define que o MVP funciona?
- **Opções:** A) importar um CSV e identificar desvio, evidência, contexto e próxima ação em até cinco minutos, com números rastreáveis; B) atingir uma métrica mínima de previsão; C) exibir todas as métricas e filtros do dataset.
- **Resposta de Luis:** **A — decisão rastreável em até cinco minutos**.
- **Implicação:** a definição de pronto será orientada à velocidade e à qualidade da decisão, não ao volume de funcionalidades. Cada alerta e recomendação deverá permitir chegar aos registros e cálculos que a sustentam.

### Onda 13 — ciclo de aprendizado

- **Pergunta:** o que deve acontecer com cada recomendação?
- **Opções:** A) registrar se foi aceita, rejeitada ou editada e comparar depois a decisão com o resultado observado; B) exibir temporariamente sem guardar a decisão; C) converter automaticamente em tarefa ou publicação.
- **Resposta de Luis:** **A — registrar a decisão humana e comparar com o resultado posterior**.
- **Implicação:** o sistema terá memória operacional auditável. A evolução não dependerá de a IA executar ações: dependerá de registrar a escolha humana, receber dados posteriores e confrontar recomendação, decisão e resultado sem inventar causalidade.

### Onda 14 — persistência local

- **Pergunta:** onde o MVP deve guardar decisões e resultados?
- **Opções:** A) SQLite local, sem serviço externo; B) arquivos CSV ou JSON; C) somente na sessão.
- **Resposta de Luis:** **A — SQLite local**.
- **Implicação:** decisões, revisões e resultados poderão ser consultados entre sessões com integridade transacional e trilha auditável, sem exigir conta, nuvem ou banco remoto.

### Onda 15 — retenção dos dados

- **Pergunta:** o que deve ser persistido no SQLite?
- **Opções:** A) decisões, resultados e metadados do arquivo, mantendo o CSV bruto fora do banco; B) toda a base importada; C) uma cópia completa de cada CSV enviado.
- **Resposta de Luis:** **A — persistir decisões, resultados e metadados; não copiar o CSV bruto**.
- **Implicação:** o banco manterá o estado operacional mínimo. Cada importação poderá ser identificada por metadados e hash, enquanto análises serão recalculadas a partir do arquivo fornecido pelo usuário, reduzindo duplicação e exposição de dados.

### Onda 16 — motor de recomendações

- **Pergunta:** como o MVP deve produzir recomendações?
- **Opções:** A) regras estatísticas determinísticas, com evidência, benchmark e justificativa reproduzível; B) API de IA generativa; C) modelo local de IA.
- **Resposta de Luis:** **A — regras estatísticas determinísticas**.
- **Implicação:** recomendações deverão resultar de cálculos e regras auditáveis. Nenhuma API paga, modelo generativo ou dependência de inferência será necessária para operar o MVP.

### Onda 17 — comunicação da incerteza

- **Pergunta:** como cada alerta deve demonstrar sua confiabilidade?
- **Opções:** A) mostrar benchmark, tamanho da amostra, diferença observada e nível de confiança; B) usar apenas um semáforo; C) apresentar somente uma explicação textual.
- **Resposta de Luis:** **A — evidência quantitativa e nível de confiança**.
- **Implicação:** todo alerta deverá expor os elementos mínimos para auditoria. Grupos insuficientes deverão ser sinalizados, e uma recomendação não poderá aparentar certeza maior que a sustentada pelos dados.

### Onda 18 — navegação do dashboard

- **Pergunta:** como organizar a experiência principal?
- **Opções:** A) visão geral com alertas prioritários e detalhamento sob demanda; B) páginas separadas por tema; C) página única extensa.
- **Resposta de Luis:** **A — visão geral com drill-down**.
- **Implicação:** o dashboard deverá começar pelo que exige atenção e permitir aprofundamento progressivo até os registros e cálculos. A arquitetura de informação evitará tanto fragmentação por excesso de páginas quanto uma tela única sobrecarregada.

### Onda 19 — prioridade dos alertas

- **Pergunta:** como ordenar os alertas na visão geral?
- **Opções:** A) impacto × confiança × atualidade; B) maior variação percentual; C) ordem cronológica.
- **Resposta de Luis:** **A — impacto × confiança × atualidade**.
- **Implicação:** uma anomalia extrema, mas pequena ou pouco sustentada, não dominará automaticamente o painel. A fórmula final deverá ser simples, documentada e testada, sem esconder seus componentes em um score opaco.

### Onda 20 — definição de impacto

- **Pergunta:** sem dados financeiros, como medir o impacto de um alerta?
- **Opções:** A) volume potencial afetado, combinando alcance, interações e exposição do creator, separado da confiança estatística; B) somente engagement rate; C) importância subjetiva atribuída pelo gestor.
- **Resposta de Luis:** **A — volume potencial afetado**.
- **Implicação:** o dashboard priorizará escala observável sem chamá-la de receita ou ROI. Taxa e volume serão apresentados juntos para evitar favorecer artificialmente creators grandes ou pequenos.

### Onda 21 — arquivo inválido

- **Pergunta:** como o MVP deve reagir a um CSV incompleto ou inconsistente?
- **Opções:** A) bloquear a análise e mostrar coluna, problema e correção esperada; B) importar apenas linhas válidas e descartar as demais; C) corrigir automaticamente sem confirmação.
- **Resposta de Luis:** **A — bloquear e apresentar diagnóstico acionável**.
- **Implicação:** a validação da entrada será um gate. O sistema não produzirá indicadores sobre uma base parcialmente descartada ou modificada sem conhecimento do usuário; o erro deverá indicar localização, causa e correção.

### Onda 22 — saída para Head e Analista

- **Pergunta:** o que o dashboard deve exportar?
- **Opções:** A) resumo executivo de uma página e CSV das evidências e decisões; B) relatório técnico completo em PDF; C) somente imagens dos gráficos.
- **Resposta de Luis:** **A — resumo executivo e CSV rastreável**.
- **Implicação:** o Head receberá síntese curta e priorizada; o Analista poderá auditar os dados estruturados. A exportação evitará um relatório longo que replique toda a interface.

### Onda 23 — uso dos dados de audiência

- **Pergunta:** como audiência deve influenciar a análise?
- **Opções:** A) usar idade, gênero e localização nos benchmarks e filtros quando houver amostra suficiente; B) criar clusters e personas automáticas; C) mostrar demografia sem influenciar alertas.
- **Resposta de Luis:** **A — segmentação contextual condicionada à suficiência da amostra**.
- **Implicação:** audiência fará parte do contexto analítico, mas não fragmentará grupos até perder validade. O sistema deverá recuar a uma segmentação mais ampla e informar o usuário quando a amostra não sustentar o corte solicitado.

### Onda 24 — diferencial do MVP

- **Pergunta:** qual deve ser o diferencial principal da entrega?
- **Opções:** A) cockpit decisório completo, com alertas contextuais, recomendações explicáveis, decisão humana e aprendizado posterior; B) modelo preditivo adicional; C) módulo avançado de hashtags adicional.
- **Resposta de Luis:** **A — cockpit decisório completo**.
- **Implicação:** o diferencial virá da integração disciplinada entre análise, decisão e aprendizado, não da acumulação de módulos. Modelo preditivo e análise avançada de hashtags ficam fora do MVP, salvo se a pesquisa ou os dados provarem que são necessários.
- **Estado da descoberta:** 24 ondas concluídas. Problema, usuários, cadência, entrada, persistência, análise, confiança, decisão, exportação e diferencial têm direção suficiente para comparar arquiteturas antes da SPEC.

## I06 — Arquitetura-base escolhida pelo briefing — 2026-09-21 16:33 BRT

- **Pergunta:** entre monólito web local, frontend com API separada, aplicativo desktop, planilha, plataforma preditiva e sistema generativo, qual arquitetura segue mais fielmente o Challenge 004?
- **Decisão:** **monólito web local** — interface, análise determinística, SQLite e exportações no mesmo projeto.
- **Evidência do briefing:** a entrega obrigatória combina análise de performance e estratégia; o diferencial aceita explicitamente um dashboard interativo ou qualquer ferramenta que transforme dados em decisão recorrente; o resultado deve ser acionável, priorizado e compreensível em cinco minutos.
- **Adequação:** uma aplicação local única entrega importação manual, análise controlada, alertas, drill-down, recomendações, registro de decisões e exportações sem exigir API, nuvem ou múltiplos serviços.
- **Rejeições:** separar frontend e API ou empacotar desktop adiciona infraestrutura sem requisito; planilha e relatório enfraquecem o ciclo diário; ML e agentes generativos aumentam risco, custo e opacidade sem resolver os critérios obrigatórios.
- **Verificação:** o README local e o `main` remoto eram idênticos no blob Git `52b10db595fb2a3f50c8a7cc73573fa53f5db087` no momento da decisão.
- **Limite:** o padrão arquitetural está decidido; framework e bibliotecas só serão escolhidos após a pesquisa obrigatória e reprodução de candidatos.

## I07 — Pesquisa obrigatória e escolha do framework — 2026-09-21 17:25 BRT

- **Decisão registrada:** pesquisar e reproduzir alternativas antes de escolher o framework e somente depois escrever a SPEC. A ordem evita transformar preferência técnica em requisito.
- **Dataset verificado:** o arquivo público possui 52.214 linhas, 27 colunas, cinco plataformas, 22.314 posts patrocinados e 29.900 orgânicos; não contém investimento, receita ou conversão.
- **Frameworks comparados:** Streamlit, Dash e Panel, com verificação de documentação oficial, licença, atividade, releases, testes e relatos de uso.
- **Soluções prontas comparadas:** três repositórios MIT de dashboards sociais/marketing. O mais próximo oferece bons padrões de validação, mas usa outro schema e uma pilha maior que o necessário.
- **Escolha:** Streamlit 1.64 + Pandas + SQLite da biblioteca padrão. É a menor pilha que cobre upload, validação, análise, drill-down, decisão persistida e exportação.
- **Reprodução:** o spike local passou health check, upload automatizado, renderização de KPI/gráfico/tabela, controle de download visível e persistência SQLite. A conclusão do download não foi testada no spike. Evidência salva em `process-log/evidence/004/framework-research/streamlit-proof.png`.
- **Limite deliberado:** nada de API separada, cloud, autenticação, DuckDB, ML ou LLM no MVP. Estado durável vai para SQLite; o CSV bruto permanece fora do banco.
- **Registro de correções durante a pesquisa:** uma variável `path` sobrescreveu o `PATH` especial do zsh; foi renomeada sem modificar arquivos. O primeiro seletor Playwright encontrou a área visual do upload, não o `input`; a verificação foi corrigida para `input[type="file"]` e passou.
- **Documento completo:** `submissions/luis-roquette/research/004-social.md`.

## I08 — SPEC elaborada pela metodologia SDD — 2026-09-21

- **Ordem aplicada:** pesquisa obrigatória → task inicial → análise de negócio → arquitetura → decomposição → julgamentos → SPEC canônica. A implementação não começou.
- **Artefato canônico:** `submissions/luis-roquette/solution/004-social/SPEC.md`; o pacote operacional SDD permanece local em `.specs/` e `.claude/`.
- **Qualidade validada:** pesquisa 4,18/5; análise do codebase 4,20/5; análise de negócio 4,47/5; arquitetura 4,38/5; decomposição 4,28/5.
- **Correção analítica decisiva:** a primeira arquitetura comparava a taxa de um post com a distribuição das medianas por creator. O julgamento detectou unidades observacionais diferentes; o contrato passou a comparar post com distribuição de posts e manteve medianas por creator apenas na análise de patrocínio.
- **Correções de dados:** o CSV não contém `engagement_rate`; a taxa será derivada e versionada. Campos de audiência são rótulos categóricos, não percentuais. O snapshot não contém zeros nas cinco métricas verificadas, limitação que deve ser mostrada.
- **Planejamento:** quatro passos em duas fases, estimativa otimista de 310 minutos de implementação ativa após o planejamento, mais 50 minutos de contingência. O tempo de pesquisa/planejamento não foi medido e não será ocultado.
- **Gate seguinte:** revisão humana da SPEC. Escrever e revisar a SPEC não autoriza implementação, push, PR, publicação ou uso de API paga.

## I09 — Auditoria final da SPEC em loop — 2026-09-21

- **Método:** duas passadas completas e independentes precisavam terminar consecutivamente sem novos achados.
- **Achados corrigidos antes da contagem final:** o spike apenas mostrou o controle de download, sem concluir um download; comparações posteriores agora exigem janelas equivalentes ou normalização diária; 27 colunas menos 16 obrigatórias resultam em 11 opcionais, não 10.
- **Resultado:** passadas finais A e B sem novos achados. Links, caminhos SDD, requisitos, métricas, causalidade, critérios, testes e sincronização entre task e SPEC foram reavaliados.
- **Identidade auditada:** SHA-256 da SPEC `a70a5e7f5dfbf6614cb59c0d72266df6bcbb5ac8bd662f101a212688ff631ea9`.
- **Limite:** o goal de absorção/revisão documental foi atingido; não é prova de runtime e não substitui a revisão humana anterior à implementação.
