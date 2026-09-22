# Support Decision Copilot

Aplicação local para diagnosticar a operação Customer Support, classificar tickets em
dois domínios independentes, aplicar um gate de risco e registrar decisões humanas sem
enviar mensagens externas. O estado atual é **seguro por padrão**: a recuperação não
produz rascunhos porque a execução real encontrou zero consultas elegíveis para a
avaliação humana obrigatória.

- [README executivo](../../README.md)
- [Pesquisa técnica](../../research/002-support.md)
- [Diário contemporâneo](../../process-log/002-support.md)
- [Challenge 002 oficial](../../../../challenges/process-002-support/README.md)

## Resposta curta às três perguntas

1. **Onde perdemos tempo?** O dataset não contém criação do ticket; só permite medir o
   intervalo pós-primeira-resposta. Restaram quatro intervalos válidos e nenhum grupo
   elegível de 30 linhas, insuficientes para afirmar um gargalo ou desperdício recuperável.
2. **O que automatizar?** Classificação e roteamento interno somente com modelo suportado,
   confiança calibrada e ausência de riscos. Resposta externa, caso crítico, sensível,
   ambíguo, inválido ou incerto permanece humano.
3. **Como funciona?** Streamlit abre na fila, explica a decisão, mostra precedentes,
   registra quatro ações em SQLite e exporta CSV; scorecard e Laboratório IT ficam em
   páginas separadas.

## Arquitetura mínima

```text
CSVs públicos → sanitização/splits → diagnóstico + modelos separados
                                      ↓
fila Customer → classificador → gate de risco → precedentes → decisão humana → SQLite/CSV
scorecard      ← evidências agregadas         Laboratório IT ← modelo/taxonomia IT
```

Customer Support usa o Dataset 1 para operação, diagnóstico e precedentes. IT usa o
Dataset 2 somente no laboratório de oito classes. Os domínios reutilizam código, mas não
linhas, rótulos, taxonomias ou métricas. A interface carrega artefatos validados; não
treina, não retuna thresholds e não aprende com uma decisão individual.

## Requisitos e setup

Requer Python 3.12, `make`, `curl` e `unzip`. O ambiente validado usa as versões exatas de
`requirements.lock`; `make setup` não resolve versões novas.

```bash
make PYTHON=python3.12 data
make PYTHON=python3.12 setup
make PYTHON=python3.12 doctor
make PYTHON=python3.12 reproduce
make PYTHON=python3.12 demo
```

`make data` é a única etapa normal que exige rede. Depois de baixar os CSVs e reproduzir
os artefatos, inferência, decisões, exportação e demonstração funcionam localmente sem API,
credencial ou serviço externo. `make demo` apenas valida o ambiente e inicia o Streamlit;
não instala, baixa ou treina.

## Fontes e retomada manual

