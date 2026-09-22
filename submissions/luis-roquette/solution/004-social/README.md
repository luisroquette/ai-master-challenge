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

Após as correções documentadas até I31, o gate limpo aprovou 62/62 testes em 17,407 s (18,27 s totais), com warnings tratados como erros. A CLI processou as 52.214 linhas em 23,08 s, com pico residente de 558.514.176 bytes e zero swap; CSV e Markdown foram idênticos byte a byte aos artefatos publicados. O resumo impresso permaneceu em uma página A4.

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
