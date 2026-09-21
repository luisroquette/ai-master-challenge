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

## I10 — Otimização do plano com `writing-plans` em loop — 2026-09-21

- **Decisão:** aplicar a skill `writing-plans` à SPEC e continuar em cascata até obter duas passadas consecutivas sem melhorias substanciais.
- **Artefato novo:** `submissions/luis-roquette/solution/004-social/IMPLEMENTATION-PLAN.md`, normativo para execução e vinculado pela SPEC.
- **Melhorias incorporadas:** seis tasks TDD; 44 ações rastreáveis; interfaces e arquivos exatos; testes separados por responsabilidade; mapa CK/HR; seis commits pequenos; tempo ativo total limitado a 360 minutos.
- **Erros prevenidos durante o loop:** exemplos não coletáveis pelo `unittest`; placeholders `...`; staging de novos arquivos dentro de `submissions/` ignorada; caminho incorreto da CLI; `sys.path` incorreto no discovery; conflito entre o plano novo e subtarefas SDD antigas; contrato inconsistente entre `load_csv`, `derive_metrics` e `analyze`.
- **Bordas transformadas em regressões:** arquivo acima de 50 MiB, CSV vazio/malformado, cabeçalho duplicado, timezone misturado, zeros, creator repetido, IQR constante, composição desigual de patrocínio, fórmula CSV, rollback e janelas temporais desiguais.
- **Passada limpa 1:** nenhuma melhoria substancial em cobertura, interfaces, comandos, dependências ou gates.
- **Passada limpa 2:** revisão inversa, do handoff à ingestão, sem melhoria substancial; todos os CK-01–11 e HR-01–04 possuem task e prova primária.
- **Goal atingido:** duas passadas consecutivas sem melhorias ou otimizações substanciais apontadas.
- **Limite:** o plano foi otimizado e revisado; implementação, push, PR e deploy continuam não autorizados até a revisão humana.

## I11 — Auditoria final contra o repositório e a stack — 2026-09-21

