# Rubrica da resposta executiva

## Regra de avaliação

A nota mede a capacidade da entrega de responder à pergunta do CEO com precisão, cobertura e utilidade. Ela não mede certeza causal. Cada rodada é pontuada sem arredondamento; a meta é `>= 9,5/10` e nenhum hard cap acionado.

| Dimensão | Peso | Nota máxima exige |
|---|---:|---|
| Resposta direta | 2,0 | Diagnóstico, limite causal e decisão no primeiro bloco. |
| Precisão quantitativa | 2,0 | Churn, denominadores, períodos, MRR, cobertura e incerteza corretos. |
| Reconciliação CS × Produto | 2,0 | Agregado e coorte comparados; respondentes não generalizados para a base. |
| Calibração causal | 1,5 | Hipótese inconclusiva nunca chamada de causa, driver ou mecanismo mais forte. |
| Utilidade decisória | 1,5 | Ações com responsável, prazo, população, métrica e regras de avançar/parar. |
| Consistência e auditoria | 1,0 | JSON, relatório e dashboard usam os mesmos claims, valores e `analysis_id`. |

## Hard caps

- Causalidade indevida: nota máxima `8,0`.
- População, período ou denominador incorreto: nota máxima `8,0`.
- Números divergentes entre superfícies: nota máxima `8,0`.

## Âncoras

### 7,0 — linha de base

Confirma a alta do churn e explica a contradição por coortes, mas chama uma hipótese inconclusiva de “mecanismo mais forte”, destaca um segmento com RR 1,08× como se fosse concentração, não leva o impacto econômico ao resumo e oferece uma única ação genérica.

### 9,5 — mínimo de aprovação

Responde em até 45 segundos: quantifica mudança e impacto; explica Produto × CS por população; declara que a causa ainda não foi demonstrada; evita falsa concentração; apresenta três validações executáveis; e mantém rastreabilidade idêntica nas três superfícies.

## Medições por incremento

| Rodada | Direta /2 | Precisão /2 | CS×Produto /2 | Causal /1,5 | Decisão /1,5 | Auditoria /1 | Total | Hard cap | Evidência |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| Linha de base | 1,4 | 1,2 | 1,8 | 1,0 | 0,8 | 0,8 | **7,0** | Não | Avaliação anterior ao novo plano. |
| Task 1 — contrato | 1,4 | 1,2 | 1,8 | 1,0 | 0,8 | 0,8 | **7,0** | Não | Rubrica e regressão fixam o critério; output ainda não mudou. |

As próximas linhas só podem ser preenchidas depois do teste da respectiva implementação.
