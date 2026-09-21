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

### Onda 21 — Fallback da resposta assistida

**Pergunta:** o que acontece quando não há resolução histórica segura?

- **A — Sem sugestão + escalonamento:** explica a insuficiência de evidência e entrega o ticket ao humano.
- **B — Template neutro:** oferece uma resposta genérica de recebimento, claramente identificada como template.
- **C — Geração local:** produz um rascunho mesmo sem precedente suficientemente similar.

**Resposta de Luis:** A — Sem sugestão + escalonamento.

**Interpretação para a próxima onda:** abstinência também vale para respostas. O produto deve mostrar ausência de evidência em vez de preencher o espaço com texto plausível. A próxima escolha precisa reconciliar os dois datasets dentro da mesma arquitetura sem inventar join, taxonomia comum ou transferência de domínio.

### Onda 22 — Convivência dos dois datasets

**Pergunta:** como usar os dois datasets sem inventar conexão?

- **A — Motor comum, modelos separados:** mesma interface e mesmos gates; Dataset 1 sustenta operação e respostas, Dataset 2 sustenta classificação IT em sua própria taxonomia.
- **B — Transferência explícita:** treina no Dataset 2 e aplica ao Dataset 1 como experimento de mudança de domínio, exibindo a perda de qualidade.
- **C — Taxonomia unificada:** combina categorias dos dois datasets em um único modelo criado manualmente.

**Resposta de Luis:** A — Motor comum, modelos separados.

**Interpretação para a próxima onda:** componentes de classificação, calibração, abstinência e auditoria serão reutilizados, mas cada domínio manterá seus próprios dados, rótulos, métricas e limitações. A próxima escolha deve definir como essa separação aparece na navegação sem transformar o produto em duas aplicações.

### Onda 23 — Navegação entre domínios

**Pergunta:** como mostrar os dois domínios na aplicação?

- **A — Operação principal + laboratório IT:** Dataset 1 alimenta o workspace diário; Dataset 2 aparece em uma área de validação do classificador.
- **B — Seletor de domínio:** o agente alterna entre Customer Support e IT, com filas equivalentes.
- **C — Operação única:** a aplicação mostra apenas Dataset 1; os resultados do Dataset 2 aparecem somente no relatório técnico.

**Resposta de Luis:** A — Operação principal + laboratório IT.

**Interpretação para a próxima onda:** o workspace do agente permanece coeso e orientado ao Dataset 1. O laboratório IT prova a capacidade de classificação no segundo dataset sem simular continuidade operacional inexistente. A próxima onda confrontará seis arquiteturas completas antes da síntese incremental do desenho.

### Onda 24 — Arquitetura completa

**Pergunta:** qual das seis arquiteturas deve seguir para a síntese?

- **A — Support Decision Copilot:** fila do agente, gate de risco, resposta recuperada, feedback auditável, scorecard e laboratório IT.
- **B — Plataforma modular por domínio:** Customer Support e IT como módulos equivalentes sobre um motor compartilhado.
- **C — Control Tower operacional:** diagnóstico e ROI como núcleo; atendimento individual como função secundária.
- **D — Analytics + classificador separado:** dashboard e ferramenta de classificação sem fluxo integrado.
- **E — Agente autônomo generativo:** automatiza respostas e roteamento com mínima intervenção humana.
- **F — Plataforma enterprise integrada:** helpdesk, autenticação, APIs e multiempresa no MVP.

**Pedido de Luis:** o Codex deve confrontar as opções com o desafio oficial e decidir com segurança, sem devolver a escolha ao usuário.

**Decisão do Codex:** A — Support Decision Copilot.

