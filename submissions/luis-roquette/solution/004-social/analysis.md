# Estratégia Social Media — Challenge 004

## Decisão para segunda-feira

Fila única: as recomendações abaixo vêm de `result[recommendations]`, na mesma ordem do HTML e do CSV. São propostas para decisão humana; não executam gasto, publicação ou interrupção.

1. YouTube / video / lifestyle / 500,000+ / 2025-04: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 0.424558; impacto 1; força 0.3; atualidade 0.0141519; ΔERv +0.0270584 p.p.; data representativa 2025-04-15T19:41:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-c514404c97b43cfb. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2025-04; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 18 creator-semanas, 18 creators; 3 semanas completas disponíveis, 3 semanas observadas; janela 2025-04-07T00:00:00 a 2025-04-27T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.
2. RedNote / video / beauty / 500,000+ / 2025-03: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 0.0190582; impacto 1; força 0.29; atualidade 0.000657178; ΔERv -0.0628742 p.p.; data representativa 2025-03-15T02:43:30. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-8ad62bd48c58837c. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2025-03; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 27 creator-semanas, 27 creators; 4 semanas completas disponíveis, 4 semanas observadas; janela 2025-03-03T00:00:00 a 2025-03-30T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.
3. YouTube / video / beauty / 500,000+ / 2024-12: Testar o padrão em escala limitada e coletar evidência antes de ampliar esforço ou investimento. Prioridade 2.93375e-06; impacto 1; força 0.3; atualidade 9.77916e-08; ΔERv +0.111229 p.p.; data representativa 2024-12-16T02:14:00. Responsável: Gestor de Social Media; execução: próximos 7 dias; revisão: 7 dias após o teste; métrica: ERv, views e interações por post. Evidência: sponsorship-342a5cae1a28de2d. Frequência: Testar 1 posts por creator por semana ISO completa; status test; unidade posts_per_creator_per_complete_iso_week; mês 2024-12; regra complete_iso_weeks_within_calendar_month_and_scope; método median_observed_posts_per_creator_week; 28 creator-semanas, 28 creators; 4 semanas completas disponíveis, 4 semanas observadas; janela 2024-12-02T00:00:00 a 2024-12-29T00:00:00; ação test_observed_cadence; mínimo de 2 semanas completas observadas. Limite: frequência observada é hipótese de teste, não efeito causal; ausência de linha não equivale a zero.

Atualidade = 2^(−idade em dias/7), ancorada na data de referência do dataset. Em grupos agregados, a data representativa é a mediana das datas do grupo-alvo (posts patrocinados na comparação de patrocínio). Um escopo de dois anos pode produzir scores muito pequenos: isso preserva a regra de recência e não demonstra uma oportunidade atual. A ordem é prioridade decrescente, |ΔERv| decrescente, data representativa decrescente e evidence_id crescente, após deduplicação contextual.

Força limitada (<0,40) exige coleta/teste, sem ampliação de investimento. As janelas de execução/revisão são propostas futuras, não datas de performance observada.

## O que os dados permitem afirmar

Método 2.0.0. Escopo efetivo: 2023-05-29T00:00:00 a 2025-05-28T00:00:00; referência 2025-05-28T11:08:00; filtros {}. 52214 posts-alvo de 52214 linhas na fonte.

Cobertura parcial: patrocínio 1.56% dos posts, 12 estratos elegíveis, 5216 insuficientes. Benchmarks: 0 níveis tentados; 0 alvos sem referência elegível; alertas post a post desativados. 0 avisos de qualidade; detalhes e motivos completos no CSV.


### Decisões recentes desta fonte

- Nenhuma decisão registrada nesta fonte.

52214 posts; 5000 creators; 527376193 views; 104966242 interações. Mediana ERv: 19.8992%; ERv ponderado: 19.9035%. Proporção de posts com zero interação: 0; taxas indefinidas: 0. Evidência: `summary-619e864d4e9f819f`.

ERv = 100 × (likes + shares + comments_count) / views; views=0 deixa a taxa indefinida e preserva volume. A mediana usa taxas por post; a taxa ponderada usa totais apenas onde views>0. Views não são alcance único; interações não são pessoas únicas.

