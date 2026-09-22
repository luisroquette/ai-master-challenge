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

Após a correção dos dois achados da Passada 7, o gate acumulado aprovou **122/122 testes** com warnings tratados como erros. A CLI real foi repetida byte a byte: `evidence.csv` SHA-256 `9c01467b7242bf0bd1af3180d1f56fae0c3e527719b4b8e5d716ab0ce674e66d`, `analysis.md` `a1a1692f3e448169b612a83d2006657173feb26eced0eecf592138d2414d6dbc` e HTML `40e7d9ea711c630512c6a48fcfc4aba13cb0a0734b3f0e6b6f064a12027fca77`. O CSV contém seis recomendações e 6.703 registros; o resumo normal e a fixture adversarial permaneceram em uma página A4.

As três prioridades executivas mantiveram scores e ordem sob IDs 2.4.0: `sponsorship-bcd859ce1b79e99d`, `sponsorship-4bfa6bf4c2b6b7e9` e `sponsorship-ab345324b2d495ba`. O CSV preserva ainda `sponsorship-e0088572ab877b95`, `sponsorship-5aa3da373ed4f6a2` e `sponsorship-5d0bd99974adeb18`.

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

Cada decisão guarda o snapshot exato do motor: alvo, comparador, quartis/fallback, força, contexto e referências. Patrocínio mantém separados os braços e usa mediana das medianas por creator; editorial usa apenas o grupo orgânico definido; alertas preservam post/benchmark e um agregado contextual separado para acompanhamento. A observação posterior reaplica esse contrato à nova fonte; só a janela temporal muda, não categoria, audiência, patrocínio ou estatística. Creators sem taxa definida não satisfazem a amostra mínima.

O histórico mostra o snapshot mesmo sem CSV. Reenviar o mesmo hash verifica referências pelo escopo salvo, inclusive quando a recomendação não está na fila ativa ou os filtros mudaram. `METHOD_VERSION = "2.4.0"` é o contrato ativo. Eventos `1.0.0`–`2.3.0` continuam legíveis, mas são incompatíveis para nova comparação automática e ficam `pending / method_mismatch`. As capturas históricas/outcomes preservadas registram eventos 2.0.0; não são apresentadas como nova comparação 2.4.0.

A entrada aceita somente ISO-8601 explícito ou `%m/%d/%y %I:%M %p`, dentro de 1971-01-01 a 2262-04-10. Datas relativas, timezone desconhecido e gramática inferida são rejeitados com linha/coluna. Inteiros são provados lexicalmente contra `int64`, sem alterar o limite global do Python. Semanas/meses são calculados como datas civis e convertidos depois do clipping, inclusive no limite superior de 2262. Sinal negativo com força abaixo de 0,40 gera coleta/teste; `review/stop` exige força suficiente.

A recência agregada usa a mediana temporal real, não o elemento central superior. O top 3 permanece como síntese, mas `all_recommendations` preserva a fila deduplicada completa; a UI permite detalhar e decidir ações adicionais sem trocar filtros/scores. O CSV exporta a fila integral e cada baseline preserva rank, score, normalização, componentes, hipótese de frequência e ação. Seleções semanal/mensal exportam modo, janela solicitada, janela efetiva e `partial_period` no CSV, HTML e Markdown.

O campo compartilhado `analysis_state` informa `ready` ou `empty_scope`. Se filtros/período formarem uma interseção vazia, o app mantém fonte, controles e histórico, mostra orientação para ajustar o recorte e não exibe KPIs, prioridades nem downloads analíticos. Nos relatórios, ausência de delta aparece como “não definido — sem comparador elegível”; uma diferença zero só aparece quando efetivamente calculada.

Datas de execução ou fim da observação futuras ficam pendentes (`execution_in_future` / `observation_in_future`); o timestamp enviado não pode adiantar o relógio real. Decisão, registro, relógio, execução e janela observada são comparados no calendário civil declarado pela fonte, inclusive `+14:00`, `-12:00` e fonte naive sem offset inventado. A regra vale para novos registros; eventos históricos persistidos não são retroclassificados. Testes injetam relógio controlado após o fim observado. Para uma demonstração sintética/retrospectiva explícita, use banco separado e defina `SOCIAL_COCKPIT_SIMULATION_NOW=2025-01-22T18:00:00+00:00` ao iniciar o comando Streamlit acima. O app exibe **SIMULAÇÃO / REPLAY RETROSPECTIVO**, e eventos persistem essa marca. Remova a variável ao retornar à produção; simulação não autoriza datas futuras em relação ao relógio controlado.

Exemplo de replay: registre a decisão com relógio em `2025-01-14T18:00:00+00:00`; reinicie em `2025-01-22T18:00:00+00:00` e observe a janela 15–21/01. A decisão precisa anteceder a observação também na simulação.

As linhas analíticas conservam a fonte ativa. Cada `decision` conserva fonte, escopo, método, baseline, data `decided_at`, IDs de evento/revisão, estado, textos original/editado/efetivo, responsável e janela. Cada `outcome` conserva a fonte observada, `recorded_at` (momento do registro, não data de execução), declaração de execução, período observado, comparação, cobertura, delta e volumes diários em views/dia. `decision_id` liga a observação à decisão; `decision_source_hash` identifica a fonte do baseline. `non_causal=true` impede interpretar a comparação como efeito causal ou ROI.

As colunas históricas são acrescentadas somente quando há decisões; a exportação estática sem histórico permanece inalterada. O escopo de novos outcomes é persistido com a observação. Outcomes legados sem esse campo exportam escopo vazio, nunca o escopo do upload atual.

Para recompor o CSV, reconstrua primeiro linhas `export_field` pelo ordinal determinístico da linha-base; depois, `analysis_field` e `history_field`. Campos históricos acima de 32.768 caracteres ficam vazios na linha principal e são transportados por linhas `history_field`: agrupe por `decision_id`, `outcome_id` e `field_name`, ordene `field_chunk`, aplique `json.loads` a cada `field_value` e concatene. O resultado é a célula CSV original, incluindo eventual apóstrofo de proteção contra fórmulas; para `baseline`/`observed`/`comparison`, decodifique então o JSON recomposto. Os blocos mantêm leitura no limite padrão do Python. Referências analíticas `source_ref` continuam usando `reference_chunk`/`reference_index`, sem mudança de contrato.

## O que ler

- [Análise e estratégia](./analysis.md)
- [Evidências reproduzíveis](./evidence.csv)
- [SPEC](./SPEC.md)
- [Diário do processo](../../process-log/004-social.md)
- [Fonte canônica, método e qualidade](../../process-log/evidence/004/cockpit-source-quality-proof.png)
- [Fila integral, quarta ação e componentes](../../process-log/evidence/004/cockpit-audience-priority-proof.png)
- [Alvo, benchmark, quartis e amostra](../../process-log/evidence/004/cockpit-priority-context-proof.png)
- [Snapshot histórico e contrato de reenvio pelo mesmo hash](../../process-log/evidence/004/cockpit-history-snapshot-proof.png)
- [SIMULAÇÃO retrospectiva e futuro pendente](../../process-log/evidence/004/cockpit-outcomes-proof.png)

## Limitações

- ERv usa views, não alcance único; audiência é rótulo agregado do post, não engajamento individual.
- Patrocínio é associação observacional. Sem investimento, receita ou conversão, não há ROI financeiro nem causalidade.
- A frequência é hipótese de teste derivada de semanas ISO completas dentro do mesmo mês/contexto, não frequência ótima.
- Atualização é importação manual; não há APIs externas, publicação, contratação ou investimento automático.