**Verificação:** reconsulta do Challenge 002 no blob `6c873eb7dd1955ebccfb730bcd98143373cbaab2`, no commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575` da `main`.

**Fundamento:** A é a única arquitetura que cobre simultaneamente o diagnóstico obrigatório, a proposta realista de automação, a demonstração funcional, os dois datasets, o trabalho diário do agente, a fronteira humano/IA e a estimativa de horas ou ROI. B dilui o caso de uso principal; C rebaixa o protótipo operacional; D fragmenta a proposta; E viola o alerta contra automação total; F excede o orçamento de 4–6 horas com infraestrutura não solicitada.

**Resultado:** arquitetura escolhida para a síntese incremental do desenho e futura SPEC.

## I07 — Síntese incremental da arquitetura — 2026-09-21 16:39 BRT

- **Objetivo:** validar o desenho do Support Decision Copilot em seções curtas antes de criar a SPEC.
- **Método:** apresentar uma seção de 200–300 palavras por vez, oferecer validação de múltipla escolha e registrar aprovação ou correção antes de avançar.
- **Estado inicial:** nenhuma SPEC criada; arquitetura A selecionada após 24 ondas socráticas.

### Seção 1 — Arquitetura e fluxo principal — proposta

O Support Decision Copilot será uma aplicação web local e autocontida com duas áreas claramente separadas: **Operação de Suporte** e **Laboratório IT**. A área principal usa o Dataset 1. Uma preparação offline remove PII, audita qualidade e produz métricas observadas. A fila diária recebe somente tickets reservados para validação, evitando demonstrar o sistema nos mesmos exemplos usados na construção.

Cada ticket percorre um pipeline único: classificação e prioridade sugeridas, confiança calibrada, regras explícitas de risco, decisão de roteamento e resposta assistida. A ordenação combina apenas sinais validados nos dados e mostra por que cada item subiu na fila. O roteamento automático exige simultaneamente confiança suficiente e ausência de bloqueios; caso sensível, crítico, ambíguo ou incerto vai para revisão humana.

A resposta assistida recupera resoluções semelhantes somente do conjunto permitido para referência, exibe os casos usados e entrega um rascunho editável. Sem similaridade segura, o sistema se abstém. O agente aprova, edita, rejeita ou escalona; a decisão, o motivo e a diferença entre sugestão e resposta final entram em uma trilha local auditável e exportável.

O scorecard gerencial deriva desse fluxo, mas separa três naturezas de evidência: histórico observado, desempenho medido do protótipo e cenários de horas ou custo. O Laboratório IT usa o Dataset 2, sua taxonomia de oito categorias e seu próprio modelo. Ele reutiliza classificação, calibração e abstinência, mas nunca mistura registros ou rótulos com o Dataset 1. Framework, algoritmo e armazenamento serão escolhidos somente após pesquisa e reprodução técnica.

**Pergunta de validação:** esta arquitetura e este fluxo principal estão corretos para avançar?

**Validação de Luis:** A — Seção 1 aprovada sem ajustes.

### Seção 2 — Componentes e fronteiras dos dados — proposta

A solução terá componentes pequenos, com arquivos de entrada e saída explícitos. O **preparador de dados** valida schemas, mede ausências e duplicidades, remove PII, normaliza tempos e cria manifests reproduzíveis de treino, validação e teste. Cada dataset terá seu próprio adaptador; nenhuma função aceitará registros dos dois domínios como se compartilhassem a mesma taxonomia. Dados brutos não serão publicados. Scripts e instruções permitirão baixá-los das fontes oficiais e regenerar artefatos derivados seguros.

O **motor analítico** processa o Dataset 1 e gera tabelas rastreáveis para gargalos, satisfação e desperdício recuperável. Ele salva resultados estruturados consumidos pelo scorecard, evitando recalcular regras de negócio na interface. Associações serão identificadas como associações; horas observadas, premissas ajustáveis e valores financeiros permanecerão em campos diferentes.

O **motor de decisão** expõe a mesma interface para modelos separados de Customer Support e IT: classe, probabilidades calibradas, confiança, versão do artefato e explicação. Um **gate de risco determinístico** recebe essa saída e regras auditáveis, retornando `auto_route` ou `human_review` com códigos de motivo. Thresholds vêm da validação, nunca de ajuste visual na demonstração.

O **recuperador de respostas** indexa apenas descrições e resoluções sanitizadas do conjunto permitido. Ele devolve casos similares, scores e identificadores de origem; abaixo do limite, devolve abstinência. A **aplicação web** apenas orquestra esses componentes, exibe artefatos e registra decisões humanas em persistência local simples. A interface não treina modelos nem altera thresholds. Um comando reproduz análise e modelos; outro inicia a aplicação. Frameworks, bibliotecas e formato de persistência continuam abertos até a pesquisa técnica provar a opção mínima adequada.

**Pergunta de validação:** estes componentes e limites de dados estão corretos para avançar?

**Validação de Luis:** A — Seção 2 aprovada sem ajustes.

### Seção 3 — Segurança, abstinência e falhas — proposta

O sistema adotará **falha segura** como padrão. Schema incompatível, coluna obrigatória ausente, artefato corrompido ou versão divergente interrompe apenas a função afetada e informa arquivo, causa e correção. Conversões inválidas de datas, tempos ou notas não serão silenciosamente transformadas em zero: ficarão isoladas, quantificadas e visíveis no relatório de qualidade. A aplicação nunca iniciará roteamento com modelo ou calibração ausentes.

Qualquer erro no classificador, no cálculo de confiança ou no gate produz `human_review`. Regras de risco têm precedência sobre probabilidade. Temas sensíveis serão definidos a partir da inspeção dos dados e de uma política documentada; nenhum rótulo será inventado antes dessa análise. PII será removida na preparação e mascarada novamente na apresentação como defesa adicional. Dados exportados não incluirão nome ou email do cliente.

O recuperador só sugere resposta quando o histórico sanitizado, a similaridade e a rubrica mínima sustentarem o uso. Índice indisponível, resolução vazia, fonte inadequada ou score insuficiente resultam em abstinência explicada. O sistema não preenche esse vazio com geração livre. O agente sempre pode rejeitar, editar ou escalonar, e nenhuma resposta é enviada externamente.

A persistência local deverá gravar cada decisão de modo atômico e manter o registro anterior se ocorrer falha. A interface distinguirá estado carregando, função indisponível e artefato desatualizado. Cada exportação carregará versão dos dados, modelo, threshold e regras usadas. Não haverá credenciais ou chamadas externas. Se o Dataset 1 ou o Dataset 2 não sustentar uma função planejada, a função será removida ou rebaixada a hipótese, e a limitação será registrada em vez de ser simulada.

**Pergunta de validação:** esta política de segurança e falhas está correta para avançar?

**Validação de Luis:** A — Seção 3 aprovada sem ajustes.

### Seção 4 — Validação, testes e evidências — proposta

A validação começará antes dos modelos. Checks de dados confirmarão schema, tipos, unicidade, ausências, duplicidades, faixas, cardinalidades e remoção de PII. Cada exclusão ou coerção terá contagem. O diagnóstico operacional terá testes de denominador e reconciliação: totais por canal, prioridade e tipo precisam retornar ao universo correto; comparações de satisfação e tempo deverão informar amostra, dispersão e dados ausentes, não apenas médias.

Cada classificador será comparado com baselines simples. A seleção usará validação cruzada somente no conjunto de desenvolvimento. O teste estratificado permanecerá congelado até modelo, calibração, regras e thresholds estarem definidos. A avaliação reportará macro-F1, precisão e recall por classe, matriz de confusão, qualidade da calibração e curva de risco versus cobertura. O gate terá testes diretos de fronteira: regra sensível vence confiança alta; confiança insuficiente gera revisão; entrada inválida nunca autoriza automação.

A recuperação de respostas será avaliada em tickets não vistos, sem resoluções do teste dentro do índice. Uma rubrica humana medirá relevância, correção, segurança e esforço de edição. Casos sem precedente adequado testarão explicitamente a abstinência. Exemplos bons e ruins serão preservados como evidência, sem substituir as métricas agregadas.

O fluxo ponta a ponta validará fila, explicação, decisão humana, persistência, exportação e scorecard usando uma amostra definida antes de observar resultados. Os artefatos incluirão relatório de qualidade, tabelas analíticas, métricas versionadas, decisões do gate, avaliação da recuperação, log exportado e screenshot real da aplicação. Comandos documentados regenerarão tudo. Uma lógica não trivial só será considerada pronta com teste reproduzível; qualquer falha conhecida bloqueia a alegação correspondente.

**Pergunta de validação:** esta estratégia de testes e evidências está correta para avançar?

**Validação de Luis:** A — Seção 4 aprovada sem ajustes.

### Seção 5 — Experiência e hierarquia da interface — proposta

A aplicação abrirá na **Fila de hoje**, não em um dashboard abstrato. Cada linha mostrará posição, prioridade composta, categoria sugerida, confiança, estado do gate e até três motivos objetivos. A ordenação será compreensível sem depender de cor; rótulos, ícones e texto manterão acessibilidade. PII permanecerá mascarada em lista, detalhe, screenshots e exportações.

Ao abrir um ticket, o agente verá três zonas. O contexto sanitizado fica em primeiro plano. Ao lado, o painel de decisão apresenta classificação, prioridade, probabilidades calibradas, regras acionadas e veredito `auto_route` ou `human_review`. A área de resposta mostra casos similares com identificadores rastreáveis, score e resolução histórica, seguida do rascunho editável. Sem evidência suficiente, ela mostra abstinência e motivo, nunca uma caixa vazia que sugira erro.

As ações serão poucas: **aprovar**, **editar e aprovar**, **rejeitar** ou **escalonar**. Rejeição e escalonamento pedem motivo curto. Após salvar, a interface confirma a gravação e exibe o evento na trilha auditável. Nenhuma ação envia mensagem real. Filtros essenciais permitem focar revisão humana, risco, categoria e prioridade; busca e customizações extensas ficam fora do MVP.

Uma navegação secundária leva ao **Scorecard**, dividido visualmente em Diagnóstico Observado, Avaliação do Protótipo e Cenários. A calculadora mostra premissas editáveis e nunca mistura projeção com histórico. O **Laboratório IT** exibe métricas, matriz de confusão, calibração e casos do teste congelado em sua própria taxonomia. Uma área de **Evidências** oferece versões, comandos de reprodução e exportações. O desenho será desktop-first, responsivo o suficiente para leitura, com estados de carregamento, indisponibilidade e erro explícitos.

**Pergunta de validação:** esta experiência e hierarquia estão corretas para avançar?

**Validação de Luis:** A — Seção 5 aprovada sem ajustes.

### Seção 6 — Entregáveis, limites e definição de pronto — proposta

A entrega pública ficará inteiramente em `submissions/luis-roquette/`. Ela conterá um README executivo com achados, decisões e instruções; a aplicação e os scripts reproduzíveis em `solution/002-support/`; a pesquisa de soluções existentes em `research/002-support.md`; o diário contemporâneo; e evidências como tabelas, métricas, exportações e screenshot real. Dados brutos, PII, credenciais e artefatos sem licença de redistribuição não entrarão no PR.

Antes de implementar, a Regra Zero pesquisará GitHub, Reddit e documentação oficial, comparará pelo menos três candidatos quando existirem e reproduzirá a menor prova do melhor candidato. A escolha de framework, classificador, calibração, recuperação e persistência ficará registrada. SDD transformará o desenho aprovado em tarefa, análise, arquitetura e passos verificáveis; Ponytail removerá qualquer componente que não sustente um critério do desafio.

O desafio estará pronto somente quando os dois datasets forem usados dentro de seus limites; o diagnóstico gerar números rastreáveis; o pipeline local rodar com um comando; classificação, calibração, gate e recuperação forem avaliados fora dos dados de construção; a fronteira humano/IA aparecer na interface; feedback persistir e exportar; horas e cenários financeiros mostrarem premissas; testes passarem; e a aplicação real estiver documentada por screenshot. Limitações e hipóteses rejeitadas serão entregáveis, não notas escondidas.

Ficam fora do MVP: helpdesk real, envio de mensagens, APIs pagas, autenticação, multiempresa, deploy obrigatório, aprendizado online, taxonomia unificada e afirmações causais não sustentadas. Se os dados invalidarem classificação, resposta assistida ou ROI, a função será reduzida e a evidência da invalidação terá prioridade sobre o plano. Após esta seção ser aprovada, `add-task` criará a primeira SPEC; nenhuma implementação começará antes de `plan-task` e da revisão humana dessa SPEC.

**Pergunta de validação:** estes entregáveis, limites e critérios de pronto estão corretos para encerrar o desenho e criar a SPEC?

**Validação de Luis:** A — Seção 6 aprovada; autorizado encerrar a exploração e criar a SPEC.

## I08 — Fechamento da exploração e autorização da SPEC — 2026-09-21 16:49 BRT

- **Objetivo:** encerrar formalmente a descoberta antes de transformar decisões em especificação.
- **Método executado:** 24 ondas socráticas adaptativas, comparação de seis arquiteturas e síntese incremental em seis seções de 200–300 palavras.
- **Resultado:** arquitetura **Support Decision Copilot** escolhida; arquitetura, componentes, fluxo de dados, segurança, falhas, testes, interface, entregáveis, limites e definição de pronto foram aprovados sem ajustes.
- **Julgamento humano:** Luis aprovou cada seção e autorizou explicitamente a criação da SPEC somente após o fechamento completo da exploração.
- **Verificação:** ledger das Ondas 1–24 e Seções 1–6 preservado neste diário; worktree limpo antes da criação do artefato SDD.
- **Evidência:** `.specs/tasks/draft/implement-support-decision-copilot.feature.md` dentro do diretório permitido do Challenge 002.
- **Limitação:** a SPEC criada por `add-task` ainda é um rascunho; pesquisa, análise e refinamento por `plan-task` continuam obrigatórios antes de qualquer implementação.

**Decisão:** exploração encerrada e SPEC inicial autorizada.

## I09 — Fechamento da SPEC inicial e abertura do plano — 2026-09-21 17:05 BRT

- **Etapa encerrada:** criação da SPEC inicial do Support Decision Copilot com requisitos, limites, critérios de validação e gates de processo aprovados.
- **Artefato:** `solution/002-support/.specs/tasks/draft/implement-support-decision-copilot.feature.md`.
- **Estado:** SPEC em `draft`; nenhuma implementação iniciada.
- **Próximo método:** criar e otimizar o plano de implementação com a skill `writing-plans`, mantendo a SPEC como fonte de verdade.
- **Loop de qualidade:** revisar o plano em cascata até obter pelo menos duas passadas consecutivas sem melhorias ou otimizações substanciais; qualquer melhoria substancial reinicia a contagem.
- **Registro:** cada passada documentará foco, achados, alterações e estado da sequência.

**Decisão:** SPEC inicial encerrada como insumo aprovado; planejamento detalhado autorizado, sem autorização para implementar o produto.

## I10 — Loop de otimização do plano — Passada 1 — 2026-09-21 17:28 BRT

- **Foco:** cobertura integral da SPEC e executabilidade do fluxo.
- **Achados substanciais:** faltavam um comando único de demonstração, features e alvos explícitos por domínio, identificador estável para o Dataset 2 e critérios objetivos para thresholds de classificação e recuperação.
- **Correções:** incluído `make demo`; fixados textos/alvos por dataset; definido `row_id` por SHA-256; definidos thresholds por erro seletivo e rubrica humana, com falha segura.
- **Sequência sem melhoria substancial:** 0 de 2.

## I11 — Loop de otimização do plano — Passada 2 — 2026-09-21 17:34 BRT

- **Foco:** falha segura, qualidade mínima dos modelos e completude da auditoria.
- **Achados substanciais:** o plano ainda poderia automatizar com ganho irrelevante sobre o baseline, aceitar intervalos negativos e exportar decisões sem todas as versões nem diferença de edição.
- **Correções:** automação desativada quando o ganho de macro-F1 for menor que 0,02; intervalos inválidos passam a ser isolados e contados; trilha ganhou versões de dados/regras e `edit_ratio`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I12 — Loop de otimização do plano — Passada 3 — 2026-09-21 17:41 BRT

- **Foco:** reprodução a partir de checkout limpo e rastreabilidade das regras.
- **Achados substanciais:** o comando único ainda pressupunha dados colocados manualmente; regras sensíveis e `rules_version` não tinham artefato explícito.
- **Correções:** `make demo` passou a encadear setup, download público, reprodução e app; criado `risk-policy.json` com categorias humanas, fórmula, versão e justificativa.
- **Sequência sem melhoria substancial:** 0 de 2.

## I13 — Loop de otimização do plano — Passada 4 — 2026-09-21 17:49 BRT

- **Foco:** buildabilidade dos comandos e ausência de placeholders.
- **Achado substancial:** assinaturas abreviadas com reticências contrariavam o gate de plano completo; o smoke test com `timeout` terminaria em código 124 mesmo quando saudável.
- **Correções:** contratos foram descritos sem corpo fictício; smoke test agora consulta o endpoint de saúde, encerra o processo e valida a saída esperada.
- **Sequência sem melhoria substancial:** 0 de 2.

## I14 — Loop de otimização do plano — Passada 5 — 2026-09-21 17:56 BRT

- **Foco:** cobertura dos estados de falha, cenários executivos e avaliação final da recuperação.
- **Achados substanciais:** faltavam tratamento verificável de artefatos ausentes/corrompidos/desatualizados, os três cenários pedidos e uma rubrica separada no teste congelado.
- **Correções:** adicionados testes e mensagens de recuperação de artefatos; presets conservador/base/otimista; amostras independentes de 50 consultas para calibração e teste da recuperação.
- **Sequência sem melhoria substancial:** 0 de 2.

## I15 — Loop de otimização do plano — Passada 6 — 2026-09-21 18:03 BRT

- **Foco:** ordem executável da avaliação humana de recuperação.
- **Achado substancial:** havia dependência circular entre escolher o threshold e gerar a amostra que seria avaliada.
- **Correção:** pipeline em passagens idempotentes: gera template de calibração com drafts bloqueados, consome a rubrica concluída para travar o threshold, gera template de teste e só então publica métricas finais.
- **Sequência sem melhoria substancial:** 0 de 2.

## I16 — Loop de otimização do plano — Passada 7 — 2026-09-21 18:11 BRT

- **Foco:** comandos reais do orquestrador de Codespaces.
- **Achado substancial:** o plano usava `run` com um nome inexistente e tentava validar conteúdo ainda ausente no remoto.
- **Correção:** comandos agora usam `create-run luisroquette/ai-master-challenge submission/luis-roquette-002-support`; checkpoints intermediários são testados localmente, commitados e enviados antes da validação remota.
- **Evidência:** `codespace-manager list` confirmou que não existe Codespace reutilizável desse repositório; `--help` confirmou a interface `create-run`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I17 — Loop de otimização do plano — Passada 8 — 2026-09-21 18:18 BRT

- **Foco:** compatibilidade dos comandos Git com as regras reais do repositório.
- **Achado substancial:** `.gitignore` raiz ignora `submissions/`; `git add` comum não incluiria arquivos novos do plano.
- **Correção:** todos os comandos de inclusão pública usam `git add -f` com caminhos explícitos dentro de `submissions/luis-roquette/`; nenhuma regra global foi afrouxada.
- **Correção editorial:** Passadas 1–8 ordenadas cronologicamente.
- **Sequência sem melhoria substancial:** 0 de 2.

## I18 — Loop de otimização do plano — Passada 9 — 2026-09-21 18:22 BRT

- **Foco:** validade do primeiro gate local em checkout sem testes.
- **Achado substancial:** `pytest` sairia com código 5 porque os testes só seriam criados na etapa seguinte.
- **Correção:** o checkpoint inicial agora usa `python -m compileall -q app.py`; pytest começa somente após existir o primeiro arquivo de teste.
- **Sequência sem melhoria substancial:** 0 de 2.

## I19 — Loop de otimização do plano — Passada 10 — 2026-09-21 18:28 BRT

- **Foco:** reprodutibilidade do ambiente Python.
- **Achado substancial:** registrar versões no manifesto não impedia resolução futura de dependências diferentes.
- **Correção:** primeiro setup gera `requirements.lock` completo; execuções seguintes instalam o lock e o pacote local sem resolver dependências novamente.
- **Sequência sem melhoria substancial:** 0 de 2.

## I20 — Loop de otimização do plano — Passada 11 — 2026-09-21 18:35 BRT

- **Foco:** compatibilidade entre a versão Python definida e a máquina de trabalho.
- **Achado substancial:** o Mac expõe Python 3.14, não 3.12; gerar o lock localmente invalidaria o ambiente declarado.
- **Correção:** o checkpoint inicial sobe sem lock; `bootstrap-lock` roda uma única vez no Codespace com Python 3.12, valida o Streamlit, commita o lock na branch e exige `git pull --ff-only` antes da etapa seguinte.
- **Sequência sem melhoria substancial:** 0 de 2.

## I21 — Loop de otimização do plano — Passada 12 — 2026-09-21 18:47 BRT

- **Foco:** coerência entre a SPEC-fonte e o plano derivado.
- **Achado substancial:** a SPEC ainda continha o placeholder de descrição e não referenciava pesquisa nem plano.
- **Correção:** descrição preenchida com objetivo, público, escopo e exclusões; links relativos adicionados para pesquisa e plano de implementação.
- **Nota SDD:** o pacote Codex instalado de `plan-task` contém apenas `SKILL.md`; os agentes, prompts e scripts exigidos pelo workflow não foram instalados. O plano atual foi criado com `writing-plans`; a promoção SDD por `plan-task` permanece bloqueada até instalar o pacote completo e continua obrigatória antes de `implement-task`.
- **Sequência sem melhoria substancial:** 0 de 2.

## I22 — Loop de otimização do plano — Passada 13 — 2026-09-21 18:54 BRT

- **Foco:** cobertura da SPEC, buildabilidade, placeholders, comandos, gates e rastreabilidade.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** `git diff --check` limpo; nove tarefas, dez checkpoints de commit e dez resultados esperados; nenhum marcador `TODO`, `TBD`, `FIXME` ou placeholder residual.
- **Sequência sem melhoria substancial:** 1 de 2.

## I23 — Loop de otimização do plano — Passada 14 — 2026-09-21 18:59 BRT

- **Foco:** documentação contemporânea durante a futura execução.
- **Achado substancial:** o plano concentrava a atualização do diário no fechamento, contrariando a regra de que documentar é tão importante quanto o resultado.
- **Correção:** cada tarefa agora exige entrada curta no diário antes do commit e inclui o process log no mesmo checkpoint.
- **Sequência sem melhoria substancial:** 0 de 2.

## I24 — Loop de otimização do plano — Passada 15 — 2026-09-21 19:03 BRT

- **Foco:** comandos, links, cobertura, checkpoints Git e registro contemporâneo.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** `git diff --check` limpo; nove comandos `git add -f`; dez referências ao diário; links relativos da SPEC resolvem para arquivos existentes.
- **Sequência sem melhoria substancial:** 1 de 2.

## I25 — Loop de otimização do plano — Passada 16 — 2026-09-21 19:08 BRT

- **Foco:** ordem TDD da interface.
- **Achado substancial:** a tarefa de UI implementava páginas antes de criar testes que demonstrassem falha nos fluxos essenciais.
- **Correção:** `AppTest` passa a cobrir página inicial, artefato desatualizado, motivo obrigatório, persistência e separação de projeções antes da implementação.
- **Sequência sem melhoria substancial:** 0 de 2.

## I26 — Loop de otimização do plano — Passada 17 — 2026-09-21 19:12 BRT

- **Foco:** completude por tarefa, TDD, validação, commit e diário.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** nove tarefas, nove blocos de arquivos, nove checkpoints de tarefa e referência ao diário em todos os checkpoints aplicáveis; nenhum placeholder residual.
- **Sequência sem melhoria substancial:** 1 de 2.

## I27 — Loop de otimização do plano — Passada 18 — 2026-09-21 19:16 BRT

- **Foco:** segurança, Ponytail/YAGNI, privacidade, evidência e aderência ao Challenge 002.
- **Resultado:** nenhuma melhoria ou otimização substancial identificada.
- **Verificação:** dependências mínimas; nenhum serviço pago; automação limitada ao roteamento elegível; risco prevalece; PII, dados brutos, modelos e banco local excluídos do Git; ambos os datasets preservam fronteiras próprias.
- **Sequência sem melhoria substancial:** 2 de 2 — meta atingida.

## I28 — Fechamento do planejamento otimizado — 2026-09-21 19:17 BRT

- **Artefato principal:** `solution/002-support/docs/superpowers/plans/2026-09-21-support-decision-copilot.md`.
- **Método:** skill `writing-plans`, 18 passadas críticas em cascata e reinício da contagem após cada melhoria substancial.
- **Resultado:** duas passadas consecutivas finais sem novos achados substanciais; plano considerado otimizado para revisão humana.
- **Pesquisa incorporada:** comparação de interface, modelagem, calibração, recuperação e persistência; inspeção real confirmou 8.469 linhas no Dataset 1 e 47.837 no Dataset 2, além das limitações temporais do Dataset 1.
- **Estado:** planejamento concluído; implementação não iniciada.
- **Gate pendente:** o workflow completo de `plan-task` exige assets ausentes da instalação Codex atual e segue obrigatório, junto da aprovação humana, antes de `implement-task`.

**Decisão:** encerrar o loop de otimização em 2/2 passadas consecutivas sem melhorias substanciais.

## I29 — Reabertura da auditoria contra o repositório canônico — 2026-09-21 19:34 BRT

- **Solicitação:** rever o repositório do desafio e garantir cobertura integral do avaliador e da stack, sem gargalos conhecidos.
- **Fonte verificada:** `upstream/main` no SHA `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; challenge, README raiz, guia de submissão, CONTRIBUTING e template oficial relidos integralmente.
- **Gaps encontrados:** README obrigatório estava planejado dentro da solução, não na raiz da submissão; desperdício não tinha fórmula fechada; satisfação não tinha teste multivariado/fallback; Dataset 1 precisava de proteção explícita contra texto fraco; Laboratório IT não recebia texto livre.
- **Correções adicionais:** matriz de oportunidade entre os datasets sem unir registros; `make doctor`; pisos compatíveis da stack; orçamento de 320 minutos; gate do diff contra `upstream/main`; título oficial do PR.
- **Evidência:** `solution/002-support/docs/reports/2026-09-21-plan-compliance-audit.md`.