## Plataforma, conteúdo, categoria, creators, audiência e tempo

As tabelas descrevem cada recorte; não criam uma segunda fila de prioridades. Diferenças pequenas de taxa, sem comparação controlada, não justificam redistribuir o mix. Idade, gênero e localização são rótulos de posts, não percentuais ou personas. Estas marginais não identificam vencedores: a análise condicionada e sua cobertura aparecem abaixo. Bilibili e RedNote permanecem no escopo junto a Instagram, TikTok e YouTube.

### Plataforma

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Bilibili | 10598 | 4540 | 107039049 | 21307767 | 19.9046 | `dimension-dfdbe8f26a25e8ad` |
| Instagram | 10423 | 4510 | 105275939 | 20946950 | 19.889 | `dimension-6f6fb073ab0edf3d` |
| RedNote | 10402 | 4514 | 105068336 | 20916853 | 19.901 | `dimension-bce38d91944bb434` |
| TikTok | 10296 | 4494 | 103995686 | 20699400 | 19.9019 | `dimension-32b7df377a05ce92` |
| YouTube | 10495 | 4540 | 105997183 | 21095272 | 19.9001 | `dimension-cf0f9d161adffee0` |

### Formato

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| image | 10303 | 4475 | 104071566 | 20712300 | 19.9007 | `dimension-9d08a1a7f5403c60` |
| mixed | 5213 | 3327 | 52652595 | 10484160 | 19.9038 | `dimension-bcd27923742b01b4` |
| text | 5198 | 3329 | 52490501 | 10452520 | 19.9122 | `dimension-e4cc141e6e16b819` |
| video | 31500 | 4999 | 318161531 | 63317262 | 19.8955 | `dimension-0072f9cb4fc83189` |

### Categoria

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| beauty | 21023 | 4977 | 212331201 | 42261477 | 19.8996 | `dimension-51b473bd76912e3a` |
| lifestyle | 20761 | 4969 | 209686263 | 41740052 | 19.9013 | `dimension-d27697621f4bed88` |
| tech | 10430 | 4523 | 105358729 | 20964713 | 19.8954 | `dimension-05e83004d74321ca` |

### Faixa de seguidores

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 0–9,999 | 454 | 436 | 4581119 | 911451 | 19.8765 | `dimension-6e62279ca28ddfbf` |
| 10,000–49,999 | 2110 | 1758 | 21313743 | 4243070 | 19.9009 | `dimension-dc7ee449463ae967` |
| 100,000–499,999 | 21025 | 4982 | 212345820 | 42266183 | 19.904 | `dimension-c408a604f52e953b` |
| 50,000–99,999 | 2596 | 2091 | 26215136 | 5219513 | 19.91 | `dimension-4ad00cf22b2475ae` |
| 500,000+ | 26029 | 4994 | 262920375 | 52326025 | 19.8936 | `dimension-6aae6c0e6cd3f0a7` |

### Idade

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 13-18 | 7852 | 4056 | 79321127 | 15782684 | 19.8956 | `dimension-06328611c14de21d` |
| 19-25 | 18276 | 4947 | 184595589 | 36749614 | 19.9009 | `dimension-12940c2a84774eb9` |
| 26-35 | 15700 | 4866 | 158563615 | 31557172 | 19.9001 | `dimension-dbe33fcf382f4466` |
| 36-50 | 7736 | 4072 | 78130652 | 15547930 | 19.8989 | `dimension-e085317c4cdc9255` |
| 50+ | 2650 | 2073 | 26765210 | 5328842 | 19.8989 | `dimension-561a01943c5cc79b` |

### Gênero

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| female | 20743 | 4979 | 209503458 | 41698343 | 19.8944 | `dimension-6caed776a1006a21` |
| male | 20987 | 4977 | 211972319 | 42190194 | 19.9003 | `dimension-3ebce2f61129282c` |
| non-binary | 5249 | 3353 | 53019133 | 10552457 | 19.9067 | `dimension-63c3a48dd9f0eed3` |
| unknown | 5235 | 3364 | 52881283 | 10525248 | 19.905 | `dimension-9053eeb3a1d9c38c` |

