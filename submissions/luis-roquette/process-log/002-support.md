# Diário de processo — Challenge 002: Redesign de Suporte

## I01 — Briefing absorvido com leitura em loop — 2026-09-21 14:27 BRT

- **Objetivo:** compreender integralmente o Challenge 002 antes de pesquisar dados, escolher ferramentas ou construir a solução.
- **IA/ferramenta:** Codex, GitHub CLI e Git; usados para ler os documentos oficiais, conferir a versão avaliada e reavaliar requisitos por lentes diferentes.
- **Ação ou prompt:** Luis definiu um gate próprio: reler o briefing até obter pelo menos duas passadas consecutivas sem novos achados. Essa decisão criativa é contribuição humana, não sugestão da IA.
- **Resultado:** cinco passadas concluídas; as passadas 4 e 5 não produziram descobertas novas, atingindo o critério de saturação 2/2.
- **Julgamento humano:** aceito por Luis como método permanente para reduzir construção prematura baseada em compreensão parcial.
- **Verificação:** README do desafio com blob Git `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, 5.320 bytes e SHA-256 `8574dbc68bdf81d2cb77bfbf84ddeb98f7d3392b9110d37a17de1bd3954cdf20`.
- **Evidência:** este ledger e os documentos oficiais vinculados abaixo.
- **Limitação:** esta iteração valida a absorção do briefing, não a qualidade, licença ou conteúdo real dos datasets; isso será verificado na etapa de pesquisa.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal do desafio e dos documentos vinculados | três resultados pedidos pelo diretor; diagnóstico, automação e demonstração funcional; dois datasets complementares; process log obrigatório |
| 2 | entregáveis, critérios e métricas | “cruzar” significa combinar evidências, não fabricar união entre linhas; custo é opcional e exige premissas; o protótipo deve ser avaliado fora dos exemplos usados na construção |
| 3 | leitura adversarial e limites | o pedido executivo torna a demonstração funcional necessária; `92%` é exemplo de especificidade, não meta; PII não entra em features ou evidências; economia deve partir de horas observáveis e custo apenas como cenário explícito |
| 4 | conferência contra todos os entregáveis, critérios e regras do PR | nenhum |
| 5 | conferência final do conteúdo e da versão do arquivo | nenhum |

**Resultado:** duas passadas consecutivas sem descoberta nova. Goal de absorção atingido.

### Compreensão consolidada

O desafio exige uma entrega única com três partes conectadas: diagnóstico operacional quantificado no Dataset 1, fronteira explícita entre automação e julgamento humano usando evidências dos dois datasets e um protótipo funcional testado em dados reais não escolhidos para favorecer o resultado.

Os datasets são complementares, mas representam contextos e taxonomias diferentes e não oferecem chave comum. Portanto, não haverá join por linha nem transferência silenciosa de categorias. O Dataset 1 sustenta gargalos, satisfação e desperdício; o Dataset 2 pode sustentar a avaliação de classificação em oito tópicos. A integração válida ocorre no desenho do processo futuro e nas decisões de automação.

“Influenciar satisfação” será tratado como associação observada, não causalidade provada. “Desperdício recuperável” não será igualado automaticamente ao tempo total de resolução. Sem custo operacional fornecido, qualquer valor financeiro será cenário identificado por premissas, enquanto horas permanecem a unidade verificável principal.

O protótipo precisa facilitar o trabalho diário do agente, expor categoria, prioridade, confiança, justificativa e fallback humano quando aplicável. Automatizar 100% é incompatível com o briefing; exemplos dos dados deverão justificar onde a IA para e a pessoa assume.

### Fontes oficiais lidas

- [Challenge 002 — Redesign de Suporte](https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/process-002-support)
- [README geral](https://github.com/luisroquette/ai-master-challenge)
- [Guia de submissão](https://github.com/luisroquette/ai-master-challenge/blob/main/submission-guide.md)
- [Regras do Pull Request](https://github.com/luisroquette/ai-master-challenge/blob/main/CONTRIBUTING.md)

## I02 — Adoção de Spec-Driven Development — 2026-09-21 14:32 BRT

- **Objetivo:** conduzir a solução do Challenge 002 por uma especificação verificável antes de implementar análise, automação ou interface.
- **IA/ferramenta:** plugin SDD `3.6.0` do Context Engineering Kit para Claude Code, com os componentes `add-task`, `plan-task`, `implement-task`, `brainstorm` e `create-ideas`.
- **Ação ou prompt:** Luis decidiu usar Spec-Driven Development como metodologia do desafio e indicou o recurso `https://claudecowork.im/resources/sdd` e o repositório `NeoLabHQ/context-engineering-kit`.
- **Resultado:** marketplace `context-engineering-kit` adicionado; plugin `sdd@context-engineering-kit` instalado no escopo do usuário, habilitado e conferido pelo inventário do Claude Code.
- **Julgamento humano:** a escolha metodológica é de Luis. O fluxo adotado será: preservar a intenção em uma tarefa, refinar a especificação e seus critérios, revisar a especificação humana e só então implementar e verificar por fases.
- **Verificação:** `claude plugin details sdd@context-engineering-kit` retornou versão `3.6.0`, cinco skills, oito agentes e status habilitado em `claude plugin list`.
- **Evidência:** [repositório oficial](https://github.com/NeoLabHQ/context-engineering-kit), [documentação SDD](https://neolab.gitbook.io/cek/plugins/sdd) e saída terminal registrada nesta sessão.
- **Limitação:** o comando publicado pelo diretório externo, `npx skills add ... --skill sdd`, não encontrou a skill porque o repositório atual distribui SDD como plugin. A instalação foi corrigida pelo fluxo oficial de marketplace do Claude Code. A nova sessão do Claude Code deve ser reiniciada para carregar o plugin.

### Regra de convivência com o briefing

SDD organiza o trabalho, mas não substitui os gates já definidos. A pesquisa comparativa e a reprodução mínima de candidatos continuam antes de qualquer implementação. A especificação deve manter os dois datasets separados no nível de linha, explicitar premissas de custo, proteger PII, reservar fallback humano e exigir validação fora dos exemplos de construção.

## I03 — Correção: SDD executado no Codex — 2026-09-21 14:36 BRT

- **Objetivo:** garantir que a metodologia SDD seja executada neste agente Codex, sem depender de uma sessão do Claude Code.
- **IA/ferramenta:** skills nativas do Codex em `~/.codex/skills`: `add-task`, `plan-task`, `implement-task`, `brainstorm` e `create-ideas`.
- **Ação ou prompt:** Luis corrigiu explicitamente a interpretação anterior: “é para usar aqui, no CODEX!”.
- **Resultado:** os cinco componentes foram detectados no catálogo ativo do Codex e seus arquivos `SKILL.md` foram verificados localmente. O Challenge 002 usará esses componentes nesta sessão e nas próximas etapas.
- **Julgamento humano:** a execução no Claude Code foi uma interpretação incorreta da IA causada pelo argumento `--agent claude-code` do comando publicado. Luis definiu o Codex como executor correto.
- **Verificação:** `npx skills list -g --agent codex --json` reconheceu os cinco componentes com agente `Codex`; os arquivos existem em `/Users/luisroquette/.codex/skills/`.
- **Evidência:** catálogo ativo desta sessão e hashes locais dos cinco `SKILL.md`.
- **Limitação:** a cópia instalada no Claude Code não será usada neste desafio; sua presença não altera arquivos ou execução do worktree.

## I04 — Documentar é parte central da entrega — 2026-09-21 14:39 BRT

- **Objetivo:** tratar o diário como parte da qualidade da submissão, com importância igual ou superior à entrega final.
- **Ação ou prompt:** Luis definiu: registrar continuamente o processo em fragmentos curtos, objetivos e diretos, destacando especialmente os pontos que ele indicar na conversa. Corrigir o português antes de incorporar qualquer texto ao diário.
- **Resultado:** cada marco relevante passará a deixar evidência contemporânea de decisão, hipótese, erro, correção, validação e contribuição humana, sem reconstrução retroativa.
- **Julgamento humano:** “Ganha quem documenta.” Como referência criativa, Luis citou Silvio Santos: “Você sabe por que o ovo de galinha vende mais do que o de pata? Porque a galinha canta quando bota.”
- **Verificação:** regra registrada neste diário antes da próxima etapa do SDD.
- **Limitação:** concisão não pode apagar evidência necessária; o diário não incluirá raciocínio interno oculto, segredos, credenciais ou dados pessoais.

## I05 — Descoberta socrática antes da SPEC — 2026-09-21 14:41 BRT

- **Objetivo:** discutir exaustivamente o projeto e arquitetar a solução sobre decisões explícitas antes de criar ou revisar qualquer especificação.
- **IA/ferramenta:** skill `brainstorm` da metodologia SDD no Codex, aplicada como método socrático de ondas adaptativas.
- **Ação ou prompt:** Luis identificou corretamente que ainda não existe SPEC e que o projeto sequer foi discutido. Ele definiu um mínimo de cinco ondas de perguntas; cada onda posterior deve depender das respostas anteriores e aprofundar lacunas, conflitos e escolhas descobertas.
- **Resultado esperado:** uma direção validada para problema, usuário, fluxo operacional, evidência, fronteira humano/IA, arquitetura, riscos e critérios de sucesso. Esses temas orientam as ondas, mas não formam um questionário rígido: as respostas determinam a próxima pergunta.
- **Julgamento humano:** o método de ondas adaptativas é uma decisão criativa de Luis. O Codex fará uma pergunta por vez, registrará os destaques de cada resposta e não antecipará a solução.
- **Verificação:** após pelo menos cinco ondas, o desenho será apresentado em seções curtas para validação incremental. Somente depois a skill `add-task` criará a SPEC inicial; `plan-task` fará o refinamento e `implement-task` só poderá começar com a especificação aprovada.
- **Evidência:** respostas desta conversa, síntese validada e futura SPEC vinculada neste diário.
- **Limitação:** cinco ondas são o piso, não o teto. Novas ondas serão abertas enquanto houver decisão material, contradição ou hipótese sem resposta.
- **Formato corrigido por Luis:** todas as ondas usarão perguntas de múltipla escolha, uma por vez. As alternativas posteriores serão adaptadas às respostas anteriores; Luis poderá complementar a opção escolhida com contexto livre.

### Sequência SDD acordada

`brainstorm socrático → síntese validada → add-task → plan-task → revisão humana da SPEC → implement-task`

## I06 — Ledger de perguntas e respostas — 2026-09-21 14:50 BRT

- **Objetivo:** preservar as decisões tomadas durante toda a descoberta socrática, não apenas a síntese final.
- **Regra definida por Luis:** registrar no diário cada pergunta, suas alternativas, a resposta escolhida e a interpretação usada para adaptar a onda seguinte. Corrigir o português sem alterar o sentido da resposta.
- **Formato:** entradas curtas, cronológicas e contemporâneas à conversa.

### Onda 1 — Foco principal do protótipo

**Pergunta:** qual deve ser o foco principal do protótipo?

- **A — Triagem inteligente:** categoria, prioridade, confiança, roteamento e fallback humano.
- **B — Controle de gargalos:** painel com atrasos, desperdício recuperável e ações por impacto.
- **C — Resposta assistida:** sugestões baseadas em tickets semelhantes, com revisão humana.

**Resposta de Luis:** A + B + C.

**Interpretação para a próxima onda:** a solução precisa integrar diagnóstico, decisão operacional e assistência ao agente. A próxima escolha deve definir como esses três resultados formam um único produto demonstrável, sem virar três protótipos desconectados.

### Onda 2 — Forma do produto integrado

**Pergunta:** como triagem inteligente, controle de gargalos e resposta assistida devem formar um único produto?

- **A — Pipeline integrado:** ticket entra, a IA classifica e prioriza, sugere uma resposta, o humano aprova ou assume e o resultado alimenta o painel.
- **B — Três módulos independentes:** triagem, respostas e dashboard funcionam separadamente sobre os mesmos dados.
- **C — Central de comando:** o dashboard é a interface principal; triagem e respostas aparecem como ações dentro dele.

**Resposta de Luis:** A — Pipeline integrado.

**Interpretação para a próxima onda:** o protótipo será uma fatia vertical demonstrável do processo, não uma coleção de telas. A próxima decisão precisa definir os pontos exatos de autonomia da IA e intervenção humana dentro desse pipeline.

### Onda 3 — Fronteira entre IA e humano

**Pergunta:** qual autonomia a IA deve ter no pipeline?

- **A — Copiloto conservador:** a IA recomenda tudo; o humano confirma categoria, prioridade, rota e resposta.
- **B — Autonomia por risco:** a IA roteia automaticamente casos seguros e confiáveis; respostas externas continuam como rascunho; baixa confiança ou tema sensível vai para o humano.
- **C — Automação de casos simples:** a IA também envia respostas automaticamente em FAQs de alta confiança; exceções seguem para o humano.

**Resposta de Luis:** B — Autonomia por risco.

**Interpretação para a próxima onda:** a arquitetura precisa separar decisões internas reversíveis de comunicação externa. Roteamento pode ocorrer automaticamente sob critérios verificáveis; respostas não serão enviadas sem revisão humana. A próxima escolha deve definir como risco e confiança serão combinados no gate.

### Onda 4 — Gate de automação

**Pergunta:** como o gate decide se a IA pode rotear automaticamente?

- **A — Confiança + regras de risco:** exige confiança calibrada e bloqueia temas sensíveis, prioridade crítica, PII ou ambiguidade.
- **B — Apenas confiança do modelo:** automatiza acima de um limite estatístico; abaixo dele, envia ao humano.
- **C — Apenas regras operacionais:** usa palavras-chave, categoria e prioridade; a confiança do modelo serve somente como informação.

**Resposta de Luis:** A — Confiança + regras de risco.

**Interpretação para a próxima onda:** o gate será híbrido e auditável. Um score alto não poderá superar bloqueios explícitos de segurança; a confiança deverá ser calibrada e o motivo da decisão ficará visível. A próxima escolha deve definir como provar, com métricas, que esse equilíbrio produz valor sem esconder risco.

### Onda 5 — Evidência prioritária

**Pergunta:** o que a demonstração precisa provar prioritariamente?

- **A — Segurança:** nenhum caso sensível ou crítico é roteado automaticamente de forma indevida; cobertura vem depois.
- **B — Eficiência:** redução mensurável de trabalho manual e horas recuperáveis; risco aparece como limite.
- **C — Evidência equilibrada:** qualidade e calibração do classificador, cobertura segura da automação e economia operacional rastreável.

**Resposta de Luis:** C — Evidência equilibrada.

**Interpretação para a próxima onda:** a validação não poderá ser resumida a acurácia. Ela deverá conectar desempenho preditivo, confiabilidade das probabilidades, proporção de tickets elegíveis à automação segura e impacto operacional calculado com premissas visíveis. O mínimo de cinco ondas foi cumprido, mas a descoberta continua porque ainda existem decisões materiais de usuário, interface, dados e arquitetura.

### Onda 6 — Usuário principal

**Pergunta:** para quem a experiência principal deve ser desenhada?

- **A — Agente de suporte:** workspace diário com ticket, classificação, risco, resposta sugerida e decisão humana; painel gerencial compacto.
- **B — Gestor de operações:** central de gargalos, métricas e economia; ticket individual como demonstração secundária.
- **C — Duas experiências equivalentes:** cockpit completo do agente e painel completo do gestor, conectados pelo mesmo pipeline.

**Resposta de Luis:** A — Agente de suporte.

**Interpretação para a próxima onda:** a unidade central da interface será o ticket em trabalho. Métricas gerenciais devem nascer das decisões registradas nesse fluxo, sem criar um segundo produto do mesmo tamanho. A próxima escolha deve definir como o agente entra e percorre esse workspace na demonstração.

### Onda 7 — Entrada no workspace

**Pergunta:** como o agente começa o trabalho?

- **A — Fila diária priorizada:** tickets reais de validação ordenados por risco e urgência; o agente abre, revisa e decide.
- **B — Ticket individual:** o agente cola um texto e recebe categoria, prioridade, confiança, rota e resposta sugerida.
- **C — Fila + entrada manual:** combina operação diária com uma caixa para testar novos tickets.

**Resposta de Luis:** A — Fila diária priorizada.

**Interpretação para a próxima onda:** o protótipo deve provar utilidade em uma sequência de trabalho, não apenas em uma inferência isolada. A fila usará dados separados da construção e permitirá rastrear decisão e resultado por ticket. A próxima escolha deve definir o princípio de ordenação da atenção humana.

### Onda 8 — Ordenação da fila humana

**Pergunta:** o que coloca um ticket no topo da fila humana?

- **A — Risco:** temas sensíveis, prioridade crítica e baixa confiança aparecem primeiro.
- **B — Urgência operacional:** maior risco de atraso e descumprimento do atendimento aparece primeiro.
- **C — Prioridade composta e explicável:** combina risco, urgência e incerteza usando somente campos validados nos dados; mostra os motivos do ranking.

**Resposta de Luis:** C — Prioridade composta e explicável.

**Interpretação para a próxima onda:** o ranking não será uma caixa-preta nem dependerá de campos presumidos. Cada ticket exibirá os fatores que elevaram sua posição; a fórmula final dependerá da auditoria dos datasets. A próxima escolha deve definir a origem e o nível de automação da resposta sugerida.

### Onda 9 — Origem da resposta sugerida

**Pergunta:** como a resposta sugerida deve ser produzida?

- **A — Recuperação de casos similares:** busca resoluções históricas semelhantes, mostra as fontes e produz um rascunho editável; só entra se a qualidade dos textos for validada.
- **B — Templates por categoria:** usa respostas padronizadas e regras, sem geração livre.
- **C — Modelo generativo local:** cria resposta fundamentada em casos similares, sem API paga, com maior complexidade e risco de alucinação.

**Resposta de Luis:** A — Recuperação de casos similares.

**Interpretação para a próxima onda:** a resposta assistida será fundamentada e rastreável, não geração livre. A auditoria do campo `Resolution` decidirá se ele é utilizável; baixa similaridade ou histórico inadequado exigirá fallback humano. A próxima escolha deve definir quais decisões e correções humanas retornam ao sistema.

### Onda 10 — Feedback humano

**Pergunta:** o que o sistema deve aprender com a decisão humana?

- **A — Feedback auditável:** registra aprovação, edição ou rejeição, motivo e diferença entre sugestão e resposta final; usa isso somente em avaliações e versões futuras.
- **B — Feedback mínimo:** registra apenas aprovação ou rejeição para métricas.
- **C — Aprendizado automático imediato:** cada decisão altera o comportamento do sistema em produção.

**Resposta de Luis:** A — Feedback auditável.

**Interpretação para a próxima onda:** o protótipo preservará a trilha entre recomendação, intervenção humana e resultado, mas não fará aprendizado online. Isso evita mudanças não validadas e cria dados para melhoria posterior. A próxima escolha deve impedir que o painel confunda métricas históricas observadas com resultados simulados ou projetados do protótipo.

### Onda 11 — Separação das evidências

**Pergunta:** como o painel deve apresentar evidências?

- **A — Duas camadas separadas:** diagnóstico histórico observado e avaliação ou projeção do protótipo aparecem em blocos distintos, com premissas visíveis.
- **B — Somente histórico:** mostra gargalos e satisfação do Dataset 1; métricas do protótipo ficam fora do painel.
- **C — Visão unificada:** mistura histórico, simulação e projeções em uma única sequência operacional.

**Resposta de Luis:** A — Duas camadas separadas.

**Interpretação para a próxima onda:** o painel diferenciará fatos, resultados de teste e cenários. Nenhuma projeção de horas ou custo poderá parecer observação real. A próxima escolha deve definir o formato executável da entrega sem antecipar o framework antes da pesquisa técnica.

### Onda 12 — Formato executável

**Pergunta:** qual deve ser o formato executável da entrega?

- **A — Aplicação web local e autocontida:** roda com um comando, sem API paga; o framework será decidido após pesquisa e reprodução de candidatos.
- **B — Notebook interativo:** combina análise, modelo e demonstração no mesmo arquivo.
- **C — Aplicação hospedada:** acesso por URL pública, com infraestrutura e deploy incluídos no escopo.

**Resposta de Luis:** A — Aplicação web local e autocontida.

**Interpretação para a próxima onda:** a solução deve ser reproduzível sem credenciais, serviços externos ou custo variável. A pesquisa escolherá a menor tecnologia capaz de entregar a experiência. A próxima decisão deve definir a filosofia de seleção do classificador sem fixar prematuramente um algoritmo.

### Onda 13 — Seleção do classificador

**Pergunta:** como o classificador deve ser escolhido?

- **A — Baseline primeiro:** comparar regras simples e modelo textual leve; só adotar embeddings ou modelo maior se houver ganho mensurável.
- **B — Semântico primeiro:** começar com embeddings para capturar significado além de palavras-chave.
- **C — Zero-shot primeiro:** usar um modelo pronto sem treinamento específico e medir sua aderência às oito categorias.

**Resposta de Luis:** A — Baseline primeiro.

**Interpretação para a próxima onda:** o algoritmo não será escolhido por novidade. A pesquisa reproduzirá candidatos e o baseline mais simples permanecerá se alternativas mais complexas não melhorarem métricas relevantes. A próxima decisão deve explicitar qual erro operacional é mais caro, orientando calibração e abstinência.

### Onda 14 — Custo assimétrico do erro

**Pergunta:** qual erro operacional é mais caro?

- **A — Automação indevida:** é pior rotear automaticamente um caso errado ou sensível; o sistema prefere encaminhar dúvidas ao humano.
- **B — Excesso de fallback:** é pior mandar tickets seguros demais ao humano; o sistema aceita mais risco para ampliar cobertura.
- **C — Custos equivalentes:** falsos roteamentos e fallbacks humanos recebem o mesmo peso.

**Resposta de Luis:** A — Automação indevida.

**Interpretação para a próxima onda:** os thresholds serão conservadores e avaliados por risco seletivo, não apenas por cobertura. Abstinência é comportamento correto quando a confiança ou as regras não sustentam automação. A próxima escolha deve definir como transformar cobertura segura em horas e custo sem fabricar ROI.

### Onda 15 — Estimativa de economia

**Pergunta:** como estimar economia sem fabricar ROI?

- **A — Calculadora de cenários:** mostra horas observáveis e permite ajustar tempo por tarefa e custo por hora; separa cenários conservador, base e otimista.
- **B — Somente horas:** quantifica tempo recuperável, sem converter para dinheiro.
- **C — Um valor executivo:** apresenta uma única estimativa mensal de economia baseada em premissas fixas.

**Resposta de Luis:** A — Calculadora de cenários.

**Interpretação para a próxima onda:** horas derivadas dos dados permanecerão separadas de parâmetros fornecidos pelo usuário. Valores financeiros serão cenários, nunca fatos observados. A próxima escolha deve definir se as decisões humanas e sua trilha de auditoria sobrevivem ao encerramento da aplicação local.

### Onda 16 — Persistência do feedback

**Pergunta:** como preservar o feedback humano?

- **A — Persistência local auditável:** salva decisões, edições e motivos em armazenamento local simples; permite exportar o histórico.
- **B — Somente durante a sessão:** mantém o feedback em memória e permite baixar um arquivo antes de fechar.
- **C — Banco externo:** persiste tudo em serviço remoto, exigindo configuração e credenciais.

**Resposta de Luis:** A — Persistência local auditável.

**Interpretação para a próxima onda:** a trilha de auditoria será persistida localmente com tecnologia nativa ou já instalada, escolhida após a pesquisa. Nenhuma credencial ou infraestrutura remota será necessária. PII deverá ser removida antes da persistência. A próxima escolha deve limitar o painel gerencial ao conjunto mínimo de decisões úteis.

### Onda 17 — Primeira visão gerencial

**Pergunta:** o que o gestor deve ver primeiro?

- **A — Scorecard decisório:** gargalo principal, fatores associados à satisfação, cobertura segura da automação e horas ou economia por cenário.
- **B — Explorador analítico:** muitos filtros, cruzamentos e gráficos para investigação livre.
- **C — Narrativa executiva:** conclusões e recomendações em texto, com poucos indicadores.

**Resposta de Luis:** A — Scorecard decisório.

**Interpretação para a próxima onda:** a camada gerencial responderá quatro decisões e oferecerá evidência detalhada sob demanda, sem virar um BI genérico. A próxima escolha deve tornar explícito o limite do MVP e impedir integrações especulativas de consumirem o tempo da demonstração principal.

### Onda 18 — Limite do MVP

**Pergunta:** qual deve ser o limite do MVP?

- **A — Demonstração local completa:** pipeline funcional com dados reais, sem integração com helpdesk, envio real de mensagens, autenticação, multiempresa ou aprendizado online.
- **B — Integração real:** conectar o protótipo a um helpdesk ou canal de atendimento.
- **C — Plataforma extensível:** incluir API, autenticação e estrutura para múltiplas empresas desde o início.

**Pedido de Luis:** o Codex deve decidir após revisar novamente o repositório oficial, sem transferir essa avaliação ao usuário.

**Decisão do Codex:** A — Demonstração local completa.

**Confirmação de Luis:** decisão aceita; seguir com esse limite de MVP.

**Verificação:** reavaliação do fork em `main` no commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; README do Challenge 002 no blob `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, além do README geral, guia de submissão e regras do PR.

**Fundamento:** o desafio pede diagnóstico, proposta de automação e algo funcional rodando com dados reais; fornece orçamento de 4–6 horas e aceita código ou aplicação com instruções de setup. Não exige integração com helpdesk, envio real, autenticação, multiempresa, API pública ou deploy. Construir B ou C consumiria o prazo em infraestrutura não avaliada e reduziria a profundidade das evidências obrigatórias.

**Interpretação para a próxima onda:** o MVP termina em uma aplicação local reproduzível que demonstra o pipeline ponta a ponta, persiste decisões localmente e exporta evidências. Integrações externas serão descritas apenas como evolução, não implementadas.

### Onda 19 — Validação do classificador

**Pergunta:** como validar o classificador sem favorecer o resultado?

- **A — Teste congelado + validação cruzada:** separa uma amostra estratificada intocável; usa validação cruzada no restante; mede por classe, calibração e cobertura segura.
- **B — Um único holdout:** separa treino e teste uma vez e reporta o resultado.
- **C — Amostra demonstrativa:** avalia manualmente um conjunto pequeno de tickets representativos.

**Resposta de Luis:** A — Teste congelado + validação cruzada.

**Interpretação para a próxima onda:** seleção de algoritmo e threshold ocorrerá sem consultar o teste final. O resultado reportará métricas globais e por classe, confiabilidade das probabilidades e trade-off entre cobertura e erro seletivo. A próxima escolha deve definir uma avaliação igualmente séria para a recuperação de respostas.

### Onda 20 — Validação das respostas recuperadas

**Pergunta:** como validar as respostas recuperadas?

- **A — Rubrica humana em tickets não vistos:** avalia relevância, correção, segurança e necessidade de edição; registra concordância e falhas reais.
- **B — Similaridade automática:** considera o score de similaridade como medida principal de qualidade.
- **C — Casos ilustrativos:** apresenta exemplos bons e ruins sem avaliação estruturada.

**Resposta de Luis:** A — Rubrica humana em tickets não vistos.

**Interpretação para a próxima onda:** similaridade será apenas um sinal de recuperação, não prova de resposta adequada. A avaliação preservará exemplos de falha e esforço de edição. A próxima escolha deve definir o comportamento seguro quando nenhum caso histórico satisfizer a rubrica ou o threshold mínimo.