**Decisão:** fechamento anterior reaberto corretamente; nova conclusão depende de duas passadas finais desta auditoria sem gap material.

## I30 — Auditoria de stack e reinício da sequência — 2026-09-21 19:46 BRT

- **Achado:** o piso `streamlit>=1.42` não garantia o `AppTest` multipágina planejado; a documentação dessa versão declara incompatibilidade com `st.navigation` e `st.Page`.
- **Correção:** piso elevado para `streamlit>=1.64,<2`, versão cuja API documenta `AppTest.switch_page()`; lock exato continua obrigatório no Codespace.
- **Verificação adjacente:** `scikit-learn>=1.6,<2` cobre `FrozenEstimator`; Python 3.12 permanece suportado.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** incompatibilidade eliminada antes da implementação; as duas passadas finais serão refeitas desde zero.

## I31 — Auditoria final, passada 1 — Requisitos do avaliador — 2026-09-21 19:51 BRT

- **Escopo relido:** challenge, guia de submissão, CONTRIBUTING e template no SHA canônico registrado.
- **Verificação:** diagnóstico, satisfação, desperdício, ambos os datasets, automação e limites humanos, fluxo prático, protótipo real, anti-cherry-picking, process log, README oficial, setup, pasta autorizada e título do PR possuem entrega e gate explícitos no plano.
- **Resultado:** nenhum gap material novo.
- **Sequência sem gap material:** 1 de 2.

