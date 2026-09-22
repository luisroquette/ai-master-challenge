# Cockpit de Social Media — Challenge 004

Aplicação local que valida o CSV do desafio, produz análise contextual reproduzível, prioriza ações, registra decisões humanas em SQLite e exporta o mesmo resultado em HTML e CSV.

## Instalação

Requisitos testados em 22/09/2026: Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3 e SQLite 3.50.4.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r submissions/luis-roquette/solution/004-social/requirements.txt
python -m pip check
```

Baixe o [Social Media Sponsorship & Engagement Dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset), publicado sob licença MIT, e localize `social_media_dataset.csv`. O CSV bruto não deve ser copiado para a submissão.

## Validar e reproduzir

Da raiz do repositório:

```bash
test -f submissions/luis-roquette/solution/004-social/tests/test_acceptance.py
python -m unittest discover \
  -s submissions/luis-roquette/solution/004-social/tests \
  -t submissions/luis-roquette/solution/004-social \
  -p 'test_*.py' -v

python submissions/luis-roquette/solution/004-social/analysis.py \
  /caminho/social_media_dataset.csv \
  --evidence /tmp/evidence.csv \
  --summary /tmp/summary.html \
  --report /tmp/analysis.md
```

Após as correções documentadas até I37, o gate em ambiente virtual novo aprovou 74/74 testes em 15,216 s (15,80 s totais), com warnings tratados como erros. A CLI processou as 52.214 linhas em 20,46 s, com pico residente de 553.402.368 bytes e zero swap; CSV e Markdown foram idênticos byte a byte aos publicados, com SHA-256 `9eebfa0d…` e `a8ab9b96…`. O resumo impresso permaneceu em uma página A4.

## Executar o cockpit

```bash
SOCIAL_COCKPIT_DB_PATH=/tmp/social-cockpit.sqlite3 \
python -m streamlit run submissions/luis-roquette/solution/004-social/app.py \
  --server.address 127.0.0.1 \
  --browser.gatherUsageStats false
```

Sem `SOCIAL_COCKPIT_DB_PATH`, o banco fica em `~/.local/share/ai-master-challenge-004/cockpit.sqlite3`. Ele guarda metadados, baselines, decisões e outcomes; nunca o CSV bruto, descrições, comentários ou URLs.

## Roteiro de cinco minutos

1. Envie um CSV válido e confira hash, período, linhas e plataformas.
2. Leia a primeira prioridade, seus componentes e o benchmark contextual.
3. Abra “Registros de origem e contexto” e explique taxa, volume, amostra e confiança.
4. Aceite, rejeite ou edite a recomendação; confirme a decisão no histórico.
5. Reinicie a aplicação, confira a persistência e baixe HTML/CSV.

O navegador automatizado concluiu esse fluxo técnico, inclusive erro sem perda de estado, revisão vinculada, guarda cronológica de outcomes e reinício com histórico completo. O cronômetro de um Gestor de Social Media real permanece como único gate humano pendente (HR-01); automação não o substitui.

## CSV com histórico local

As linhas analíticas conservam a fonte ativa. Cada `decision` conserva fonte, escopo, método, baseline, data `decided_at`, IDs de evento/revisão, estado, textos original/editado/efetivo, responsável e janela. Cada `outcome` conserva a fonte observada, `recorded_at` (momento do registro, não data de execução), declaração de execução, período observado, comparação, cobertura, delta e volumes diários em views/dia. `decision_id` liga a observação à decisão; `decision_source_hash` identifica a fonte do baseline. `non_causal=true` impede interpretar a comparação como efeito causal ou ROI.

As colunas históricas são acrescentadas somente quando há decisões; a exportação estática sem histórico permanece inalterada. O escopo de novos outcomes é persistido com a observação. Outcomes legados sem esse campo exportam escopo vazio, nunca o escopo do upload atual.

Campos históricos acima de 32.768 caracteres ficam vazios na linha principal e são transportados por linhas `history_field`: agrupe por `decision_id`, `outcome_id` e `field_name`, ordene `field_chunk`, aplique `json.loads` a cada `field_value` e concatene. O resultado é a célula CSV original, incluindo eventual apóstrofo de proteção contra fórmulas; para `baseline`/`observed`/`comparison`, decodifique então o JSON recomposto. Os blocos mantêm leitura no limite padrão do Python. Referências analíticas `source_ref` continuam usando `reference_chunk`/`reference_index`, sem mudança de contrato.

## O que ler

- [Análise e estratégia](./analysis.md)
- [Evidências reproduzíveis](./evidence.csv)
- [SPEC](./SPEC.md)
- [Diário do processo](../../process-log/004-social.md)
- [Prova de prioridades, contexto e downloads](../../process-log/evidence/004/cockpit-priorities-proof.png)
- [Prova do histórico e outcomes após reinício](../../process-log/evidence/004/cockpit-proof.png)

## Limitações

- ERv usa views, não alcance único; audiência é rótulo agregado do post, não engajamento individual.
- Patrocínio é associação observacional. Sem investimento, receita ou conversão, não há ROI financeiro nem causalidade.
- A frequência é hipótese de teste derivada de semanas ISO completas dentro do mesmo mês/contexto, não frequência ótima.
- Atualização é importação manual; não há APIs externas, publicação, contratação ou investimento automático.
