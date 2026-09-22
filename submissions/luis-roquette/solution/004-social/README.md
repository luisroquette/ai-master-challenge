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

Após as correções documentadas em I38–I40, o gate acumulado aprovou **102/102 testes** com warnings tratados como erros. A CLI real foi repetida byte a byte: `evidence.csv` SHA-256 `017588dfa23f032684066c049f2f5aac4a380e5615de029b80e57a29311b3f1e`, `analysis.md` `c65b42f631c3532433683b2cf2cbdcea1be74147cfc86cc38146b13f52859fe6` e HTML `a90d85f64b20e0d2c556cba2bcfda09378e16f07c4507f25927ad0a5f29f7fb1`. O resumo normal e a fixture adversarial permaneceram em uma página A4.

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

O histórico mostra o snapshot mesmo sem CSV. Reenviar o mesmo hash verifica referências pelo escopo salvo, inclusive quando a recomendação não está na fila ativa ou os filtros mudaram. `METHOD_VERSION = "2.0.0"` é o contrato ativo. Eventos `1.0.0` continuam legíveis, mas são incompatíveis para nova comparação automática e ficam `pending / method_mismatch`.

Datas de execução ou fim da observação futuras ficam pendentes (`execution_in_future` / `observation_in_future`); o timestamp enviado não pode adiantar o relógio real. Testes injetam relógio controlado após o fim observado. Para uma demonstração sintética/retrospectiva explícita, use banco separado e defina `SOCIAL_COCKPIT_SIMULATION_NOW=2025-01-22T18:00:00+00:00` ao iniciar o comando Streamlit acima. O app exibe **SIMULAÇÃO / REPLAY RETROSPECTIVO**, e eventos persistem essa marca. Remova a variável ao retornar à produção; simulação não autoriza datas futuras em relação ao relógio controlado.

Exemplo de replay: registre a decisão com relógio em `2025-01-14T18:00:00+00:00`; reinicie em `2025-01-22T18:00:00+00:00` e observe a janela 15–21/01. A decisão precisa anteceder a observação também na simulação.

As linhas analíticas conservam a fonte ativa. Cada `decision` conserva fonte, escopo, método, baseline, data `decided_at`, IDs de evento/revisão, estado, textos original/editado/efetivo, responsável e janela. Cada `outcome` conserva a fonte observada, `recorded_at` (momento do registro, não data de execução), declaração de execução, período observado, comparação, cobertura, delta e volumes diários em views/dia. `decision_id` liga a observação à decisão; `decision_source_hash` identifica a fonte do baseline. `non_causal=true` impede interpretar a comparação como efeito causal ou ROI.

As colunas históricas são acrescentadas somente quando há decisões; a exportação estática sem histórico permanece inalterada. O escopo de novos outcomes é persistido com a observação. Outcomes legados sem esse campo exportam escopo vazio, nunca o escopo do upload atual.

Campos históricos acima de 32.768 caracteres ficam vazios na linha principal e são transportados por linhas `history_field`: agrupe por `decision_id`, `outcome_id` e `field_name`, ordene `field_chunk`, aplique `json.loads` a cada `field_value` e concatene. O resultado é a célula CSV original, incluindo eventual apóstrofo de proteção contra fórmulas; para `baseline`/`observed`/`comparison`, decodifique então o JSON recomposto. Os blocos mantêm leitura no limite padrão do Python. Referências analíticas `source_ref` continuam usando `reference_chunk`/`reference_index`, sem mudança de contrato.

## O que ler

- [Análise e estratégia](./analysis.md)
- [Evidências reproduzíveis](./evidence.csv)
- [SPEC](./SPEC.md)
- [Diário do processo](../../process-log/004-social.md)
- [Fonte canônica, método e qualidade](../../process-log/evidence/004/cockpit-source-quality-proof.png)
- [Audiência condicionada e prioridade](../../process-log/evidence/004/cockpit-audience-priority-proof.png)
- [Alvo, benchmark, quartis e amostra](../../process-log/evidence/004/cockpit-priority-context-proof.png)
- [Snapshot histórico e contrato de reenvio pelo mesmo hash](../../process-log/evidence/004/cockpit-history-snapshot-proof.png)
- [SIMULAÇÃO retrospectiva e futuro pendente](../../process-log/evidence/004/cockpit-outcomes-proof.png)

## Limitações

- ERv usa views, não alcance único; audiência é rótulo agregado do post, não engajamento individual.
- Patrocínio é associação observacional. Sem investimento, receita ou conversão, não há ROI financeiro nem causalidade.
- A frequência é hipótese de teste derivada de semanas ISO completas dentro do mesmo mês/contexto, não frequência ótima.
- Atualização é importação manual; não há APIs externas, publicação, contratação ou investimento automático.