**Decisão:** manter o plano sem expansão; seguir para a passada independente de stack e execução.

## I32 — Auditoria de stack, achados operacionais — 2026-09-21 20:02 BRT

- **Achados:** faltava política explícita de reuso/cota de Codespaces; Task 7 executaria suíte completa no Mac; o smoke do Streamlit ficaria bloqueado; o preflight final antecedia arquivos ainda não criados.
- **Correções:** reuso e cota viraram pré-condições; teste local foi reduzido ao arquivo focal; smoke ganhou health check e encerramento; evidências e READMEs agora precedem commit, push e preflight do SHA final.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** os quatro gargalos foram eliminados no plano; reiniciar ambas as passadas finais.

## I33 — Auditoria final reiniciada, gap de comunicação — 2026-09-21 20:07 BRT

- **Achado:** o fluxo prático existia na arquitetura e no app, mas o plano não obrigava o README final a narrá-lo ponta a ponta para o avaliador.
- **Correção:** Task 9 agora exige a sequência explícita de entrada, validação, modelo, gate, recuperação/abstenção, decisão humana e auditoria.
- **Sequência sem gap material:** reiniciada em 0 de 2.

**Decisão:** implementação e comunicação passam a provar o mesmo fluxo operacional.

## I34 — Auditoria final, passada 1 — Cobertura do avaliador — 2026-09-21 20:10 BRT

