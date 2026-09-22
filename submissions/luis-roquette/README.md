# Submissão — Luis Fernando Roquette — Challenge 001

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 001 — Diagnóstico de Churn

## Executive Summary

Cruzei as cinco tabelas em um painel temporal reproduzível, com leituras `observed` e `strict`, para testar as alegações de uso, satisfação e seis possíveis causas de churn. O resultado principal é uma abstenção útil: nenhuma causa passou todos os gates de estabilidade, associação e confirmação entre fontes, enquanto as datas apresentam contradições materiais. O uso agregado cresce, mas satisfação não pode ser chamada de “ok”; o modelo opcional também foi recusado fora do tempo. Recomendo corrigir a medição e validar qualitativamente as hipóteses antes de direcionar uma intervenção — sem transformar correlação frágil em certeza executiva.

## Solução

### Abordagem

1. Imobilizei os cinco CSVs com SHA-256 e contratos explícitos.
2. Modelei conta por data de corte, com janelas de 7, 30 e 90 dias sem vazamento.
3. Comparei cronologias `observed` e `strict` e avaliei seis hipóteses pré-definidas.
4. Separei diagnóstico do modelo opcional e apliquei gates fora do tempo.
5. Gerei relatório, dashboard e fila a partir do mesmo objeto, protegidos por manifesto.

### Resultados / Findings

- [Relatório executivo](solution/001-churn/artifacts/report.md): decisão e evidências verificáveis.
- [Dashboard local e reprodução](solution/001-churn/README.md): três visões, filtros e exportação.
- [Findings canônicos](solution/001-churn/artifacts/findings.csv): seis hipóteses inconclusivas com motivo explícito.
- [Claims canônicos](solution/001-churn/artifacts/claim_checks.csv): uso sobe no agregado, cai na coorte de churn e satisfação permanece `concern`.
- [Contas para validação](solution/001-churn/artifacts/account_watchlist.csv): sinais descritivos nomeados, sem autorização de intervenção.
- [Qualidade dos dados](solution/001-churn/artifacts/quality_report.json): 19.142 usos pré-assinatura, 13.198 pré-cadastro e 1.077 tickets pré-cadastro.

### Recomendações

1. Em uma semana, auditar relógios, cadastro e vínculo assinatura–uso; suspender ranking causal automático até o gate ficar verde.
2. Revisar manualmente uma amostra estratificada das 97 contas com renovação automática desligada, sem tratá-la como causa provada.
3. Em 30–90 dias, corrigir instrumentação e medir uma coorte prospectiva com owner e critério de sucesso pré-definidos.
4. Só publicar scores quando o modelo superar baseline fora do tempo; nesta execução, ele foi corretamente bloqueado.

### Limitações

Os dados são observacionais, contraditórios e aparentemente sintéticos. Não há histórico de intervenção para estimar receita recuperável ou efeito causal. Feedback de churn não entra em score prospectivo. As métricas de segmento usam o último snapshot diagnóstico elegível por conta e não representam uma taxa histórica populacional.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| OpenAI Codex | pesquisa, leitura do desafio, perguntas socráticas, SPEC, implementação, testes e documentação |
| SDD — Context Engineering Kit | sequência SPEC → plano → execução → validação |
| Ponytail | controle de escopo, reuso e menor implementação suficiente |
| Pesquisa web/GitHub | busca prévia de padrões e soluções existentes antes da criação |

### Workflow

1. Li o briefing em loop até duas passadas consecutivas sem novos achados.
2. Conduzi cinco ondas socráticas adaptativas antes de escrever a SPEC.
3. Refinei o plano até duas rodadas consecutivas sem melhoria substancial.
4. Implementei cada fase em `Planejamento → Revisão → Execução → Teste`, repetindo quando um gate falhou.
5. Mantive decisões, erros, correções e provas em diários contemporâneos.

### Onde a IA errou e como corrigi

A IA inicialmente herdou um teste de caminho incompatível com a resolução real do `AppTest`; corrigi para caminho absoluto e preservei a prova pela raiz. Também tentou capturar exceções amplas no modelo estatístico e recebeu bloqueio do Ruff; restringi às falhas numéricas conhecidas. No painel, rejeitei um teste conceitualmente impossível que exigia cobertura histórica antes do cadastro. Finalmente, um smoke revelou `pd.NA` incompatível com sklearn, levando à normalização explícita das features aprovadas.

### O que eu adicionei que a IA sozinha não faria

Defini documentação como parte principal da entrega — “ganha quem documenta” — e exigi absorção por loop, cinco ondas socráticas e SDD antes de qualquer implementação. Também determinei que abstenção é melhor que uma narrativa causal instável, que toda recomendação precisa de um portão de confiança e que relatório, dashboard e CSV devem compartilhar a mesma verdade canônica.

## Evidências

- [ ] Screenshots das conversas com IA — não necessários para reproduzir o trabalho
- [ ] Screen recording do workflow — não produzido
- [x] [Diário pré-início](process-log/000-pre-inicio.md)
- [x] [Descoberta socrática](process-log/001-descoberta-socratica.md)
- [x] [Otimização do plano](process-log/002-otimizacao-plano-loop.md)
- [x] [Implementação em feedback looping](process-log/003-implementacao-feedback-looping.md)
- [x] [Histórico Git da branch](https://github.com/luisroquette/ai-master-challenge/commits/submission/luis-roquette/)

---

_Submissão preparada em: 21 de setembro de 2026_
