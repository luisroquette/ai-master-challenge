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