- **Fonte remota:** `main` do fork em `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; o briefing do Challenge 004 permanece no blob `52b10db595fb2a3f50c8a7cc73573fa53f5db087`, idêntico ao já absorvido.
- **Arquivos relidos:** README raiz, briefing completo, `submission-guide.md`, `CONTRIBUTING.md` e `templates/submission-template.md`.
- **Gap crítico encontrado e corrigido:** o plano previa somente o README técnico. A entrega exige também `submissions/luis-roquette/README.md` baseado no template oficial; Task 6 agora cria e valida ambos.
- **Regras de PR incorporadas:** somente caminhos em `submissions/luis-roquette/`, branch-alvo `submission/luis-roquette`, um PR e título `[Submission] Luis Roquette — Challenge 004`. A publicação continua dependente de autorização explícita.
- **Cobertura do avaliador:** análise obrigatória, estratégia obrigatória, diferencial recorrente, comparação justa, priorização, clareza executiva, process log e formato de submissão estão mapeados a tasks e provas finais no plano.
- **Stack comprovada:** Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3, SQLite 3.50.4 e `AppTest` importaram juntos; `pip check` não encontrou dependências quebradas.
- **Prova de capacidade-base:** 52.214 linhas lidas em 0,17 s; derivação e agrupamento representativo em 0,01 s; probe total em 0,65 s, cerca de 218 MB de memória máxima e zero swap.
- **Erro operacional registrado:** o primeiro comando `gh api` deixou `?ref=main` sem aspas; o zsh tentou expandir o caractere curinga. A consulta foi repetida com o endpoint entre aspas e passou sem alterar arquivos.
- **Passada final 1:** após incluir o README obrigatório, nova comparação briefing → critérios → tasks → provas terminou sem lacunas adicionais.
- **Passada final 2:** auditoria inversa de stack, tempo, imports, dependências, staging, escopo Git e handoff terminou sem novo gargalo de plano; 360 minutos ativos, zero dependência paga e todos os CK/HR cobertos.
- **Limite de certeza:** o plano cobre integralmente os requisitos conhecidos e a stack não apresenta gargalo-base. Runtime final, achados reais, fluxo de cinco minutos, exports, persistência e setup limpo só podem ser certificados após a implementação e os gates das Tasks 1–6.

## I12 — Autorização de implementação e Feedback Looping — 2026-09-21

- **Decisão humana:** Luis autorizou o início da implementação após a pesquisa, as 24 ondas socráticas, a SPEC, o plano otimizado e a auditoria final. As perguntas, alternativas e respostas das 24 ondas permanecem registradas integralmente em I05; este marco não as resume nem substitui.
- **Metodologia obrigatória:** manter SDD como autoridade e executar em fases cronológicas, uma após a outra, pelo ciclo `Planejamento → Revisão → Execução → Teste`.
- **Feedback Looping:** cada resultado de execução e teste produz um report objetivo para a própria IA. Com base nele, a IA decide entre reforçar/corrigir o trabalho na mesma fase ou avançar para a fase seguinte.
- **Gate de avanço:** uma fase só termina quando seus critérios e testes aplicáveis estiverem validados. Se algum teste falhar, o ciclo reinicia na própria fase; nenhuma falha é transferida silenciosamente para a seguinte.
- **Cascata de loops:** cada passo do plano usa seu loop local; as revisões de fase consolidam os passos concluídos. O Definition of Done recebe um loop final independente de verificação, correção e nova verificação.
- **Reports:** registrar durante a execução, com baixa latência, o plano da fase, a revisão, os comandos realmente executados, resultados, falhas, correções, evidências e julgamento humano. Documentar é parte central da entrega, não um apêndice.
- **Mapeamento SDD:** S1 cobre Tasks 1–2 do plano; S2 cobre Task 3; S3 cobre Tasks 4–5; S4 cobre Task 6. A ordem é estritamente sequencial e preserva a prioridade da análise e da estratégia antes do cockpit.
- **Limites de autorização:** implementação local e commits da branch estão autorizados. APIs pagas, push, PR, merge, deploy, publicação, investimento ou execução externa continuam fora do escopo até autorização explícita.

## I13 — S1/Task 1: fronteira do CSV e métricas — 2026-09-21 19:16 BRT

- **Planejamento:** implementar primeiro a fronteira atômica do CSV e as fórmulas puras, sem Streamlit, SQLite, serviço ou dependência além dos pins já reproduzidos.
- **Revisão:** o contrato preservou subconjuntos válidos, zeros, hash/linhas de origem, faixas de creators e diagnósticos acionáveis; o CSV bruto permaneceu fora do repositório.
- **Execução:** foram criados `requirements.txt`, `analysis.py`, fixtures determinísticas e testes `unittest`. O primeiro run ficou vermelho pelo motivo esperado: `ModuleNotFoundError: analysis`.
- **Feedback loop:** o primeiro run verde parcial teve 13/14 testes aprovados; o único erro era um `creator_id` fornecido duas vezes no builder. A correção foi feita no helper. Warnings do Pandas revelaram dtypes `object`; a normalização passou a criar dtypes numéricos/booleanos reais e o gate foi repetido com warnings tratados como erro.
- **Teste sintético:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v` terminou com 14/14 testes aprovados em 0,515 s.
- **Teste real:** ambiente isolado em `/tmp`, Python 3.14.2, Streamlit 1.64.0 e Pandas 2.3.3; `pip check` sem dependências quebradas. O CSV público de 23.290.049 bytes reconciliou 52.214 linhas e as cinco plataformas.
- **Medição:** validação real em 1,242 s; análise inicial em 10,999 s; total 12,241 s. O caminho cabe no objetivo de decisão em cinco minutos; não foi adicionada otimização preventiva.
- **Limitação:** o teste real encontrou cobertura zero para comparação de patrocínio na janela-padrão recente, estado válido de insuficiência — não uma licença para relaxar os mínimos. Exports e CLI pertencem à S2/Task 3.

## I14 — S1/Task 2: evidência contextual e ações — 2026-09-21 19:21 BRT

