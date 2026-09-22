# RavenStack: diagnóstico reproduzível de churn

Pipeline Python 3.12 que cruza as cinco tabelas do Challenge 001, testa as alegações do CEO, avalia seis causas candidatas e publica relatório, dashboard e fila operacional a partir do mesmo conjunto canônico de artefatos.

## Decisão executiva

Os dados não sustentam priorizar uma causa como raiz. As seis hipóteses falharam pelo menos um gate de estabilidade cronológica, associação controlada, cobertura ou corroboração entre tabelas. Portanto, a fila operacional está deliberadamente vazia; uma watchlist separada nomeia contas somente para validar sinais e o relatório recomenda corrigir a confiabilidade da medição antes de lançar uma intervenção causal.

Ainda assim, há fatos úteis:

- o uso médio ajustado por cobertura sobe no agregado, mas cai entre as contas que churnam em até 30 dias;
- satisfação é `concern`, não “ok”: média e cobertura de respostas não passam juntas pelo gate;
- 19.142 usos antecedem o início da assinatura, 13.198 antecedem o cadastro e 1.077 tickets antecedem o cadastro;
- desligamento de renovação automática expõe no máximo US$ 2.096.221 de MRR em 97 contas, mas não passou o gate entre tabelas;
- o modelo opcional passou ganho de average precision e lift, mas foi recusado por Brier e não convergência; nenhum score foi publicado.

Leia primeiro o [relatório executivo](artifacts/report.md). A [fila CSV](artifacts/account_queue.csv) é vazia por desenho, não por falha do pipeline; a [watchlist](artifacts/account_watchlist.csv) não autoriza contato ou intervenção.

## Reproduzir

Requer Python 3.12. Se `python3.12` não estiver disponível, `make setup` usa `uv` quando instalado.

```bash
cd submissions/luis-roquette/solution/001-churn
make setup
make reproduce
make check
make app
```

O dashboard abre em `http://localhost:8501`. Hospedagem pública é opcional; a reprodução local é a entrega autoritativa.

## Arquitetura

```text
5 CSVs imutáveis
      ↓ contratos + qualidade
painéis observed/strict por conta e cutoff
      ↓ claims + 6 hipóteses + segmentos + modelo opcional
AnalysisResult único
      ↓ publicação atômica + checksums
relatório · dashboard somente leitura · fila CSV · manifesto
```

`make check` executa Ruff e pytest, reproduz em diretório temporário e compara conteúdo e parâmetros com os artefatos canônicos. Só timestamp UTC e SHA de origem podem variar.

## Estrutura

- `src/ravenstack_churn/`: contratos, painel temporal, diagnóstico, modelo e publicação.
- `tests/`: testes de dados, vazamento, gates, consistência, Markdown e dashboard.
- `artifacts/`: saídas canônicas protegidas por `run_manifest.json`.
- `app.py`: Streamlit somente leitura; nunca recalcula a análise.
- `.specs/` e `docs/superpowers/plans/`: SPEC e plano SDD executado.

## Artefatos

| Arquivo | Conteúdo |
|---|---|
| `report.md` | decisão executiva, claims, evidências, segmentos, ações e limitações |
| `findings.csv` | seis hipóteses com efeito, intervalo, sensibilidade e gate |
| `claim_checks.csv` | uso e satisfação por coorte |
| `segment_metrics.csv` | snapshot diagnóstico por segmento; não é taxa populacional histórica |
| `account_panel.csv` | painel completo `observed` + `strict` |
| `account_queue.csv` | contas acionáveis apenas quando existe finding aceito |
| `account_watchlist.csv` | contas nomeadas para validação descritiva, sem ação autorizada |
| `quality_report.json` | schema, nulos, duplicidades e contradições |
| `model_evaluation.json` | métricas fora do tempo e motivos de recusa |
| `run_manifest.json` | ambiente, parâmetros e SHA-256 dos outros nove artefatos |

## Gates analíticos

Uma causa só é aceita se direção e intervalo ajustado forem coerentes, a leitura `observed`/`strict` for estável, amostra e cobertura forem suficientes e outra tabela corroborar o sinal. Associação aceita ainda não é causalidade comprovada.

O modelo usa split estável por conta, treino até agosto de 2024 e teste de setembro a novembro. Scores só são publicados se houver ganho de average precision, lift ≥ 1,25, Brier não pior que o baseline e avaliação segmentada completa.

## Dados e limitações

Fonte: [SaaS Subscription & Churn Analytics](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset), por River @ Rivalytics, licença MIT. Os cinco arquivos originais são preservados e verificados por SHA-256.

As datas contraditórias limitam inferência; feedback textual é usado apenas retrospectivamente; MRR exposto é oportunidade máxima, não receita recuperável; e nenhum experimento de intervenção existe para estimar impacto causal. O dataset parece sintético e não deve orientar contato real com clientes.

## Solução de problemas

- `Python 3.12 ou uv é obrigatório`: instale um deles e repita `make setup`.
- `ravenstack_*.csv: checksum mismatch`: restaure os dados brutos oficiais e repita `make reproduce`.
- `findings.csv checksum mismatch` (ou outro artefato): não edite `artifacts/`; execute `make reproduce`.
- `Artefatos inválidos` no app: conclua `make reproduce` antes de `make app`.
- wheel ausente: confirme Python 3.12; as versões fixadas possuem wheels Linux e macOS.

## Processo

O método completo está nos diários [pré-início](../../process-log/000-pre-inicio.md), [descoberta socrática](../../process-log/001-descoberta-socratica.md), [otimização do plano](../../process-log/002-otimizacao-plano-loop.md) e [implementação em feedback looping](../../process-log/003-implementacao-feedback-looping.md).
