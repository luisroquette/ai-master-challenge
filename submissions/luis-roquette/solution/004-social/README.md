# Cockpit de Social Media — Challenge 004

Aplicação local que valida o CSV do desafio, produz análise contextual reproduzível, prioriza ações, registra decisões humanas em SQLite e exporta o mesmo resultado em HTML e CSV.

## Instalação

Requisitos testados em 21/09/2026: Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3 e SQLite 3.50.4.

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

Após a correção documentada em I28, o gate limpo aprovou 58/58 testes em 9,243 s (9,81 s totais), com warnings tratados como erros. A CLI processou as 52.214 linhas em 16,69 s, com pico residente de 557.023.232 bytes e zero swap; os arquivos gerados foram idênticos aos artefatos publicados.

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

## O que ler

- [Análise e estratégia](./analysis.md)
- [Evidências reproduzíveis](./evidence.csv)
- [SPEC](./SPEC.md)
- [Diário do processo](../../process-log/004-social.md)
- [Screenshot do cockpit](../../process-log/evidence/004/cockpit-proof.png)

## Limitações

- ERv usa views, não alcance único; audiência é rótulo agregado do post, não engajamento individual.
- Patrocínio é associação observacional. Sem investimento, receita ou conversão, não há ROI financeiro nem causalidade.
- A frequência é hipótese de teste derivada de semanas observadas, não frequência ótima.
- Atualização é importação manual; não há APIs externas, publicação, contratação ou investimento automático.
