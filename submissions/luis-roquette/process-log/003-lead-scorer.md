# Diário de processo — Challenge 003: Lead Scorer

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:28 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir a ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a fonte e a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** cinco passadas concluídas; as passadas 2 a 5 não produziram novas descobertas. O README local corresponde ao commit-fonte `d4c8fc7e20cc99370df5cc438aa553bb4a9789b2` e tem SHA-256 `0f88457c166c0b945ef645dfb25ae35021d38a6dab92e4af613ddcc8253dd466`.
- **Julgamento humano:** a leitura em loop e o critério de parada são um diferencial criativo de Luis. A IA executou e documentou o protocolo, sem apresentar a técnica como sugestão própria.
- **Verificação:** releitura integral normal e reversa, conferência estrutural das 100 linhas e teste de 11 invariantes textuais; a fonte local não apresentou diferença contra o commit do challenge.
- **Evidência:** este ledger, o hash do arquivo e o histórico Git do README avaliado.
- **Limitação:** os dados ainda não foram inspecionados e nenhuma hipótese de scoring foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal e documentos vinculados | problema comercial, quatro tabelas, solução funcional, documentação, process log, critérios, dicas, template e regras do PR |
| 2 | requisitos normativos | nenhum |
| 3 | conferência linha a linha | nenhum |
| 4 | conferência integral em ordem reversa | nenhum |
| 5 | identidade da fonte e matriz de invariantes | nenhum |

**Gate atingido:** pelo menos duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O problema não é prever fechamento em abstrato. É substituir a priorização “no feeling” por uma fila diária que ajude 35 vendedores a decidir onde agir dentro de aproximadamente 8.800 oportunidades. O software precisa funcionar com os dados reais, ir além de ordenar por valor e explicar por que cada deal recebeu prioridade alta ou baixa.

O `sales_pipeline.csv` é a tabela central e se conecta a contas, produtos e equipe comercial. Antes de definir qualquer score, as chaves, cardinalidades, ausências e distribuição temporal precisam ser medidas. O briefing comum adiciona um limite decisivo: deals ativos não podem usar `close_date`, `close_value` nem estágio final como features, pois isso vazaria o resultado futuro.

Complexidade de modelo não é o objetivo. Regras ou heurísticas bem validadas e explicáveis podem superar um modelo opaco se ajudarem o vendedor a tomar uma ação na segunda-feira de manhã. Filtros por vendedor, manager e região são um bônus de alto valor, não substitutos dos requisitos mínimos.

A entrega precisa incluir setup reproduzível, lógica e limitações, além de evidências do processo. A pesquisa externa e a inspeção dos dados decidirão a tecnologia, os critérios do score e se o diferencial proposto — fila por vendedor com motivos, risco de esfriar e próxima ação — é sustentado pelos dados.

### Erro registrado nesta etapa

No primeiro verificador local, a variável de shell `path` sobrescreveu o `PATH` especial do `zsh`, e o comando `git` deixou de ser localizado. A variável foi renomeada para `challenge_file`; o verificador passou sem alterar arquivos.