| Domínio | Download público | Arquivo esperado |
|---|---|---|
| Customer | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/suraj520/customer-support-ticket-dataset) | `customer_support_tickets.csv` |
| IT | [Kaggle](https://www.kaggle.com/api/v1/datasets/download/adisongoh/it-service-ticket-classification-dataset) | `all_tickets_processed_improved_v3.csv` |

Se `make data` falhar, baixe os dois ZIPs pelos links, extraia exatamente esses arquivos
para `data/raw/` e repita `make reproduce`. Não use CSV sintético como substituto. Dados
brutos, `.venv`, artefatos reproduzíveis, banco e exports runtime são ignorados pelo Git.

## Comandos

| Comando | Função |
|---|---|
| `make doctor` | Confere Python 3.12, lock, ferramentas, fontes e diretório gravável |
| `make setup` | Cria `.venv` e instala lock + pacote local |
| `make data` | Baixa os dois datasets públicos sem credenciais |
| `make reproduce` | Sanitiza, divide, analisa, treina e publica artefatos verificados |
| `make demo` | Executa `doctor` e abre a aplicação local |
| `make test` | Executa a suíte pytest |
| `make lint` | Executa Ruff |

O lock só deve ser criado por `make bootstrap-lock` em Python 3.12 quando ainda não
existir. Ele não deve ser regenerado para “consertar” uma falha de ambiente.

## Fluxo do agente

1. A fila Customer é ordenada por prioridade existente, quantidade de riscos e incerteza.
2. O detalhe mostra texto sanitizado, categoria, confiança, regras e decisão do gate.
3. Até três precedentes do treino podem aparecer com ID e similaridade.
4. O agente aprova, edita e aprova, rejeita ou escalona; as duas últimas exigem motivo.
5. A confirmação só aparece após escrita e releitura do `audit_id`; o CSV usa os bytes do
   arquivo persistido e neutraliza fórmulas de planilha.

Nenhuma ação envia mensagem, fecha ticket, retreina modelo ou altera threshold. Sem draft
validado, aprovação é bloqueada e a saída correta é revisão humana ou escalonamento.

## Evidência: observado, medido e projetado

### Histórico observado

- Dataset 1 lido: 8.469 linhas; 1.389 passaram pela sanitização conservadora no último
  gate registrado da Phase 2.
- Dataset 2 lido: 47.837 linhas; 26.472 passaram pela mesma fronteira pública.
- O intervalo temporal disponível é pós-primeira-resposta, não resolução total.
- Quatro intervalos válidos e nenhum grupo de 30 linhas impedem conclusão de gargalo ou
  desperdício observado. A satisfação no desenvolvimento ficou sem sinal confiável.

### Desempenho medido

- Modelos são escolhidos contra dummy e baselines textuais por CV somente no treino.
- Teste fica lacrado até modelos, calibração, regras e thresholds estarem congelados.
- Métricas finais por classe, confusão, log loss, ECE e risco/cobertura dependem do gate
  final e não são antecipadas neste README.
- Fixtures provaram fluxo, persistência e falha segura; não contam como resultado real.

### Cenários projetados

Conservador, base e otimista aplicam volume elegível, fração endereçável, minutos poupados
e custo/hora editáveis. Horas são `volume × fração × minutos / 60`; custo é `horas ×
custo/hora`. Nenhum cenário é apresentado como economia realizada ou efeito causal.

## Protocolo humano de recuperação

A fonte normativa completa é o docstring/ajuda de
`src/support_copilot/retrieval.py`. Resumo operacional:

```bash
.venv/bin/python -m support_copilot.retrieval prepare-review \
  --artifacts artifacts --split calibration

.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split calibration \
  --rubric CAMINHO_DA_RUBRICA_PREENCHIDA.csv

.venv/bin/python -m support_copilot.retrieval prepare-review \
  --artifacts artifacts --split test

.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split test \
  --rubric CAMINHO_DA_RUBRICA_FINAL.csv
```

Calibração e teste exigem amostras seeded, estratificadas e independentes de 30 consultas.
O avaliador preenche relevância, correção, segurança e esforço de edição de 1 a 5, além de
pseudônimo e timestamp. Menos de 30 consultas, formulário incompleto, nota de segurança
abaixo de 3 ou médias de correção/segurança abaixo de 4 mantêm drafts bloqueados. O teste
final nunca retuna o threshold. A execução real atual registrou `insufficient_evidence`
com zero consultas elegíveis; portanto, nenhuma rubrica foi fabricada.

Para congelar explicitamente uma demonstração sem revisão suficiente:

```bash
.venv/bin/python -m support_copilot.retrieval lock-review \
  --artifacts artifacts --split calibration --decision disabled
```

## Privacidade, integridade e falhas

- Nome, email, telefone, URL, IP e identificadores são removidos antes de treino, UI,
  persistência e export. Texto suspeito inteiro entra em quarentena.
- Sanitização por regex é conservadora, não prova anonimização universal e pode reduzir
  cobertura. Toda amostra pública ainda exige revisão humana.
- Manifesto vincula fontes, lock, configuração, código, splits e artefatos por hashes.
- Artefato ausente, corrompido, incompatível ou stale bloqueia só a capacidade afetada,
  mostra caminho relativo, causa e `make reproduce` como correção.
- SQLite usa transação atômica e idempotência por UUID. Falha não apaga registros antigos
  nem anuncia sucesso.

## Evidências finais pendentes

A etapa final deve substituir este checklist somente com artefatos reais correlacionados:

- [ ] screenshot sanitizado da fila/scorecard/Laboratório IT;
- [ ] aprovação ou edição e escalonamento persistidos após reinício;
- [ ] CSV público com os mesmos audit IDs;
- [ ] métricas finais e estado da rubrica humana;
- [ ] `make test && make lint && make reproduce` no SHA/diff entregue.

Ausência de humano ou de amostra suficiente mantém o critério correspondente pendente;
desativar a função é o comportamento seguro, mas não fabrica a evidência exigida.

## Limitações e escopo excluído

- Sem timestamp de criação, primeira resposta e resolução total não são observáveis.
- Associação não é causalidade; custo é cenário, nunca fato histórico.
- Sanitização forte reduz amostra e pode enviesar as conclusões.
- Recuperação está desativada por evidência insuficiente; não há geração livre de fallback.
- Não existem helpdesk real, envio, autenticação, multiempresa, deploy obrigatório ou
  aprendizado online.

## Verificação

Durante o paralelo da Phase 3, este step executa somente:

```bash
.venv/bin/pytest tests/test_workflow.py::test_delivery_documentation_contract -q
.venv/bin/ruff check tests/test_workflow.py
git diff --check
```

A suíte completa e a demonstração visual pertencem ao gate final. Resultado de outro SHA,
fixture sintética ou teste S07 isolado não é apresentado como aprovação da entrega final.