### Localização

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| Brazil | 6505 | 3724 | 65693721 | 13079528 | 19.9015 | `dimension-cd3c275257f6b05a` |
| China | 6648 | 3818 | 67156444 | 13367265 | 19.9036 | `dimension-0ed36b5ad811a208` |
| Germany | 6497 | 3734 | 65632058 | 13058763 | 19.8976 | `dimension-78ed902691d8c076` |
| India | 6484 | 3780 | 65500057 | 13029391 | 19.8872 | `dimension-eb7df3692cbdff5d` |
| Japan | 6553 | 3738 | 66182343 | 13172600 | 19.8964 | `dimension-a5b13ab2fc68ff09` |
| Russia | 6459 | 3757 | 65229927 | 12982754 | 19.8982 | `dimension-f5e13b7594d6ada4` |
| UK | 6570 | 3796 | 66354996 | 13213549 | 19.9048 | `dimension-a1cec99442632e67` |
| USA | 6498 | 3726 | 65626647 | 13062392 | 19.9035 | `dimension-af53e138070b3a9d` |

### Mês

| Recorte | Posts | Creators | Views | Interações | Mediana ERv (%) | Evidência |
|---|---:|---:|---:|---:|---:|---|
| 2023-05 | 188 | 187 | 1898818 | 377813 | 19.8931 | `dimension-b5d32dcd7622953d` |
| 2023-06 | 2241 | 1811 | 22636496 | 4505008 | 19.8951 | `dimension-e3ba1edcdd1dbb9f` |
| 2023-07 | 2221 | 1831 | 22425828 | 4465405 | 19.9107 | `dimension-54803315249cbcc9` |
| 2023-08 | 2233 | 1837 | 22555419 | 4486031 | 19.8795 | `dimension-52fe2e9597250874` |
| 2023-09 | 2092 | 1741 | 21132335 | 4207344 | 19.913 | `dimension-486aed51e7dac4ca` |
| 2023-10 | 2186 | 1812 | 22078142 | 4393121 | 19.8941 | `dimension-068a2dfa57be9706` |
| 2023-11 | 2168 | 1808 | 21897271 | 4359592 | 19.9102 | `dimension-e61a32fe1fcd9a03` |
| 2023-12 | 2177 | 1801 | 21982940 | 4377864 | 19.9073 | `dimension-9669c0863553a795` |
| 2024-01 | 2192 | 1804 | 22140371 | 4408052 | 19.9032 | `dimension-a8667e1ffc3a799b` |
| 2024-02 | 2099 | 1737 | 21199664 | 4218973 | 19.8981 | `dimension-6c9c9c6abbdd2b00` |
| 2024-03 | 2210 | 1792 | 22322168 | 4442533 | 19.8918 | `dimension-53ae8781b77b96b4` |
| 2024-04 | 2121 | 1761 | 21425517 | 4261036 | 19.8774 | `dimension-d34a9a58d4b0ea3e` |
| 2024-05 | 2195 | 1820 | 22167277 | 4413864 | 19.9028 | `dimension-36c1aaa63a8f1c57` |
| 2024-06 | 2165 | 1786 | 21866512 | 4352679 | 19.906 | `dimension-627e5202c781b108` |
| 2024-07 | 2229 | 1820 | 22519508 | 4481034 | 19.8965 | `dimension-051a584fa069e8f2` |
| 2024-08 | 2347 | 1916 | 23702162 | 4719291 | 19.911 | `dimension-b2443632196bba82` |
| 2024-09 | 2139 | 1741 | 21607668 | 4299942 | 19.8955 | `dimension-d1cdc468cbaaa741` |
| 2024-10 | 2212 | 1833 | 22348182 | 4444786 | 19.8886 | `dimension-5ca86e442405ae3c` |
| 2024-11 | 2151 | 1790 | 21724203 | 4325675 | 19.8963 | `dimension-f8092a05fbeea5e5` |
| 2024-12 | 2228 | 1862 | 22500047 | 4480727 | 19.9155 | `dimension-a626a7ab63c6e15f` |
| 2025-01 | 2146 | 1773 | 21672074 | 4314145 | 19.8876 | `dimension-7b81a304687e174d` |
| 2025-02 | 1914 | 1601 | 19332056 | 3848371 | 19.8969 | `dimension-35ad770fe9a4f9e0` |
| 2025-03 | 2213 | 1813 | 22351748 | 4444840 | 19.8846 | `dimension-34c7569ed3340b29` |
| 2025-04 | 2173 | 1807 | 21954870 | 4369314 | 19.901 | `dimension-4ca38b330ee9cd1b` |
| 2025-05 | 1974 | 1626 | 19934917 | 3968802 | 19.9019 | `dimension-ede9a83387026cc2` |

