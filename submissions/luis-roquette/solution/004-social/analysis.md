# Estratégia Social Media — Challenge 004

## Decisão para segunda-feira

Fila única: as recomendações abaixo vêm de `result[recommendations]`, na mesma ordem do HTML e do CSV. São propostas para decisão humana; não executam gasto, publicação ou interrupção.

1. Bilibili / mixed / tech / 100,000–499,999: Executar teste controlado e reavaliar; patrocínio depende de custos reais. Prioridade 4.56797e-09; impacto 0.0498253; força 0.3; atualidade 3.05599e-09; ΔERv +0.130877 p.p.; data representativa 2024-11-11T21:32:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-16ea8aa86ed6ce32
2. Instagram / text / tech / 500,000+: Executar teste controlado e reavaliar; patrocínio depende de custos reais. Prioridade 3.95029e-11; impacto 0.0989732; força 0.45; atualidade 8.86949e-12; ΔERv +0.0855155 p.p.; data representativa 2024-09-13T22:58:30. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-79c48fa46f3b3f67
3. YouTube / video / beauty / 50,000–99,999: Executar teste controlado e reavaliar; patrocínio depende de custos reais. Prioridade 5.07978e-12; impacto 0.0634691; força 0.44; atualidade 1.81899e-12; ΔERv +0.0255073 p.p.; data representativa 2024-08-28T04:28:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-4bd4e28ee9e3b1fc

Atualidade = 2^(−idade em dias/7), ancorada na data de referência do dataset. Em grupos agregados, a data representativa é a mediana das datas do grupo-alvo (posts patrocinados na comparação de patrocínio). Um escopo de dois anos pode produzir scores muito pequenos: isso preserva a regra de recência e não demonstra uma oportunidade atual. A ordem é prioridade decrescente, |ΔERv| decrescente, data representativa decrescente e evidence_id crescente, após deduplicação contextual.

Força limitada (<0,40) exige coleta/teste, sem ampliação de investimento. As janelas de execução/revisão são propostas futuras, não datas de performance observada.

## O que os dados permitem afirmar

Escopo: 2023-05-29T00:00:00 a 2025-05-28T23:59:59.999999; referência: 2025-05-28T11:08:00; filtros: `{}`.

52214 posts; 5000 creators; 527376193 views; 104966242 interações. Mediana ERv: 19.8992%; ERv ponderado: 19.9035%. Proporção de posts com zero interação: 0; taxas indefinidas: 0. Evidência: `summary-6c93d64bb97724fa`.

ERv = 100 × (likes + shares + comments_count) / views; views=0 deixa a taxa indefinida e preserva volume. A mediana usa taxas por post; a taxa ponderada usa totais apenas onde views>0. Views não são alcance único; interações não são pessoas únicas.

## Plataforma, conteúdo, categoria, creators, audiência e tempo

As tabelas descrevem cada recorte; não criam uma segunda fila de prioridades. Diferenças pequenas de taxa, sem comparação controlada, não justificam redistribuir o mix. Idade, gênero e localização são rótulos de posts, não percentuais ou personas. Estas marginais não identificam qual público vence dentro de cada combinação plataforma/formato/categoria: essa pergunta exige filtros comparáveis e amostra suficiente no motor. Bilibili e RedNote permanecem no escopo junto a Instagram, TikTok e YouTube.

### Plataforma

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Bilibili | 10598 | 4540 | 107039049 | 21307767 | 19.9046 | `dimension-e026b6bfbfe3d1b3` |
| Instagram | 10423 | 4510 | 105275939 | 20946950 | 19.889 | `dimension-6eccbbcf35e00dbe` |
| RedNote | 10402 | 4514 | 105068336 | 20916853 | 19.901 | `dimension-6a4ff42c20775f39` |
| TikTok | 10296 | 4494 | 103995686 | 20699400 | 19.9019 | `dimension-858afe9cefe3af85` |
| YouTube | 10495 | 4540 | 105997183 | 21095272 | 19.9001 | `dimension-fa6ec5f09b73c9a5` |

