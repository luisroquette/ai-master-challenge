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

## Enxugamento para o avaliador com pouco tempo

Luis introduziu duas restrições decisivas: o avaliador provavelmente terá pouco tempo e baixa disposição para navegar muitos materiais; além disso, já existe um vídeo obrigatório em que Luis explica a arquitetura.

**Evidência do vídeo:** arquivo MP4 de 232.879.349 bytes, duração de 365,533 segundos (6min05s), 1920×1080, 60 fps, H.264 com áudio AAC estéreo e SHA-256 `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`. A inspeção visual confirmou captura de tela, facecam e legendas queimadas. Não há stream separado de legenda.

**Corte Ponytail:** removemos o Video Overview do NotebookLM, o mapa mental e o TXT. O vídeo existente substitui qualquer segundo vídeo; Markdown já atende leitura por IA; DOCX atende leitura humana; um único infográfico comunica a evolução visual. O MP4 não será commitado, evitando 222 MiB no histórico; o Git guardará link, poster, capítulos, metadados e checksum.

**Nova hierarquia:** quatro entradas visíveis: `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Audite o processo`. Arcade foi reduzido a oito passos e demonstrará apenas o sistema. Relatório, código, segurança e Process Log permanecem disponíveis dentro da camada de auditoria.

**Plano canônico revisado:** `solution/001-churn/docs/superpowers/plans/2026-09-22-lean-delivery-package.md`. O plano multimodal anterior permanece no histórico e está marcado como substituído.

**Estado:** plano enxuto aguardando validação de Luis; nenhuma mídia foi publicada.

## Ajuste final de escopo por decisão de Luis

Luis decidiu manter quatro peças complementares: Video Overview do NotebookLM, infográfico do NotebookLM, Arcade no formato atual de oito passos e o vídeo obrigatório de arquitetura já gravado. A decisão substitui apenas o corte anterior do Video Overview; o mapa mental e o TXT continuam removidos.

**Separação de funções:** o vídeo obrigatório apresenta Luis explicando a arquitetura em primeira pessoa; o Video Overview sintetiza a construção, as decisões humanas e a evolução do método; o Arcade demonstra o sistema; o infográfico oferece leitura visual instantânea. Essa separação evita que dois vídeos contem a mesma história.

**Nova hierarquia:** `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Veja a síntese do NotebookLM`; `Audite o processo`. O infográfico acompanha a síntese do NotebookLM.

**Estado:** SPEC e plano atualizados; implementação continua não iniciada.

## Auditoria final das regras oficiais de entrega

Antes da implementação dos entregáveis, Luis exigiu uma nova conferência do README raiz, do Challenge 001, do Guia de Submissão, do `CONTRIBUTING.md` e do template oficial. A regra de parada foi endurecida: nenhum push final ou PR poderá ocorrer enquanto a aderência não estiver em 100%.

A auditoria encontrou quatro lacunas. O relatório não explicitava impacto estimado por ação; a entrada não resumiria a quantidade de iterações; o plano ainda não transformava branch, PR único e título em gates; data, histórico Git e links externos precisavam de validação final. Todas foram incorporadas à SPEC e ao plano.

**Decisão metodológica:** quando o impacto financeiro não puder ser estimado causalmente, a entrega dirá “não estimável” e mostrará somente o MRR perdido observado como teto histórico. Inventar receita recuperável para preencher o requisito seria menos aderente que explicitar a limitação.

**Gate de submissão:** os quatro desafios serão consolidados na branch única `submission/luis-roquette` e no PR único `[Submission] Luis Fernando Roquette — Challenges 001–004`; diff limitado a `submissions/luis-roquette/`; README baseado no template; setup reproduzível; links anônimos; data e histórico finais; confirmação explícita de Luis antes do envio.

**Estado:** correções locais em execução; nenhum push ou PR autorizado até a validação integral.

## Execução dos entregáveis — Task 1

A primeira etapa produziu a porta de entrada em Markdown e DOCX a partir da resposta canônica. O brief tem 777 palavras e duas páginas A4. Ele começa pelo diagnóstico do CEO, explicita o conflito entre agregado e coorte, recusa causalidade não demonstrada e apresenta três ações com responsável, prazo, impacto estimado e confiança.

O DOCX passou por duas renderizações. A primeira revelou uma borda indevida sob o título e excesso de espaço na página inicial. A quebra de página foi deslocada para a evolução da resposta e a borda do estilo foi removida. A segunda inspeção confirmou duas páginas legíveis, tabelas sem clipping, hierarquia clara e links visíveis.

**Validação:** 777 palavras; cinco números e quatro notas internas reconciliados; zero links locais quebrados; metadados pessoais removidos; nenhuma publicação externa realizada.

**Estado:** Task 1 concluída localmente. Push permanece bloqueado.

## Execução dos entregáveis — Task 2

O vídeo obrigatório foi inspecionado sem colocá-lo no Git. Confirmamos 6min05s, H.264 em 1920×1080 a 60 fps, áudio AAC estéreo, legendas queimadas, 232.879.349 bytes e SHA-256 `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`.

A revisão visual usou 366 amostras, uma por segundo, e OCR local das legendas. Isso revelou uma correção de enquadramento: o vídeo explica a arquitetura do trabalho nos quatro desafios — SDD, Ponytail, método socrático, otimização de planos, feedback looping, segurança, UI/UX e revisão do output — e não apenas a arquitetura técnica do dashboard de churn.

Foram registrados onze capítulos e criado um poster sem tela privada. O vídeo cita notas e 99% de confiança como parte do prompt de autoavaliação; o README deixa explícito que não se trata de nota do G4 nem confiança estatística do diagnóstico.

**Estado:** pacote local do vídeo pronto. Hospedagem e validação anônima permanecem bloqueadas até confirmação explícita de Luis e reprodução integral em tempo real.
