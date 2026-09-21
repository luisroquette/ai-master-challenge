# Diário de implementação: SDD com feedback looping

- **Início:** 21 de setembro de 2026
- **Estado inicial:** implementação autorizada; código da solução ainda não criado
- **SPEC:** `solution/001-churn/.specs/tasks/in-progress/implement-churn-diagnostic.feature.md`
- **Plano canônico:** `solution/001-churn/docs/superpowers/plans/2026-09-21-ravenstack-churn-diagnostic.md`
- **Transcrição socrática canônica:** `process-log/001-descoberta-socratica.md`

## Fechamento da etapa anterior

O briefing oficial foi relido até duas passadas consecutivas sem novos achados. Em seguida, conduzimos cinco ondas socráticas adaptativas, criamos a SPEC, consolidamos o desenho em quatro seções, refinamos o plano em vinte passadas e encerramos com duas passadas estáveis. A auditoria final confirmou cobertura integral dos requisitos no plano, compatibilidade da stack e ausência de lacuna técnica conhecida.

O único gargalo externo era o teto global de cinco Codespaces. Após autorização explícita de Luis, excluímos somente `codex-preflight-vr7p79qv66whw4g9`, parado e limpo. O código desse ambiente permanece no commit `d73cbea`, integrado pela PR `luisroquette/swen.ia.br-claude#320`. A verificação final mostrou quatro Codespaces em `Shutdown` e uma vaga livre.

## Construção socrática preservada

Este mapa não substitui a transcrição integral. O diário `001-descoberta-socratica.md` preserva as alternativas, respostas literais, recomendações do agente, interpretações e consequências.

### Onda 1 — problema, decisão e usuário

1. Decisão principal do CEO: **C**, escolher qual problema de produto ou suporte corrigir primeiro.
2. Hipótese inicial: **A**, começar sem culpado e deixar os dados compararem as áreas.
3. Conflito entre contas e receita: **C**, usar matriz multicritério transparente.
4. Horizonte: **C**, contenção imediata seguida de correção estrutural.
5. Primeiro artefato: **D**, decisão executiva, dashboard de evidências e fila operacional.

### Onda 2 — sucesso, evidência e prioridade

1. Evidência mínima: **C**, associação controlada, coerência temporal e confirmação entre tabelas.
2. Métrica principal: **C**, MRR perdido com proteções de contas e segmentos.
3. Ordenação: **C**, portão de confiança e depois MRR recuperável, alcance e possibilidade de ação.
4. Estimativa sem histórico de intervenção: **A**, usar todo o MRR exposto como oportunidade bruta.
5. Nome do valor: **B**, “MRR exposto — oportunidade máxima”, com limitações explícitas.

### Onda 3 — dados, tempo e vazamento

1. Unidade analítica: **C**, conta por data de corte.
2. Horizonte de risco: **C**, 30 dias e visão adicional da renovação anual.
3. Janelas: **C**, 7, 30 e 90 dias quando houver cobertura.
4. Motivo e feedback de churn: **C**, somente diagnóstico retrospectivo.
5. Validação de modelo: **C**, fora do tempo, com contas agrupadas.

### Onda 4 — arquitetura, automação e experiência

1. Arquitetura: **B**, pipeline Python único para relatório, dashboard e fila CSV.
2. Reprodução: **B**, `make reproduce` e `make app`.
3. Dashboard: **B**, três visões com metodologia recolhível.
4. Automação de CS: **B**, CSV baixável; sem CRM ou contato automático.
5. Disponibilização: **B**, execução local obrigatória e Streamlit público não bloqueante. Luis delegou a decisão após nova verificação do repositório.

### Onda 5 — aceite, testes e definição de pronto

1. Finding final: **B, sem dúvidas**, com trilha reproduzível completa.
2. Testes bloqueantes: **B**, contratos, joins, receita, tempo, artefatos e dashboard.
3. Modelo preditivo: **B**, somente se superar baseline fora do tempo; Luis confirmou após comparar B e C.
4. Evidência insuficiente: **B**, marcar como inconclusiva e suprimir ranking instável.
5. Definição de pronto: **B**, requisitos, cinco tabelas, três respostas, consistência, gates, setup, limitações, diário e revisão executiva.

## Decisão metodológica de implementação

Luis definiu como obrigatória a **implementação em feedback looping**, combinada ao SDD. A execução seguirá uma etapa cronológica por vez e não avançará com gate vermelho.

Para cada etapa:

1. **Planejamento:** reler SPEC, plano, dependências e critério de aceite da etapa.
2. **Revisão:** confrontar o recorte com briefing, riscos, Ponytail e evidências existentes.
3. **Execução:** implementar somente o menor conjunto necessário para o critério atual.
4. **Teste:** executar o gate definido e registrar resultado, falha e correção.

Se o teste falhar, os insights alimentam imediatamente um novo ciclo da mesma etapa: `Planejamento → Revisão → Execução → Teste`. A passagem à etapa seguinte só ocorre após validação verde. Reports intermediários registrarão decisão, evidência, estado do gate e próximo movimento escolhido pela própria IA.

## Goal de implementação

Implementar integralmente o Challenge 001 pela SPEC e pelo plano canônico, mantendo fases SDD sequenciais, testes bloqueantes e diário contínuo. O goal só será concluído quando todos os critérios de aceite estiverem comprovados para o mesmo commit e conjunto de dados.

## Fase 1 — fundação reproduzível e dados verificados

### Planejamento — ciclo 1

**Estado:** iniciado.

O primeiro recorte corresponde à Task 1 do plano: projeto Python 3.12 instalável, constantes auditáveis, cinco CSVs imutáveis, checksums publicados e teste mínimo que prove a integridade das entradas. Nenhuma análise, modelo ou interface será antecipada nesta fase.

### Revisão — ciclo 1

**Resultado:** aprovado para execução.

A SPEC foi promovida de `draft` para `in-progress`, conforme o ciclo de vida SDD. O plano e os diários ativos agora apontam para o novo caminho. A transcrição histórica mantém as referências ao estado `draft` porque elas descrevem corretamente o estágio em que foram escritas.

A pesquisa externa anterior já havia identificado soluções de churn com pipeline local, scoring em lote e Streamlit, e rejeitado dependências de IA paga. A Task 1 reutiliza apenas o padrão validado de projeto instalável e arquivos imutáveis; não antecipa infraestrutura, modelo ou abstração.

### Incidente operacional

Uma busca `rg` usou backticks dentro de uma string com aspas duplas. O `zsh` tentou executar `draft` como comando e retornou `command not found`. Nenhum arquivo foi alterado. A correção é usar aspas simples para padrões que contenham backticks.
