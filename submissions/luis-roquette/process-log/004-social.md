# Diário de processo — Challenge 004: Estratégia Social Media

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:27 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir qualquer ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** seis passadas concluídas; as passadas 5 e 6 não produziram novas descobertas. O arquivo local e o `main` remoto eram idênticos no blob Git `52b10db595fb2a3f50c8a7cc73573fa53f5db087`.
- **Julgamento humano:** a técnica de leitura em loop e o critério de parada foram decisões criativas de Luis. A IA executou e documentou o protocolo.
- **Verificação:** checklist reverso localizou 18 de 18 requisitos críticos; duas releituras consecutivas encerraram sem novos achados.
- **Evidência:** este ledger e o histórico Git do arquivo.
- **Limitação:** os dados ainda não foram inspecionados; nenhuma hipótese de performance foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal | contexto, dados, quatro entregáveis, critérios de qualidade, dicas e público executivo |
| 2 | contradições e exigências implícitas | ausência de gasto impede ROI financeiro verdadeiro; Bilibili e RedNote aparecem nos dados, mas não no contexto inicial; frequência e thresholds exigem cautela causal |
| 3 | documentos obrigatórios vinculados | process log é eliminatório e deve mostrar decomposição, iterações, erros da IA, correções e contribuição humana |
| 4 | template e regras de submissão | resumo executivo curto, resultados com evidência, recomendações priorizadas, limitações, instruções de uso e alterações restritas à pasta da submissão |
| 5 | conferência integral por seção | nenhum |
| 6 | checklist reverso dos requisitos | nenhum |

**Gate atingido:** duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O desafio pede uma análise controlada, não médias gerais. A comparação entre conteúdo orgânico e patrocinado precisa considerar pelo menos plataforma, categoria e tamanho do creator, além de contextualizar engagement rate com alcance. Sem dados de gasto, não existe base para declarar ROI financeiro.

A estratégia deve dizer onde concentrar esforço, o que produzir, para quem, quando, com qual faixa de creator e qual evidência sustenta a decisão. Também precisa apontar o que parar, ordenar prioridades e propor quick wins executáveis na mesma semana.

O diferencial deve transformar os achados em decisão recorrente sem aumentar o escopo antes da evidência. A escolha entre dashboard, recomendador ou outra ferramenta será feita somente após pesquisa de soluções existentes e inspeção dos dados.

## I02 — SDD adotado antes da construção — 2026-09-21 14:31 BRT

- **Objetivo:** transformar o desafio em especificação verificável antes de implementar análise ou ferramenta.
- **IA/ferramenta:** skills `add-task`, `plan-task` e `implement-task` do Context Engineering Kit, instaladas para Claude Code via `npx skills`.
- **Ação ou prompt:** Luis decidiu usar Spec-Driven Development e indicou a skill SDD do repositório `NeoLabHQ/context-engineering-kit`.
- **Resultado:** a versão atual não expõe uma skill única chamada `sdd`; o fluxo foi instalado pelos três componentes publicados e iniciado com a spec local `.specs/tasks/draft/implement-challenge-004-social-media.feature.md`.
- **Julgamento humano:** adotar SDD foi decisão de Luis. O planejamento deve passar por revisão humana antes de qualquer implementação; a spec não substitui a Regra zero de pesquisa e evidência.
- **Verificação:** o instalador confirmou as três skills para Claude Code e classificou todas como seguras; a spec inicial preserva o prompt original e permanece em `draft`.
- **Evidência:** este registro, `skills-lock.json`, diretórios locais `.claude/skills/` e a spec em `.specs/tasks/draft/`.
- **Limitação:** `npx skills` instala skills, mas não os subagentes do plugin completo. Os artefatos de ferramenta ficam locais e não entrarão no Pull Request, que aceita apenas `submissions/luis-roquette/`.

**Fluxo adotado:** `add-task → plan-task → revisão humana da spec → implement-task`, sempre subordinado às regras de pesquisa, Ponytail, testes e integridade do desafio.
