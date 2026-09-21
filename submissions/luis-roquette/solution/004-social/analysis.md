# Estratégia Social Media — Challenge 004

## Decisão para segunda-feira

1. **Não redistribuir orçamento por média de plataforma ou formato.** As medianas de ERv são quase planas: 19,889%–19,905% entre plataformas e 19,895%–19,912% entre formatos. Tratar “vídeo vence imagem” como hipótese não sustentada neste snapshot. Evidências: `dimension-6eccbbcf35e00dbe`, `dimension-e026b6bfbfe3d1b3`, `dimension-c0c665ae984b3dc0`, `dimension-7630e3ba82eaf9c7`.
2. **Testar patrocínio apenas em células controladas e com custos anexados antes da decisão financeira.** Priorizar dois testes pequenos: YouTube/mixed/beauty/500.000+ (+0,213 p.p.; força 0,77; 114 orgânicos e 79 patrocinados) e TikTok/image/tech/100.000–499.999 (+0,206 p.p.; força 0,80; 85 e 81 posts). Evidências: `sponsorship-586a8f3868ac1b32`, `sponsorship-072f5cb006c11a93`.
3. **Suspender renovação automática na célula negativa mais clara e reavaliar criativo/fit.** TikTok/video/lifestyle/10.000–49.999 teve associação de −0,262 p.p., força 0,41, com 52 posts orgânicos e 42 patrocinados. Isso não prova que patrocínio causou a queda. Evidência: `sponsorship-6ee8d64c66ca1aa4`.

**Responsável:** Gestor de Social Media. **Execução:** próximos 7 dias. **Revisão:** 7 dias após cada teste, comparando ERv, views e interações por post no mesmo contexto. O Head aprova gasto somente após incluir investimento, custo de produção e valor de conversão.

## O que os dados permitem afirmar

O arquivo contém 52.214 posts de 5.000 creators, de 29/05/2023 a 28/05/2025. A mediana global de ERv é 19,899%; o ERv ponderado é 19,903%; há 527.376.193 views e 104.966.242 interações. ERv = `100 × (likes + shares + comments_count) / views`. Evidência: `summary-6c93d64bb97724fa`.

### Plataforma, conteúdo e categoria

- Bilibili tem a maior mediana por plataforma, 19,905%, e Instagram a menor, 19,889%: diferença de apenas 0,016 p.p. Evidências: `dimension-e026b6bfbfe3d1b3`, `dimension-6eccbbcf35e00dbe`.
- Texto tem a maior mediana por formato, 19,912%, e vídeo a menor, 19,895%: diferença de 0,017 p.p. Texto tem 5.198 posts; vídeo, 31.500. A taxa isolada não justifica trocar todo o mix. Evidências: `dimension-7630e3ba82eaf9c7`, `dimension-c0c665ae984b3dc0`.
- Lifestyle, beauty e tech ficam entre 19,895% e 19,901% de mediana. Não há categoria universalmente vencedora; decisões devem usar o contexto combinado. Evidências: `dimension-3d248b83fca7dba4`, `dimension-0de1ed4ecf6c2101`, `dimension-0d8b78c17d80b337`.

### Tamanho de creator e audiência

- A faixa 50.000–99.999 tem a maior mediana, 19,910%, mas só 2.596 posts; 0–9.999 tem 19,877% em 454 posts. A diferença de 0,033 p.p. não sustenta um threshold universal de contratação. Evidências: `dimension-c3bf54192981b458`, `dimension-e2f23f833d85ba1b`.
- Idade varia de 19,896% (13–18) a 19,901% (19–25); gênero, de 19,894% (female) a 19,907% (non-binary); localização, de 19,887% (India) a 19,905% (UK). São rótulos categóricos do post, não percentuais nem personas individuais. Evidências: `dimension-97811d82c6713d8e`, `dimension-1a2946a769307ac5`, `dimension-eccf69932cfd21b3`, `dimension-345f893059ca62e2`, `dimension-d6626844f1f30d18`, `dimension-74ce2305331fb1af`.

