# Diário 004 — Planejamento dos entregáveis

## Fechamento da segurança

Luis confirmou o encerramento da auditoria proporcional ao beta. O parecer registrou os 19 controles solicitados e concluiu que não existe implementação indispensável pendente no dashboard local, estático e somente leitura. A segurança deve ser reaberta antes de internet pública, dados reais, autenticação, banco, escrita ou API paga.

## Nova decisão de entrega

Com o projeto funcional e auditado, Luis propôs uma entrega multimodal:

- wizard guiado do sistema no estilo Arcade;
- resumo escrito da construção em texto, DOCX e Markdown;
- peça visual ligando prompts decisivos à evolução do sistema;
- vídeo explicativo, mapa mental e infográfico gerados no NotebookLM.

O objetivo não é apenas exibir o produto. É demonstrar uma metodologia proprietária de criação com IA: SDD, método socrático em cinco ondas adaptativas, SPEC, lapidação, feedback looping, redundância necessária, medição e documentação contínua.

## Pesquisa e escolha de formato

Revalidamos o guia oficial do desafio. A submissão exige solução e Process Log e valoriza decomposição, erros da IA, correções humanas, iteração e comunicação clara. O pacote proposto atende diretamente esses critérios, desde que os formatos visuais permaneçam complementares ao PR.

O material oficial do NotebookLM confirma Video Overviews, Mind Maps, Infographics e Slide Decks fundamentados nas fontes, com risco explícito de imprecisão. Por isso, todo output visual terá revisão factual antes de ser aceito.

Os benchmarks publicados pelo Arcade recomendam 9–12 passos, texto curto, valor antecipado e vídeo somente onde movimento agrega. Definimos um tour de 10 passos centrado na pergunta do CEO, não numa lista de funcionalidades.

## Arquitetura aprovada para planejamento

O README, o relatório e o Process Log continuam sendo a entrega autoritativa. Uma narrativa canônica alimentará `.md`, `.txt` e `.docx`; o mesmo source pack alimentará NotebookLM; o Arcade demonstrará em 10 passos a resposta, a evidência e a decisão. Assim, cada formato reforça a mesma verdade e o avaliador não depende de ferramenta externa.

## Ordem planejada

1. congelar contrato editorial e source pack;
2. escrever narrativa canônica e converter formatos;
3. gerar e revisar mapa mental e infográfico;
4. gerar e revisar Video Overview;
5. capturar e revisar Arcade;
6. reconciliar manifesto, README, links e PR.

## Gate

Nenhum derivado pode inventar causa, número, impacto recuperável ou score externo. NotebookLM e Arcade só recebem dados públicos do desafio. Publicação externa e submissão ao upstream aguardam confirmação final de Luis.

## Artefatos de planejamento

- SPEC: `solution/001-churn/.specs/tasks/todo/package-challenge-001-deliverables.feature.md`
- Plano: `solution/001-churn/docs/superpowers/plans/2026-09-22-challenge-001-delivery-package.md`

**Estado:** planejamento concluído; implementação ainda não iniciada.