### Formato

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| image | 10303 | 4475 | 104071566 | 20712300 | 19.9007 | `dimension-42ce93794522edb9` |
| mixed | 5213 | 3327 | 52652595 | 10484160 | 19.9038 | `dimension-8bc9ffc9412a981e` |
| text | 5198 | 3329 | 52490501 | 10452520 | 19.9122 | `dimension-7630e3ba82eaf9c7` |
| video | 31500 | 4999 | 318161531 | 63317262 | 19.8955 | `dimension-c0c665ae984b3dc0` |

### Categoria

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| beauty | 21023 | 4977 | 212331201 | 42261477 | 19.8996 | `dimension-0de1ed4ecf6c2101` |
| lifestyle | 20761 | 4969 | 209686263 | 41740052 | 19.9013 | `dimension-3d248b83fca7dba4` |
| tech | 10430 | 4523 | 105358729 | 20964713 | 19.8954 | `dimension-0d8b78c17d80b337` |

### Faixa de seguidores

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 0–9,999 | 454 | 436 | 4581119 | 911451 | 19.8765 | `dimension-e2f23f833d85ba1b` |
| 10,000–49,999 | 2110 | 1758 | 21313743 | 4243070 | 19.9009 | `dimension-59a905415c3c4ba8` |
| 100,000–499,999 | 21025 | 4982 | 212345820 | 42266183 | 19.904 | `dimension-54a808a7ed67ed4c` |
| 50,000–99,999 | 2596 | 2091 | 26215136 | 5219513 | 19.91 | `dimension-c3bf54192981b458` |
| 500,000+ | 26029 | 4994 | 262920375 | 52326025 | 19.8936 | `dimension-ba554894e5fd643c` |

### Idade

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 13-18 | 7852 | 4056 | 79321127 | 15782684 | 19.8956 | `dimension-97811d82c6713d8e` |
| 19-25 | 18276 | 4947 | 184595589 | 36749614 | 19.9009 | `dimension-1a2946a769307ac5` |
| 26-35 | 15700 | 4866 | 158563615 | 31557172 | 19.9001 | `dimension-809dabeff0675e8b` |
| 36-50 | 7736 | 4072 | 78130652 | 15547930 | 19.8989 | `dimension-1630ec374e62cb6d` |
| 50+ | 2650 | 2073 | 26765210 | 5328842 | 19.8989 | `dimension-7816aaed372d522b` |

### Gênero

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| female | 20743 | 4979 | 209503458 | 41698343 | 19.8944 | `dimension-eccf69932cfd21b3` |
| male | 20987 | 4977 | 211972319 | 42190194 | 19.9003 | `dimension-2a2cc6fe1648bc47` |
| non-binary | 5249 | 3353 | 53019133 | 10552457 | 19.9067 | `dimension-345f893059ca62e2` |
| unknown | 5235 | 3364 | 52881283 | 10525248 | 19.905 | `dimension-9b822635bf2c2e49` |

### Localização

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Brazil | 6505 | 3724 | 65693721 | 13079528 | 19.9015 | `dimension-7eb2655bd408b127` |
| China | 6648 | 3818 | 67156444 | 13367265 | 19.9036 | `dimension-986560b278af61a8` |
| Germany | 6497 | 3734 | 65632058 | 13058763 | 19.8976 | `dimension-0c537f49ce576150` |
| India | 6484 | 3780 | 65500057 | 13029391 | 19.8872 | `dimension-d6626844f1f30d18` |
| Japan | 6553 | 3738 | 66182343 | 13172600 | 19.8964 | `dimension-ea5233f1bf36b6cd` |
| Russia | 6459 | 3757 | 65229927 | 12982754 | 19.8982 | `dimension-5f2b28087d1b8df1` |
| UK | 6570 | 3796 | 66354996 | 13213549 | 19.9048 | `dimension-74ce2305331fb1af` |
| USA | 6498 | 3726 | 65626647 | 13062392 | 19.9035 | `dimension-990802eba75cae6a` |