- **Verificação:** matriz automatizada de 18 exigências contra o plano e releitura das quatro fontes canônicas no SHA `4aed364d572fabe0f1fff1f0c6f32960b30fe575`.
- **Resultado:** 18 de 18 exigências cobertas; nenhum gap material novo.
- **Sequência sem gap material:** 1 de 2.

**Decisão:** preservar o escopo e executar a passada independente de stack, comandos e ciclo de vida.

## I35 — Auditoria final, passada 2 — Stack e execução — 2026-09-21 20:13 BRT

- **Verificação:** nove tarefas e nove contratos de interface; 45 passos; pisos compatíveis; nenhuma suíte completa local; reuso/cota de Codespaces; dois smokes limitados; gate do SHA final; diff restrito à submissão; `git diff --check` limpo.
- **Resultado:** nenhum gap material novo.
- **Sequência sem gap material:** 2 de 2 — meta atingida.

**Decisão:** auditoria encerrada. O plano cobre 100% dos requisitos publicados e não mantém gargalo conhecido de arquitetura, stack ou execução; prontidão funcional permanece condicionada à implementação e aos gates previstos.

## I36 — Fechamento da construção socrática e auditoria pré-implementação — 2026-09-21 20:20 BRT

- **Construção preservada:** o ledger I06 registra integralmente as 24 ondas adaptativas, sempre com pergunta, alternativas de múltipla escolha, resposta, interpretação e dependência da onda seguinte.
- **Síntese preservada:** I07 registra as seis seções incrementais da arquitetura; I08 registra a aprovação humana que autorizou a SPEC.
- **Última etapa:** I29–I35 registram a reauditoria do repositório canônico, os gaps encontrados, as correções e duas passadas consecutivas finais sem novo gap material.
- **Resultado:** 18 de 18 exigências publicadas possuem entrega e gate explícitos; stack, comandos, ciclo de Codespaces e SHA final foram reconciliados.