- **Planejamento:** manter o núcleo comparável fixo, aplicar os cinco níveis de fallback apenas à audiência e separar alertas post a post, comparação editorial e patrocínio por creator/estrato.
- **Revisão:** a fórmula de força permaneceu separada de impacto; a prioridade usa P95 da plataforma, força e recência ancorada no dataset. Ações são templates determinísticos e nunca executam publicação ou investimento.
- **Execução:** foram implementados benchmarks com exclusão do creator-alvo, quartis por post, fallback explícito, concentração, patrocínio estratificado, comparação editorial de janelas iguais, deduplicação contextual e fila de até três prioridades.
- **Feedback loop 1:** 15/16 testes passaram. A fixture de recomendação agregada tinha 20 creators; excluir um ainda deixava benchmark individual suficiente e o teste não isolava o agregado. A fixture passou a usar cinco creators compartilhados, preservando a elegibilidade editorial e tornando o alerta individual insuficiente.
- **Feedback loop 2:** testes adicionais fixaram a penalidade de concentração (`0,95` balanceado versus `0,05` concentrado), sinais editoriais positivos/negativos/conflitantes, fallback sem remover controles essenciais e agregado sem outlier.
- **Feedback loop 3:** o ambiente isolado, com a resolução atual de NumPy, expôs avisos de unidade temporal genérica em `pd.Timedelta`. O motor passou a usar `datetime.timedelta` da biblioteca padrão; a fixture também deixou de fazer uma concatenação redundante.
- **Gate:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` terminou com 17/17 testes aprovados em 1,508 s. `py_compile` e `git diff --check` passaram sem saída.
- **Gate isolado final:** 17/17 testes em 1,470 s, com warnings tratados como erro. O caminho completo do CSV canônico passou em 13,17 s, pico residente de 491.651.072 bytes e zero swap.
- **Julgamento:** a janela real recente não gerou comparação patrocinada elegível; o motor expõe insuficiência e cobertura, sem reduzir 30 posts/cinco creators para fabricar recomendação.
- **Limitação:** este marco prova CK-01–07 no motor e a capacidade real. Exportação, CLI, relatório e evidência oficial continuam corretamente reservados para S2/Task 3.

## I15 — S2/Task 3: análise publicada e exportação segura — 2026-09-21 19:44 BRT

- **Planejamento:** gerar relatório e evidência pelo mesmo resultado do motor, sem recalcular analytics no export; usar HTML estático escapado, CSV neutro a fórmulas e escrita atômica. O relatório deveria responder ao briefing antes de qualquer cockpit.
- **Revisão:** S1 ainda não expunha agregados auditáveis por plataforma, conteúdo, categoria, faixa de creator, audiência e mês. O contrato recebeu `dimensions` e um teste de regressão; thresholds e achados não foram alterados para produzir uma narrativa mais atraente.
- **Primeiro gate vermelho:** `test_exports.py` falhou por ausência esperada de `export_evidence` e `executive_summary`. Após a implementação, 20/21 testes passaram; a projeção priorizava `posts=1` sobre `metric_value=10`. O seletor compartilhado foi corrigido.
- **Feedback loop real:** a primeira exportação válida produziu 414.643 linhas e 184.043.808 bytes, inviável para GitHub. A causa era repetir uma linha completa por vínculo fonte×dimensão. Todos os IDs foram preservados, mas agrupados em uma linha `source_ref` por `evidence_id`, com hash em coluna própria; o artefato caiu para centenas de registros e cerca de 6,5 MB.
- **Execução real:** a CLI processou as 52.214 linhas completas, sem alertas post a post no modo de publicação, e gerou `evidence.csv`/HTML por troca atômica. Uma medição intermediária completou em 13,66 s, pico residente de 462.929.920 bytes e zero swap.
- **Recálculo independente:** Pandas direto, sem chamar o motor, confirmou Bilibili em 19,904630989319% de mediana ERv (10.598 posts); YouTube/mixed/beauty/500.000+ em +0,212889341081 p.p. (114 orgânicos/79 patrocinados; 113/78 creators); e o ranking positivo com força mínima 0,70 em YouTube/mixed/beauty/500.000+ seguido por TikTok/image/tech/100.000–499.999.
- **Estratégia humana:** não transformar diferenças globais mínimas em mudança de mix; testar somente células patrocinadas controladas, revisar a célula negativa prioritária e exigir investimento, custo e conversão antes de qualquer decisão de ROI. Frequência e threshold de creators permanecem hipóteses de teste, não leis do dataset.
- **Proveniência:** fonte SHA-256 `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `1.0.0`; comando: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html`.
- **Limites:** o snapshot não contém zeros observados nem dados financeiros; associação patrocinada não é causalidade. A publicação local não autoriza push, PR ou deploy.

## I16 — Revisão P1/S1: endurecimento da fronteira temporal e numérica — 2026-09-21 20:02 BRT

- **Report recebido:** a primeira revisão de P1 atribuiu nota combinada 3,18 e encontrou uma falha alta de CK-01 em S1: `NaT`, offsets incompatíveis e inteiros acima de `int64` podiam atravessar ou derrubar `load_csv`.
- **Planejamento/revisão:** corrigir somente a fronteira de confiança de S1, sem alterar exports/relatório de S2. Política temporal explícita: o arquivo usa datas todas sem offset ou todas com o mesmo offset UTC declarado; nenhuma conversão silenciosa para UTC.
- **Gate vermelho:** duas regressões reproduziram três falhas: `NaT` e `+00:00/-03:00` eram aceitos; `views=2**63` lançava `OverflowError` em vez de retornar diagnóstico.
- **Execução:** `NaT` agora é data inválida; offsets distintos geram `incompatible_timezone_offset`; valores fora de `0..2**63-1` geram `integer_out_of_range`. As séries numéricas validadas alimentam a conversão, evitando um segundo parse divergente.
- **Teste positivo:** duas datas com o mesmo `+02:00` permanecem aceitas como dtype temporal compatível e atravessam `analyze` sem erro.
- **Gate verde:** suíte completa com warnings como erro: 27/27 testes aprovados em 2,332 s. `compileall` e `git diff --check` passaram; não existe lint configurado no repositório.
- **Regressão real:** CSV canônico aprovado com 52.214 linhas e cinco plataformas; validação em 1,270 s e análise em 11,545 s.
- **Resultado:** a importação continua atômica e nenhum dos três valores hostis pode alcançar o motor após um retorno de sucesso.

## I17 — Revisão P1/S1: recência do agregado patrocinado — 2026-09-21 20:07 BRT

- **Novo achado do Feedback Looping:** a evidência de patrocínio não carregava `representative_date`; a fila usava como fallback a mediana de todas as datas da plataforma, inclusive outros estratos.
- **Impacto:** a atualidade e a prioridade podiam ser reduzidas ou elevadas por posts alheios ao braço patrocinado avaliado, contrariando o contrato de recência do agregado.
- **Gate vermelho:** fixture com o estrato patrocinado em 31/01 e todo o restante da plataforma em 01/01 falhou por ausência de `representative_date`.
- **Correção:** cada estrato patrocinado elegível agora registra a mediana de `post_date` dos posts do braço patrocinado. A recomendação exige essa data diretamente; o fallback global por plataforma foi removido da fila agregada.
- **Gate verde:** a regressão confirmou data de evidência/recomendação em 31/01 e recência `1,0`. A suíte completa passou com 28/28 testes em 2,647 s, warnings tratados como erro; `compileall` e `git diff --check` passaram.
- **Regressão real:** CSV canônico aprovado com 52.214 linhas e cinco plataformas; validação em 1,251 s e análise em 11,828 s. A janela-padrão permaneceu sem estrato patrocinado suficiente, como já documentado, sem relaxar o mínimo.
- **Limite:** nenhuma alteração foi feita em `analysis.md`, `evidence.csv` ou no formato de exportação de S2.

## I18 — Revisão P1/S1: universo do P95 e linhas físicas — 2026-09-21 20:23 BRT

- **Gaps do Feedback Looping:** o P95 agregado usava somente comparações elegíveis, embora a SPEC exija todos os grupos não vazios do mesmo tipo/plataforma/janela; diagnósticos de `load_csv` ainda usavam `index+2`, incorreto após células multilinha.
- **Gate vermelho do P95:** um grupo patrocinado grande, sem braço orgânico e portanto inelegível, não alterou o denominador de 3.000 views do grupo elegível.
- **Correção do P95:** os pools de normalização agora são independentes da fila. Editorial usa todos os grupos orgânicos não vazios do núcleo/audiência; patrocínio usa todos os grupos patrocinados não vazios do núcleo. Elegibilidade continua decidindo recomendações, nunca o universo do denominador.
- **Gate vermelho de linhas:** um registro inválido após texto com quebra de linha reportou linha lógica 3, em vez da linha física 4.
- **Correção de linhas:** todos os diagnósticos por registro reutilizam o mapa físico criado pelo `csv.reader`, o mesmo contrato persistido em `source_line`; multiline conta cada linha física.
- **Gates verdes:** a fixture grande aumentou o denominador, reduziu a prioridade e permaneceu fora da fila; o CSV multiline reportou `views` e `post_date` na linha 4. Suíte completa com warnings como erro: 33/33 em 3,565 s; `compileall` e `git diff --check` passaram.
- **CSV real:** 52.214 linhas e cinco plataformas passaram; load em 1,268 s e dois escopos analisados em 26,422 s. A fila recente permaneceu idêntica. A fila histórica manteve os mesmos três IDs e a mesma ordem, mas os scores mudaram de `4,567965e-09 / 3,950288e-11 / 5,079782e-12` para `6,532899e-09 / 5,863452e-11 / 6,169594e-12`.
- **Handoff S2:** como a fila histórica mudou numericamente, `analysis.md`, `evidence.csv` e HTML precisam ser regenerados pelo responsável de S2. Nenhum desses artefatos foi alterado neste fix S1.

## I18 — Revisão P1/S2: contrato único de prioridades — 2026-09-21 20:09 BRT

- **Planejamento:** corrigir os três achados de S2: exportar a fila e seus componentes, gerar o relatório com a ordem do motor corrigido em `81b18fd` e preservar o vínculo compacto entre ID e linha da fonte.
- **Revisão:** `result[recommendations]` será a única fila ordenada; rankings por efeito/força não substituirão a fórmula. O relatório documentará a recência histórica, sem alterar scores para favorecer achados. Não há nova decisão humana sobre patrocínio.
- **Correção de proveniência:** I15 chamou a síntese da IA de “Estratégia humana”; essa atribuição não comprova aprovação humana das células escolhidas. Esta revisão mantém o registro histórico e substitui aquela seleção editorial pela fila determinística do motor.
- **Gate vermelho:** a regressão falhou pela ausência de `analysis_report`; foram acrescentados checks da fila completa, recomposição da prioridade e round-trip de ID opaco/linha física, inclusive campo CSV multilinha.
- **Execução:** a CLI ganhou `--report`; Markdown, HTML e CSV consomem a mesma fila. CSV inclui rank/componentes/valores/P95/ação/janelas; `source_ref` usa arrays JSON paralelos. O mapa passou de índice lógico para linha física inicial do registro.
- **Gate intermediário:** 30/30 testes passaram com warnings como erro em 2,648 s, antes da regeneração dos artefatos reais. O aceite publicado e a repetição real serão verificados a seguir.
- **Gate final:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` passou com 31/31 testes em 2,916 s. `python3 -m compileall -q submissions/luis-roquette/solution/004-social` e `git diff --check` passaram.
- **Regeração real:** `PYTHONWARNINGS=error python3 submissions/luis-roquette/solution/004-social/analysis.py /tmp/social-dataset.tEuI48/social_media_dataset.csv --evidence submissions/luis-roquette/solution/004-social/evidence.csv --summary /tmp/ai-master-004-s2-fixed-summary.html --report submissions/luis-roquette/solution/004-social/analysis.md`. Duas execuções finais concluíram em 14,03 s e 14,81 s, até 544.964.608 bytes residentes, zero swap. CSV, Markdown e HTML foram idênticos byte a byte; HTML ficou em `/tmp`.
- **Prova independente:** leitura via `csv.reader.line_num` reconciliou 571.112 vínculos e todos os 52.214 IDs distintos com as linhas físicas da fonte. O export tem 400 registros: 1 summary, 198 evidence, 198 source_ref, 3 recommendation; 10.404.284 bytes. Recência, impacto e score foram recompostos dos campos exportados, e a ordem dos três IDs foi conferida no Markdown/HTML.
- **Fila corrigida:** Bilibili/mixed/tech/100.000–499.999 (`4,567965181674604e-09`); Instagram/text/tech/500.000+ (`3,950287568451419e-11`); YouTube/video/beauty/50.000–99.999 (`5,07978178671046e-12`). A troca resulta da recência por estrato corrigida em S1; não houve seleção por efeito positivo ou força mínima extra. O primeiro item tem força limitada e exige coleta/teste, não investimento.
- **Identidade dos artefatos:** `evidence.csv` SHA-256 `1a64240eb9c195a000d803edb104dda9b96abaa4577f9f94ebcfe10b3dee132f`; `analysis.md` SHA-256 `7c3bd408aa3a03113b4771e6706b8e756afad5434971c5c781e87ada8bc22500`; HTML SHA-256 `b4ee4c560ca2d9a613b2bf39346182741940df1364bad3866824fa9791ddbcc5`.
- **Tempo/limites:** correção retomada às 20:09 e gates concluídos às 20:15 BRT, cerca de 6 minutos; a leitura anterior à interrupção não foi cronometrada. O CSV cresceu para preservar as linhas físicas. Fluxo do cockpit e impressão A4 visual continuam para P2; este gate não declara a interface pronta. Sem API paga, push, PR ou deploy.
- **Staging:** `git add` foi recusado pela regra que ignora `submissions/`; repetido com `git add -f` somente nos seis arquivos autorizados, sem incluir ferramentas locais ou CSV bruto.