### Mês

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 2023-05 | 188 | 187 | 1898818 | 377813 | 19.8931 | `dimension-55b56deacab0b814` |
| 2023-06 | 2241 | 1811 | 22636496 | 4505008 | 19.8951 | `dimension-27e52c263baf338b` |
| 2023-07 | 2221 | 1831 | 22425828 | 4465405 | 19.9107 | `dimension-58433a9a49a5168c` |
| 2023-08 | 2233 | 1837 | 22555419 | 4486031 | 19.8795 | `dimension-5979f365cfd396fa` |
| 2023-09 | 2092 | 1741 | 21132335 | 4207344 | 19.913 | `dimension-3a477c1a31c00eb5` |
| 2023-10 | 2186 | 1812 | 22078142 | 4393121 | 19.8941 | `dimension-97fb17d147ef0eab` |
| 2023-11 | 2168 | 1808 | 21897271 | 4359592 | 19.9102 | `dimension-f85609596f990454` |
| 2023-12 | 2177 | 1801 | 21982940 | 4377864 | 19.9073 | `dimension-5faf27ec44e3d947` |
| 2024-01 | 2192 | 1804 | 22140371 | 4408052 | 19.9032 | `dimension-c519c00ee20c7abe` |
| 2024-02 | 2099 | 1737 | 21199664 | 4218973 | 19.8981 | `dimension-70f7065fab236caa` |
| 2024-03 | 2210 | 1792 | 22322168 | 4442533 | 19.8918 | `dimension-e77e61cdf7cc6368` |
| 2024-04 | 2121 | 1761 | 21425517 | 4261036 | 19.8774 | `dimension-dcd915ab6a174675` |
| 2024-05 | 2195 | 1820 | 22167277 | 4413864 | 19.9028 | `dimension-b10d3f3bb024974f` |
| 2024-06 | 2165 | 1786 | 21866512 | 4352679 | 19.906 | `dimension-8ab0184b3545b35e` |
| 2024-07 | 2229 | 1820 | 22519508 | 4481034 | 19.8965 | `dimension-c56258d304fe2bc9` |
| 2024-08 | 2347 | 1916 | 23702162 | 4719291 | 19.911 | `dimension-04c6ffcf358e2c19` |
| 2024-09 | 2139 | 1741 | 21607668 | 4299942 | 19.8955 | `dimension-c7ac880048918482` |
| 2024-10 | 2212 | 1833 | 22348182 | 4444786 | 19.8886 | `dimension-4ab15e81c77b63b6` |
| 2024-11 | 2151 | 1790 | 21724203 | 4325675 | 19.8963 | `dimension-dd1ea5b900646c36` |
| 2024-12 | 2228 | 1862 | 22500047 | 4480727 | 19.9155 | `dimension-c6ed5d8b983d9f4b` |
| 2025-01 | 2146 | 1773 | 21672074 | 4314145 | 19.8876 | `dimension-5bbfff19853beee9` |
| 2025-02 | 1914 | 1601 | 19332056 | 3848371 | 19.8969 | `dimension-236fa4e3197e6ded` |
| 2025-03 | 2213 | 1813 | 22351748 | 4444840 | 19.8846 | `dimension-359df8b2ee737026` |
| 2025-04 | 2173 | 1807 | 21954870 | 4369314 | 19.901 | `dimension-39b356ba3d22a3fb` |
| 2025-05 | 1974 | 1626 | 19934917 | 3968802 | 19.9019 | `dimension-41d6443fe88dc140` |

## Patrocínio e o que não funciona

137 estratos elegíveis; 162 sem amostra/contraparte suficiente; cobertura de 93.7909% dos posts. Evidência: `sponsorship-overview-8f28cf7c82d0369d`.

