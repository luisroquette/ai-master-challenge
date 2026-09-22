# Submissão — Luis Roquette — Challenge 002

## Sobre mim

- **Nome:** Luis Roquette
- **LinkedIn:** Não informado
- **Challenge escolhido:** 002 — Redesign de Suporte

---

## Executive Summary

Construí um **Support Decision Copilot** local que conecta diagnóstico operacional,
classificação, gate de risco, precedentes históricos e decisão humana auditável. A
análise encontrou uma limitação estrutural: o Dataset 1 não permite medir tempo até a
primeira resposta nem resolução total; só permite o intervalo pós-primeira-resposta.
Além disso, a amostra sanitizada atual não sustenta uma estimativa observada de
desperdício nem valida respostas sugeridas. A recomendação é usar a fila e os modelos
como apoio à revisão humana, mantendo rascunhos bloqueados até existir avaliação humana
suficiente e preservando custos apenas como cenários editáveis.

---

## Solução

### As três respostas ao Diretor de Operações

#### 1. Onde estamos perdendo tempo?

- O único intervalo temporal observável é
  `Time to Resolution - First Response Time`, chamado de **intervalo
  pós-primeira-resposta**. Não é tempo total de resolução.
- A execução real encontrou somente quatro intervalos válidos após a sanitização.
  Isso não sustenta ranking de gargalos por canal, prioridade e tipo.
- Nenhum grupo atingiu as 30 linhas válidas exigidas para estimar excesso recuperável.
  A aplicação mostra a limitação em vez de transformar amostra insuficiente em finding.
- A associação com satisfação também ficou sem sinal confiável no desenvolvimento; não
  há alegação causal sobre canal, tipo ou tempo.

#### 2. O que pode ser automatizado com IA?

- **Classificação e roteamento interno** podem ser automatizados somente quando o modelo
  é suportado, a entrada é válida, a confiança calibrada supera o limite e nenhuma regra
  de risco bloqueia o caso.
- Prioridade crítica, tema sensível, ambiguidade, PII, artefato inválido ou incerteza
  sempre levam a revisão humana, mesmo com confiança alta.
- **Respostas não são enviadas automaticamente.** O sistema só pode oferecer um
  precedente histórico editável após uma avaliação humana formal da recuperação.
- A população elegível atual foi zero; portanto, os rascunhos permanecem bloqueados e
  não houve relaxamento de regra, duplicação de consulta nem geração livre como fallback.

#### 3. Como isso funciona na prática?

O agente abre uma fila Customer Support, vê categoria, confiança, riscos e decisão do
gate, consulta até três fontes sanitizadas e decide entre aprovar, editar e aprovar,
rejeitar ou escalonar. A decisão é gravada atomicamente em SQLite e pode ser exportada
em CSV. O scorecard separa histórico observado, desempenho medido e cenários projetados.
Um Laboratório IT independente demonstra a taxonomia de oito classes do Dataset 2 sem
misturar linhas, rótulos ou métricas com Customer Support.

### Abordagem

1. Releitura do briefing até duas passadas consecutivas sem novos achados.
2. Descoberta socrática em 24 ondas e especificação aprovada antes do código.
3. Pesquisa comparativa e prova mínima antes de escolher Streamlit, scikit-learn e SQLite.
4. Implementação SDD por fases, com revisão, execução, teste e diário contemporâneo.
5. Falha segura: capacidade sem evidência é desativada e documentada, não simulada.

A arquitetura, os comandos e os contratos técnicos estão no
[README da solução](solution/002-support/README.md). A pesquisa que fundamentou as
escolhas está em [pesquisa técnica](research/002-support.md).

### Resultados / Findings

- Fontes reais inspecionadas: 8.469 linhas Customer Support e 47.837 linhas IT.
- Após a sanitização conservadora registrada no último gate da Phase 2: 1.389 linhas
  Customer e 26.472 linhas IT permaneceram disponíveis; exclusões e denominadores são
  parte do manifesto reproduzível.
