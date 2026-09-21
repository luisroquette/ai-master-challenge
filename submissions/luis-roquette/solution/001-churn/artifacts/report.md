# Diagnóstico executivo de churn

## Decisão executiva

Evidência insuficiente para priorizar uma causa

## O que não bate

| claim id | cohort | start value | end value | status | coverage |
| --- | --- | --- | --- | --- | --- |
| C-usage-growth | overall | 0.356 | 0.520 | up | 0.845 |
| C-satisfaction-ok | overall | 3.940 | 4.021 | concern | 0.640 |
| C-usage-growth | churn_next_30d | 0.374 | 0.319 | up | 0.634 |
| C-satisfaction-ok | churn_next_30d | 4.500 | 3.667 | concern | 0.659 |

## Evidências causais candidatas

| finding id | failure reason |
| --- | --- |
| F-commercial-renewal | cross_table_gate |
| F-product-usage-drop | model_failure:ValueError |
| F-product-errors | model_failure:ValueError |
| F-commercial-downgrade | cross_table_gate |
| F-support-satisfaction | model_failure:ValueError |
| F-support-escalation | model_failure:ValueError |

## Segmentos

| dimension | segment | sample size | churn rate | mrr lost | confidence |
| --- | --- | --- | --- | --- | --- |
| industry | Cybersecurity | 89 | 0.663 | 362645.000 | eligible |
| industry | DevTools | 100 | 0.700 | 558429.000 | eligible |
| industry | EdTech | 71 | 0.676 | 313110.000 | eligible |
| industry | FinTech | 98 | 0.582 | 503672.000 | eligible |
| industry | HealthTech | 84 | 0.631 | 435392.000 | eligible |
| country | AU | 29 | 0.621 | 156205.000 | inconclusive |
| country | CA | 21 | 0.714 | 56012.000 | inconclusive |
| country | DE | 25 | 0.560 | 77630.000 | inconclusive |
| country | FR | 18 | 0.722 | 70523.000 | inconclusive |
| country | IN | 42 | 0.595 | 317109.000 | eligible |
| country | UK | 55 | 0.727 | 229150.000 | eligible |
| country | US | 252 | 0.643 | 1266619.000 | eligible |
| referral_source | ads | 90 | 0.556 | 425283.000 | eligible |
| referral_source | event | 85 | 0.647 | 365083.000 | eligible |
| referral_source | organic | 102 | 0.696 | 676986.000 | eligible |

## Contas prioritárias

Nenhuma conta nomeada: não há finding aceito.

## Plano de ação

Revisar qualidade, cobertura e estabilidade antes de direcionar uma intervenção.

## Metodologia e limitações

Painel conta-data de corte, leitura strict para decisão e observed apenas para sensibilidade. As associações não demonstram causalidade; MRR exposto é oportunidade máxima, não receita recuperável.

O modelo preditivo só é publicado quando supera todos os gates fora do tempo. Nesta execução: publish_model=False.