**Decisão:** encerrar formalmente descoberta, síntese, SPEC e planejamento; iniciar implementação somente pelo workflow SDD validado.

## I37 — Metodologia obrigatória de implementação: Feedback Looping — 2026-09-21 20:21 BRT

- **Autoria:** metodologia definida por Luis; o registro é parte obrigatória e tão importante quanto o resultado final.
- **Fluxo cronológico:** `Planejamento → Revisão → Execução → Teste`.
- **Loop:** cada fase produz reports quase em tempo real para a própria IA; os achados determinam se o trabalho é reforçado no mesmo estágio ou se pode avançar.
- **Gate:** uma fase somente termina quando validada. Falha em revisão ou teste retorna ao planejamento da própria fase, seguido de nova revisão, execução e teste.
- **Cascata:** os loops menores validam passos; os loops maiores validam fases; o `/goal` permanece ativo até todos os critérios de pronto passarem.
- **SDD:** `plan-task` refina e decompõe a SPEC; `implement-task` executa uma etapa por agente, revisa cada fase e verifica a definição de pronto ao final.
- **Limitação técnica registrada:** os `SKILL.md` de SDD estão instalados no Codex, mas os scripts, prompts e agentes nomeados do pacote Claude não estão presentes. O Codex seguirá o mesmo contrato com os agentes e ferramentas disponíveis, sem simular artefatos ausentes.