## Audiência condicionada: elegibilidade, efeito e cobertura

Para cada rótulo de idade, gênero ou localização, comparamos pares dentro da mesma plataforma, formato, categoria, faixa de seguidores, mês-calendário e estado de patrocínio. Cada rótulo precisa de 30 taxas definidas e cinco creators. O efeito é mediana ERv do alvo menos mediana do comparador; taxa é acompanhada de volume e amostra. As demais dimensões de audiência não são controladas: associação descritiva, não efeito causal, persona ou vencedor geral. Sem dois rótulos elegíveis, a resposta é insuficiência quantificada, não uma preferência por público.

| Dimensão | Estratos elegíveis/total | Células elegíveis/total | Maior amostra de taxas por célula | Posts cobertos/total | Cobertura | Evidência |
|---|---:|---:|---:|---:|---:|---|
| audience_age_distribution | 0/8749 | 0/21644 | 19 | 0/52214 | 0% | `audience-overview-2fb31d1b58493c2b` |
| audience_gender_distribution | 0/8749 | 0/19024 | 23 | 0/52214 | 0% | `audience-overview-7c123b51f1ca929f` |
| audience_location | 0/8749 | 0/28638 | 12 | 0/52214 | 0% | `audience-overview-33460f68fd7f184b` |

## Patrocínio e o que não funciona

12 estratos elegíveis; 5216 sem amostra/contraparte suficiente; cobertura de 1.55897% dos posts. Evidência: `sponsorship-overview-e511c764e8b62394`.

Controle: mesma plataforma, formato, categoria, faixa de creator e mês-calendário. Cada mês exige contrapartes contemporâneas; orgânicos de um mês não são comparados a patrocinados de outro. Cada braço exige 30 taxas definidas e cinco creators; o efeito é a diferença entre medianas das medianas de ERv por creator. Cobertura baixa restringe as conclusões aos meses/contextos elegíveis; não sustenta uma política geral de patrocínio. Patrocínio é associação observacional, não causalidade. Custo implícito e retorno financeiro não podem ser calculados: faltam investimento, custo de produção, receita/conversão. Nenhum threshold de seguidores justifica desembolso sozinho.

Menor associação de ERv: Bilibili / video / lifestyle / 500,000+ / 2023-09; ΔERv -0.136225 p.p.; força 0.36; orgânicos/patrocinados: 37/38 posts, 372753/383650 views, 74407/76011 interações. Evidência: `sponsorship-13b0e47e53e74b9c`.

Maior associação de ERv: YouTube / video / lifestyle / 500,000+ / 2024-04; ΔERv +0.160707 p.p.; força 0.29; orgânicos/patrocinados: 34/30 posts, 343605/302197 views, 68090/60132 interações. Evidência: `sponsorship-aad291b3f1ea5f54`.

Esses extremos são achados descritivos, não prioridades adicionais nem ordens para suspender renovação. Sinal negativo isolado ou força insuficiente exige investigação; interromper investimento requer sinais concordantes, evidência forte e decisão humana. Ausência de zeros observados, quando indicada acima, limita a avaliação do fracasso: não prova inexistência de posts sem engajamento.

## Estratégia operacional e quick wins

Responsável sugerido: Gestor de Social Media. Executar nos próximos 7 dias; revisar 7 dias após cada teste. A estratégia abaixo aplica a fila inicial, sem reordená-la.

