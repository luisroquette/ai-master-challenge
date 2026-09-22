# Submissão — Luis Fernando Roquette — Challenge 003

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 003 — Lead Scorer

## Executive Summary

Construí uma aplicação Streamlit que transforma 8.800 oportunidades reais de CRM em filas comerciais explicáveis para vendedor e gestor. A ferramenta separa `Engaging` de `Prospecting`, bloqueia probabilidades que não passaram nos gates temporais e abre diretamente com **Minha fila agora**: até três leads por estágio, o motivo da prioridade, os sinais observados e a próxima ação. O resultado não é apenas um dashboard; é uma orientação operacional que responde “onde focar agora?” sem esconder incerteza estatística. Recomendo validar a fila em um piloto controlado antes de integrar escrita no CRM ou automatizar ações.

## Solução

### Abordagem

1. Congelei e validei os quatro CSVs reais, incluindo esquema, cardinalidade, joins e checksums.
2. Separei treino, calibração e teste no tempo e proibi `close_value`, `close_date` e derivados como features.
3. Modelei `Engaging` com candidatos comparáveis e gates de publicação; tratei `Prospecting` com heurística histórica suavizada.
4. Reconstruí as explicações a partir da lógica efetivamente usada e converti cada prioridade em uma ação determinística.
5. Transformei o ranking em uma fila operacional curta, com contextos de vendedor e gestor e auditoria local das prioridades temporárias.

### Resultados e evidências

- **Aplicação funcional:** [setup e execução local](solution/003-lead-scorer/README.md).
- **Evidência técnica:** [métricas, cobertura e limitações](solution/003-lead-scorer/docs/evaluation.md).
- **Dados reais:** 8.800 oportunidades, 85 contas, 7 produtos e 35 vendedores.
- **Decisão útil:** 2.089 oportunidades ativas priorizadas sem misturar escalas de `Engaging` e `Prospecting`.
- **Explicabilidade:** cada recomendação mostra “Foque neste lead”, “Por quê”, “Sinais” e “Ação”.

### Como experimentar

```bash
cd submissions/luis-roquette/solution/003-lead-scorer
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m streamlit run app.py --browser.gatherUsageStats=false
```

A URL local será exibida pelo Streamlit. Uma URL pública e o tour interativo só serão adicionados após validação final e autorização expressa de publicação.

### Recomendações

1. Rodar um piloto controlado com vendedores, registrando prioridade apresentada, ação executada e desfecho.
2. Medir ganho de ordenação e calibração por período, região e estágio antes de publicar probabilidades.
3. Integrar leitura e escrita no CRM somente com autenticação, autorização e trilha de auditoria por identidade verificada.
4. Recalibrar periodicamente e interromper a publicação quando qualidade, cobertura ou drift ultrapassarem os limites definidos.

### Limitações

Os dados são estáticos e observacionais. As quatro rotas probabilísticas avaliadas foram rejeitadas pelo gate de suporte; por isso, o produto publica prioridade relativa, não probabilidade de fechamento. O perfil vendedor/gestor é demonstrativo, sem autenticação. A aplicação não escreve no CRM, não mede efeito causal das ações e não possui monitoramento ou retreino agendado. As prioridades temporárias duram na sessão; seus eventos são persistidos localmente em uma trilha encadeada, mas o ator continua não verificado.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| OpenAI Codex | leitura em loop, perguntas socráticas, planejamento, implementação, testes e documentação |
| SDD Context Engineering Kit | especificação, decomposição e execução rastreável por critérios de aceite |
| Frontend Design | lapidação de UI e UX orientada à decisão comercial |
| Git e GitHub | histórico incremental, isolamento da branch e verificação das regras de entrega |

### Workflow

1. Reli o briefing até duas passadas consecutivas sem novos achados.
2. Conduzi seis ondas socráticas adaptativas antes da SPEC.
3. Transformei as decisões aprovadas em requisitos, arquitetura, critérios e contratos de teste.
4. Implementei em `Planejamento → Revisão → Execução → Teste`, repetindo quando o gate falhou.
5. Executei redundância, lapidação de produto, UI/UX e segurança antes de preparar a entrega.

### Onde a IA errou e como corrigi

A IA propôs inicialmente decisões que deixariam ambiguidade estatística, permitiriam leakage ou comunicariam prioridade relativa como probabilidade. As perguntas socráticas e os gates humanos corrigiram esses rumos. Durante a execução, testes revelaram problemas de `pd.NA`, seleção entre grades, serialização imutável, identidade da fonte e afirmações excessivas no verificador live. Cada falha foi corrigida na causa, recebeu regressão focal e voltou ao loop de validação.

### O que eu adicionei que a IA sozinha não faria

Defini a absorção por redundância antes de criar, o processo socrático em ondas dependentes, a documentação como parte central da engenharia e o critério de duas passadas limpas para fechar revisões. Também reposicionei o produto de “dashboard que explica” para “ferramenta que diz onde agir”, exigindo que cada recomendação respondesse: qual lead, por que ele, quais sinais e qual ação.

## Evidências

- [x] [Diário completo e contemporâneo](process-log/003-lead-scorer.md)
- [x] [Metodologia de construção](docs/metodologia-construcao-cognitiva-em-loops.md)
- [x] [Metodologia em DOCX](docs/metodologia-construcao-cognitiva-em-loops.docx)
- [x] [Mapa visual do prompt ao produto](docs/do-prompt-ao-produto.png)
- [x] [Prompts-chave e evolução](docs/prompts-chave.md)
- [x] [Roteiro do tour guiado](docs/roteiro-tour-guiado.md)
- [x] Histórico Git local com mais de 100 commits incrementais
- [ ] URL pública e gravação do tour — dependem de validação e autorização final

---

_Submissão preparada em: 22 de setembro de 2026_