**Decisão:** avançar automaticamente fase a fase; repetir qualquer etapa reprovada e nunca promover trabalho não validado.

## I38 — SDD `plan-task`: refinamento e decomposição validados — 2026-09-21 21:18 BRT

- **Configuração:** task complexa; qualidade mínima `3,5/5`; até três iterações; tier equivalente a `opus`; sem checkpoints humanos intermediários porque Luis já autorizou seguir para implementação.
- **Fase 2a — pesquisa:** 16 recursos; skill reutilizável criada; juiz `4,70/5`.
- **Fase 2b — impacto:** 28 criações e três modificações estimadas; risco alto; juiz `4,565/5`.
- **Fase 2c — negócio:** 20 critérios, cinco checks, cinco rubricas e 42 casos; juiz `4,405/5`.
- **Fase 3 — arquitetura:** primeira revisão `4,395/5`; dois contratos P1 corrigidos em loop — transporte de OOD e bloqueio de drafts por sinais; segunda revisão `4,65/5`, sem P1/P2.
- **Fase 4 — decomposição:** dez subtarefas em três fases; primeira revisão `4,609/5`; três ambiguidades corrigidas em loop — reprodução dupla, corrida de teste e propriedade documental; segunda revisão `4,742/5`, sem novo achado.
- **Adaptação registrada:** `prompts/judge.md`, scripts e agentes Claude do pacote não existem na instalação Codex; juízes independentes aplicaram as rubricas integrais contidas no `SKILL.md` instalado.

**Decisão:** promover a SPEC de `draft` para `todo`; planejamento e revisão SDD estão validados, permitindo iniciar `implement-task`.

## I39 — Step 01: início da prova de ambiente — 2026-09-21 21:35 BRT

- **Aprovação e escopo:** a autorização humana da SPEC foi confirmada em I38. O step limita-se à prova sintética de ambiente; não implementa dados, modelos ou domínio.
- **Estado inicial:** branch `submission/luis-roquette-002-support`, commit `ee01252b3bf0799ba1508b1c2cad7fbc923bc7ec`, árvore limpa e nenhum workflow de CI presente.
- **Decisão:** manter Streamlit, após comparar os três candidatos já registrados — Streamlit, Gradio e Dash — e reproduzir navegação, formulário editado, transação SQLite, releitura por nova conexão e CSV persistido.
- **Arquivos em preparação:** pacote Python 3.12, comandos Make reais, configuração Streamlit offline, prova em `app.py`, teste focal e README técnico inicial.
- **Gate:** versões exatas só serão registradas após instalação e teste no Codespace gerenciado com o diff deste checkpoint. `make reproduce` falha explicitamente enquanto o pipeline de step posterior não existe.
- **Validação local leve:** `python3 -m compileall -q app.py src tests` e `git diff --check` concluíram com status 0. Instalação, lock e pytest permanecem pendentes do ambiente Python 3.12 gerenciado.
- **Erro e correção:** o primeiro bootstrap selecionou o `python3` padrão 3.14.2 e foi bloqueado como previsto; `/usr/bin/python3.12` foi localizado e passado por `PYTHON`. Na execução seguinte, Ruff encontrou uma linha de 104 caracteres e o `doctor` revelou que seu `echo` final mascarava a falha da sondagem HTTP por `HEAD`. A linha foi quebrada, a sondagem passou a usar GET parcial com redirects e o retorno de erro foi preservado explicitamente.
- **Erro e correção:** com Ruff e `doctor` verdes, o pytest falhou na coleta porque `pythonpath = ["src"]` corretamente expõe o pacote, mas não transforma `app.py` em módulo importável. O teste passou a carregar esse arquivo explicitamente com `runpy`, preservando o package discovery definido.
- **Erro e correção:** o AppTest 1.64 não materializou links para páginas definidas por callables, portanto contar `page_link` não provava navegação. A página de limites foi reduzida a `pages/limits.py`, permitindo usar `AppTest.switch_page()` e validar a troca pelo título renderizado.

## I40 — Step 01: ambiente e prova mínima validados — 2026-09-21 23:24 BRT

- **Ambiente reproduzido:** Codespace `codex-preflight-657v7q4ggx7f5557`, Python 3.12, branch `submission/luis-roquette-002-support` e SHA de código `e1c348557b81278ac1894a1dc068b4dd28ed2615`.
- **Instalação limpa:** `make PYTHON=/usr/bin/python3.12 setup` criou uma nova `.venv` a partir de `requirements.lock`; `import support_copilot` confirmou a versão `0.1.0` sem resolução adicional do pacote local.
- **Versões centrais comprovadas:** Streamlit 1.64.0, pandas 2.3.3, scikit-learn 1.9.1, joblib 1.6.0, pytest 8.4.2 e Ruff 0.16.8.
- **Validação:** `make doctor` passou; `make lint` passou; `make test` concluiu `3 passed`; a prova navegou para a página de limites, editou e submeteu o formulário, confirmou a linha SQLite por nova conexão e comparou byte a byte o conteúdo oferecido ao download com o arquivo CSV persistido.
- **Gate futuro:** `make reproduce` retornou status 2 e explicou que `scripts/reproduce.py` pertence a step posterior; nenhum placeholder retornou sucesso.
- **Smoke real:** o servidor Streamlit respondeu `ok` em `/_stcore/health` e encerrou deliberadamente com status 0. A prova é identificada como sintética e não usa API paga, credencial nem dado pessoal.
- **Ciclo do Codespace:** a sessão do step foi interrompida após os gates porque outro `codespace-manager run` passou a usar o mesmo ambiente. O inventário confirmou branch limpa e estado `Available`; o Codespace não foi apagado nem interrompido para preservar a sessão concorrente.

## I41 — Step 02: contratos de dados e quarentena conservadora — 2026-09-21 20:45 BRT