| Tema | Ação | Critério de revisão |
|---|---|---|
| Esforço e quick win | Preparar briefs dos contextos da fila na ordem exibida; anexar a evidência e registrar aceitar/rejeitar/editar. | Rever ERv, views e interações por post no mesmo contexto. |
| Público e creators | Preservar rótulos de audiência e faixa de creator do contexto; coletar se faltarem controles. Não inferir uma persona ou threshold de contratação. | Pelo menos 30 taxas e cinco creators por braço; declarar composição e concentração. |
| Frequência | Testar a mediana observada de posts/creator/semana completa indicada em cada prioridade; estado collect pede coleta antes de propor cadência. | Comparar janelas equivalentes; hipótese observacional, não frequência ótima ou efeito causal. Ausência de linha não equivale a zero. |
| Patrocínio | Obter custos reais antes de avaliar desembolso; força limitada pede coleta/teste. | ERv e volume concordantes, grupo comparável e dados financeiros. |
| Parar/revisar | Revisar repetição de padrões negativos; não parar por média global ou sinal isolado. | Interrupção exige a guarda do motor e decisão humana; sem base, coletar. |

## Auditabilidade e limites

Fonte SHA-256: `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `2.0.0`. Cada evidência está em [evidence.csv](./evidence.csv), com escopo, fórmula e referências.

Regeração conjunta: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html --report analysis.md`.

Linhas `recommendation` preservam `rank`, score, impacto, força, atualidade, valores originais V/I/F, denominadores P95, diferença, data representativa, ação, responsável e janelas. Impacto = média de min(V/P95_V,1), min(I/P95_I,1), min(F/P95_F,1); prioridade = 100 × impacto × força × atualidade. Scores são relativos à plataforma/tipo/unidade, não monetários. P95=0 usa máximo positivo ou zero se inexistente.

A coluna JSON `frequency_hypothesis` preserva status, valor/unidade, método, amostra de creator-semanas/creators, mês (`period_month`), regra (`coverage_rule`), semanas completas disponíveis/observadas, janela, ação, mínimo de semanas para coleta e limitação. No patrocínio mensal, entram apenas semanas ISO completas inteiramente dentro do mês e do escopo; semanas que atravessam a fronteira mensal ficam fora. Sem mês fixo, vale a cobertura completa do escopo. O valor é uma hipótese de teste no mesmo contexto da recomendação, não promessa de desempenho.

Em `source_ref`, agrupar por `evidence_id` e `reference_role` (target/comparator) e ordenar por `reference_chunk` (base 1). `source_row_id`, `source_line` e `reference_index` são arrays JSON paralelos, em blocos de até 500 entradas e 32.768 caracteres no campo de IDs, legíveis pelo limite padrão do csv.reader. O índice identifica o registro dentro da evidência (base 0); concatenar fragmentos de ID com o mesmo `reference_index`, conservando a linha física inicial (base 1). IDs acima de 4.096 caracteres são fragmentados sem perder conteúdo. Reconstituir a chave completa com `source_hash + ':' + ID`. Campos multilinha contam todas as linhas físicas; células de texto neutralizam fórmulas de planilha.

Linhas `evidence_detail` projetam estatísticas do alvo/comparador, incluindo quartis, amostra, fallback e controles removidos de benchmarks; no editorial, target=current e comparator=previous. `statistics` preserva os números completos. `quality`, `warning`, `benchmark_diagnostic` e `sponsorship_uncovered` conservam diagnósticos sem reunir milhares de contextos numa célula. Campos analíticos acima de 32.768 caracteres ficam vazios na linha-base e são reconstruídos por `analysis_field`: agrupar evidence_id/reference_role/field_name, ordenar field_chunk e concatenar json.loads(field_value); field_name tem formato record_type.campo para evitar colisões entre evidência e recomendação. O mesmo princípio vale para `history_field` no histórico, usando decision_id/outcome_id. A neutralização de fórmulas é preservada no texto recomposto.

A CLI publica todo o histórico, sem alertas post a post. Ausência de período anterior igualmente longo pode impedir comparações editoriais; não se inventa tendência. O monitoramento recente pode produzir outra fila porque tem outro escopo. Não há unidade confirmada de content_length, causalidade, ROI ou resultados futuros inferidos.