Controle: mesma plataforma, formato, categoria, faixa de creator e período. Cada braço exige 30 taxas definidas e cinco creators; o efeito é a diferença entre medianas das medianas de ERv por creator. Patrocínio é associação observacional, não causalidade. Custo implícito e retorno financeiro não podem ser calculados: faltam investimento, custo de produção, receita/conversão. Nenhum threshold de seguidores justifica desembolso sozinho.

Menor associação de ERv: TikTok / video / lifestyle / 10,000–49,999; ΔERv -0.262464 p.p.; força 0.41; orgânicos/patrocinados: 52/42 posts, 525074/424018 views, 105270/83981 interações. Evidência: `sponsorship-6ee8d64c66ca1aa4`.

Maior associação de ERv: YouTube / mixed / beauty / 500,000+; ΔERv +0.212889 p.p.; força 0.77; orgânicos/patrocinados: 114/79 posts, 1152525/797935 views, 228438/159479 interações. Evidência: `sponsorship-586a8f3868ac1b32`.

Esses extremos são achados descritivos, não prioridades adicionais nem ordens para suspender renovação. Sinal negativo isolado ou força insuficiente exige investigação; interromper investimento requer sinais concordantes, evidência forte e decisão humana. Ausência de zeros observados, quando indicada acima, limita a avaliação do fracasso: não prova inexistência de posts sem engajamento.

## Estratégia operacional e quick wins

Responsável sugerido: Gestor de Social Media. Executar nos próximos 7 dias; revisar 7 dias após cada teste. A estratégia abaixo aplica a fila inicial, sem reordená-la.

| Tema | Ação | Critério de revisão |
|---|---|---|
| Esforço e quick win | Preparar briefs dos contextos da fila na ordem exibida; anexar a evidência e registrar aceitar/rejeitar/editar. | Rever ERv, views e interações por post no mesmo contexto. |
| Público e creators | Preservar rótulos de audiência e faixa de creator do contexto; coletar se faltarem controles. Não inferir uma persona ou threshold de contratação. | Pelo menos 30 taxas e cinco creators por braço; declarar composição e concentração. |
| Frequência | Testar uma cadência por vez; este relatório não estima uma frequência ótima. | Janelas equivalentes e pelo menos duas semanas completas antes de propor frequência observada. |
| Patrocínio | Obter custos reais antes de avaliar desembolso; força limitada pede coleta/teste. | ERv e volume concordantes, grupo comparável e dados financeiros. |
| Parar/revisar | Revisar repetição de padrões negativos; não parar por média global ou sinal isolado. | Interrupção exige a guarda do motor e decisão humana; sem base, coletar. |

## Auditabilidade e limites

Fonte SHA-256: `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `1.0.0`. Cada evidência está em [evidence.csv](./evidence.csv), com escopo, fórmula e referências.

Regeração conjunta: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html --report analysis.md`.

Linhas `recommendation` preservam `rank`, score, impacto, força, atualidade, valores originais V/I/F, denominadores P95, diferença, data representativa, ação, responsável e janelas. Impacto = média de min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1); prioridade = 100 × impacto × força × atualidade. Scores são relativos à plataforma/tipo/unidade, não monetários. P95=0 usa máximo positivo ou zero se inexistente.

Em `source_ref`, `source_row_id` e `source_line` são arrays JSON de mesmo tamanho e ordem: o par de índice i identifica o ID opaco e a primeira linha física (base 1) do registro. Reconstituir a chave completa com `source_hash + ':' + source_row_id[i]`. Campos multilinha contam todas as linhas físicas; células de texto neutralizam fórmulas de planilha.

A CLI publica todo o histórico, sem alertas post a post. Ausência de período anterior igualmente longo pode impedir comparações editoriais; não se inventa tendência. O monitoramento recente pode produzir outra fila porque tem outro escopo. Não há unidade confirmada de content_length, causalidade, ROI ou resultados futuros inferidos.