- **Relógio:** horário obtido nesta execução por `date` no fuso America/Sao_Paulo; os horários anteriores foram preservados como registrados, mesmo com divergência de ordenação.
- **Fontes reais:** download público sem credenciais confirmou 8.469 linhas Customer, schema de 17 colunas; 47.837 linhas IT, colunas `Document`/`Topic_group` e as oito categorias previstas. Arquivos brutos permaneceram em `data/raw/`, ignorado pelo Git; nenhum exemplo bruto foi registrado no diário.
- **Decisão de privacidade:** colunas pessoais/demográficas são descartadas, identificadores conhecidos são mascarados e suspeitas residuais causam quarentena da linha inteira. Entidades capitalizadas desconhecidas também são recusadas, aceitando falsos positivos. Datas ilegíveis mantêm somente uma sentinela inválida; notas inválidas viram nulo, nunca zero. Não se alega anonimização universal; amostras públicas continuam bloqueadas até revisão humana.
- **Contratos:** `data.py` entrega frames independentes por domínio, hashes/qualidade, agrupamento canônico, representante por menor ID e quarentena de rótulos conflitantes. Splits seeded usam 60/20/20 por classe, com arredondamento documentado e mínimo de dez representantes por classe. Calibração se divide uma única vez; `DatasetSplit.test` contém apenas IDs/grupos, sem features/rótulos finais.
- **Implementação:** pipeline inicial publica JSON finito e atômico de treino/calibração e manifesto por último; modelos, fila e assistência futura ficam explicitamente indisponíveis. README e Makefile documentam fontes, destino manual e retomada sem fallback sintético.
- **Loop de teste:** seis testes focados passaram localmente em 0,27 s usando Python 3.12 e dependências existentes no cache. O primeiro lint identificou cinco linhas acima do limite; foram quebradas sem mudança funcional e o Ruff passou. `git diff --check` também passou.
- **Gate remoto iniciado:** o Codespace inicialmente estava ativo e foi preservado. Após confirmar `Shutdown` e árvore limpa, `codespace-manager run` iniciou validação em worktree temporário, com snapshot tar de SHA-256 `272bf723ce0eca9de71d41eba8cdfaf20ec028d8344dbd21688b62a4310663b1`. A reprodução real e suas contagens ainda não foram declaradas aprovadas neste registro.
- **Correção do registro do gate:** a primeira tentativa foi recusada com status 73 porque o estado passou a `ShuttingDown` antes da execução. A segunda iniciou o ambiente, mas o comando não chegou a executar: uma linha base64 longa ultrapassou o transporte do PTY e deixou o shell aguardando fechamento de aspas. Somente os processos dessa tentativa foram encerrados; o checkout permaneceu limpo. O reenvio usará linhas curtas e o snapshot atualizado `226aa25155a34a372816faeb4140391c925289c5a62f984f25386918febc2fd4`, que inclui validação estrutural adicional do manifesto, novamente coberta pelos seis testes verdes.
- **Terceira tentativa e limite:** o transporte com linhas curtas funcionou e criou `/tmp/support-step02.udisVV` sobre a base remota `e1c3485`. A verificação falhou antes de extrair o snapshot: `echo` acrescentou um terceiro espaço entre hash e caminho; `sha256sum` interpretou esse espaço como parte do filename. Correção identificada: usar `printf '%s  %s\n' HASH CAMINHO`. Após três tentativas sem gate concluído, as novas tentativas foram interrompidas conforme `AGENTS.md`; a hipótese duvidosa era o transporte/conferência do snapshot pelo PTY, não o resultado dos testes locais. Nenhum lint, teste ou pipeline remoto deste step recebeu alegação de aprovação.
- **Estado entregue ao orquestrador:** seis testes de dados verdes, Ruff verde nos três arquivos Python novos, compilação e `git diff --check` verdes. Fontes reais/schema/IDs/taxonomia foram inspecionados, mas contagens completas de sanitização/deduplicação, reprodução remota e revisão humana de amostras continuam pendentes. O worktree remoto temporário contém o arquivo de transporte e não foi apagado automaticamente.

## I42 — Step 02: retomada pelo commit da branch — 2026-09-21 20:55 BRT

- **Correção de processo:** o orquestrador autorizou abandonar o transporte artesanal por PTY e validar somente arquivos da branch publicados em commit intermediário. Nenhuma nova função ou etapa foi adicionada.
- **Inspeção:** apenas os seis arquivos do step e o registro contemporâneo estavam alterados; nenhum workflow de CI/configuração de deploy existe no repositório e a branch não possui PR aberto. O push intermediário de feature está autorizado pela regra global; não substitui o gate remoto.
- **Gates repetidos:** seis testes focados passaram em 0,42 s; Ruff passou; `git diff --check` passou. O cache local serve apenas aos testes focados; o lock do ambiente gerenciado continua sendo a referência de reprodução.
- **Próxima execução:** commit/push na branch `submission/luis-roquette-002-support`; reuso apenas de Codespace parado e limpo, atualização por Git e conferência do SHA exato antes de lint, testes e reprodução real.

## I43 — Jornada construtiva: o diário como entrega — 2026-09-21

- **Definição de Luis:** o process log é o diário oficial da construção. Deve mostrar como o arquiteto desenha e como o engenheiro constrói.
- **O que registrar:** decisões, hipóteses, critérios, feedback, erros, correções, validação e motivo para avançar ou repetir. Fragmentos curtos, escritos durante o trabalho; uma etapa não avança apenas porque um arquivo foi concluído.
- **Pivot do step 02:** snapshot/PTTY falhou em três tentativas. A premissa do transporte artesanal foi revista; commit e push do SHA exato substituíram esse caminho. O código foi publicado em `497ab03962f6f23481e580dfebb3c483ab55b190`, depois de seis testes focados, lint e verificação de whitespace aprovados.
- **Concorrência preservada:** o Codespace voltou a `Available` por uma execução concorrente de `lead-step01-manifest`. Nenhum processo dessa sessão foi interrompido. O suporte aguarda `Shutdown` e checkout limpo antes de executar seus gates.
- **Critério para avançar:** validar o SHA publicado no ambiente gerenciado, concluir os gates de dados e registrar resultados reais. Falha de código retorna ao ciclo correção → teste focado → commit/push → novo gate; ausência de evidência permanece explícita.