### Tempo e o que não funciona

- As medianas mensais variam de 19,877% em 2024-04 a 19,916% em 2024-12. A amplitude de 0,038 p.p. não autoriza atribuir tendência, sazonalidade ou efeito de calendário sem teste. Evidências: `dimension-dcd915ab6a174675`, `dimension-c6ed5d8b983d9f4b`.
- O snapshot não contém posts com zero interação e não representa esse risco operacional; arquivos futuros aceitam zeros sem convertê-los em ausência. Evidência: `summary-6c93d64bb97724fa`.
- O pior sinal patrocinado observado é a célula TikTok/video/lifestyle/10.000–49.999 já indicada para revisão. Evitar a leitura superficial de médias globais ou de “alcance alto” sem taxa, volume, amostra e controles. Evidência: `sponsorship-6ee8d64c66ca1aa4`.

## Patrocínio: resposta honesta

Há 137 estratos elegíveis e 162 não elegíveis; 93,79% dos posts pertencem a estratos com os dois braços, mínimo de 30 taxas e cinco creators por braço. O controle fixa plataforma, formato, categoria, faixa de creator e período; o efeito é a diferença entre medianas de ERv por creator. Evidência: `sponsorship-overview-8f28cf7c82d0369d`.

Patrocínio apresenta associações positivas e negativas conforme o contexto. Portanto, a resposta é **“testar seletivamente”**, não “sempre patrocinar” nem “nunca patrocinar”. Mesmo os melhores sinais não são ROI: o arquivo não contém investimento, custo de produção, receita ou conversão. A decisão financeira fica pendente até esses campos existirem.

## Estratégia operacional

| Tema | Ação | Critério de revisão |
|---|---|---|
| Esforço | Manter distribuição-base entre plataformas; concentrar o próximo aprendizado nas duas células patrocinadas positivas citadas. | Escalar só se ERv e volume por post se mantiverem no grupo comparável. |
| Público | Preservar idade, gênero e localização observados como controles; não criar persona a partir dos rótulos. | Amostra mínima permanece 30 taxas e 5 creators por braço. |
| Frequência | Testar uma cadência por vez no mesmo creator/contexto; frequência ótima não é identificável neste snapshot. | Comparar janelas equivalentes por 7 dias; não usar volume bruto entre janelas desiguais. |
| Creators | Selecionar por contexto e ERv histórico com volume, não só seguidores; 50.000–99.999 é hipótese, não regra. | Exigir grupo comparável e custos reais antes de contratação. |
| Parar/revisar | Pausar renovação automática da célula negativa TikTok/video/lifestyle/10.000–49.999. | Retomar apenas após novo criativo/teste controlado e leitura conjunta de taxa e volume. |

## Quick wins desta semana

1. Criar briefs separados para os dois testes positivos, mantendo plataforma, formato, categoria e faixa de creator constantes (`sponsorship-586a8f3868ac1b32`; `sponsorship-072f5cb006c11a93`).
2. Abrir uma revisão do segmento negativo e registrar a decisão humana, sem alterar calendário ou orçamento automaticamente (`sponsorship-6ee8d64c66ca1aa4`).
3. Adicionar investimento, custo de produção e valor de conversão ao próximo snapshot; até lá, comunicar associação observacional, nunca ROI (`sponsorship-overview-8f28cf7c82d0369d`).

## Auditabilidade e limites

- Fonte SHA-256: `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `1.0.0`. Cada ID acima possui filtro, fórmula, amostra e IDs de origem em [`evidence.csv`](./evidence.csv).
- Regeração: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html`.
- O CSV de evidência neutraliza células iniciadas por `=`, `+`, `-`, `@`, tab ou retorno. Os IDs de origem ficam agrupados por evidência para evitar duplicação, com o hash da fonte em coluna própria.
- Não há causalidade, ROI, alcance único, percentuais demográficos individuais ou unidade confiável de duração inferidos. Bilibili e RedNote permanecem na análise, apesar do foco executivo do briefing em Instagram, TikTok e YouTube.