- Classificadores, calibração, risco e cobertura são mantidos por domínio; nenhum join
  fictício conecta os datasets.
- A fila real, o escalonamento, a persistência após reinício, o export e as páginas
  separadas foram comprovados no navegador. Aprovação/edição ficaram corretamente
  bloqueadas; fixtures cobrem as quatro ações, mas não contam como evidência real.
- A avaliação humana de recuperação não pôde começar por ausência de 30 consultas
  elegíveis. Essa insuficiência mantém a assistência de resposta desativada.

### Recomendações

1. Operar primeiro como copiloto: revisão humana obrigatória para comunicação externa.
2. Coletar timestamps de criação e estados do atendimento para medir gargalos reais.
3. Auditar a coleta de satisfação e ampliar denominadores antes de priorizar drivers.
4. Avaliar 30 consultas independentes antes de habilitar qualquer rascunho histórico.
5. Tratar horas e custo como cenários editáveis até existir medição operacional posterior.

### Limitações

- O Dataset 1 não observa criação do ticket; não mede primeira resposta nem resolução total.
- A sanitização conservadora reduz cobertura e pode introduzir viés de seleção.
- Associação não prova causalidade; projeção de custo não é economia realizada.
- Um único revisor seria permitido pelo protocolo, mas nenhuma rubrica humana foi
  preenchida porque a população elegível foi insuficiente.
- Não há helpdesk, envio de mensagem, autenticação, multiempresa, aprendizado online ou
  deploy obrigatório. A entrega é uma demonstração local.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| Codex | Descoberta socrática, SDD, implementação, revisão e testes por fases |
| Git/GitHub CLI | Isolamento em worktree, histórico, diff e verificação remota |
| GitHub Codespaces | Gates pesados reproduzíveis em Python 3.12 |

### Workflow

1. Transformei o briefing em critérios verificáveis antes de escolher tecnologia.
2. Usei perguntas adaptativas para definir usuário, risco, evidência e limites do MVP.
3. Comparei alternativas, reproduzi a menor prova útil e congelei o plano aprovado.
4. Implementei em ciclos Planejamento → Revisão → Execução → Teste.
5. Registrei contemporaneamente decisões, erros, correções, hashes e gates.

### Onde a IA errou e como corrigi

A IA inicialmente interpretou a instalação do SDD como uso no Claude Code; corrigi para
execução no Codex. Durante a implementação, a primeira normalização aceitava texto antes
de unir quebras de linha, permitindo divergência na segunda sanitização. A validação foi
movida para depois da normalização e recebeu regressão. O primeiro manifesto da fila
também não declarava a dependência do modelo Customer; o grafo e a mensagem de falha
foram corrigidos antes de avançar.

### O que eu adicionei que a IA sozinha não faria

Defini três métodos obrigatórios: saturação por duas releituras consecutivas sem novos
achados, descoberta socrática em ondas adaptativas e documentação com a mesma importância
do resultado. Também defini a redundância pós-implementação e a lapidação em loops, sempre
reiniciando a contagem quando surge uma correção relevante.

O registro completo, incluindo perguntas, respostas e verificações, está no
[diário contemporâneo](process-log/002-support.md).

---

## Evidências

- [x] [Narrativa contemporânea e decisões](process-log/002-support.md)
- [x] [Pesquisa técnica e prova mínima](research/002-support.md)
- [x] [Código e instruções reproduzíveis](solution/002-support/README.md)
- [x] [Screenshot real da demonstração](solution/002-support/evidence/screenshot.png)
- [x] [Export persistido correlacionado ao audit ID 1](solution/002-support/evidence/decisions-demo.csv)
- [x] [Métricas, hashes e limitações finais](solution/002-support/evidence/metrics.json)
- [ ] CK-12 — 30 avaliações humanas por split: **incompleto por zero consultas elegíveis**
- [x] Gate consolidado: `make doctor`, 230 testes, Ruff, reprodução real e 34 testes
  de workflow no Python 3.12 do Codespace gerenciado

---

_Submissão enviada em: Não enviada; publicação depende dos gates finais._
