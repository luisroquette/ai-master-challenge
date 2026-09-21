---
title: Implementar diagnóstico acionável de churn da RavenStack
---

## Initial User Prompt

### Solicitações originais relevantes, preservadas

> Challege 1 por tanto. a) Você vai registrar,s eguindo nossa metodologia de diário, tudoq ue fizemos até aqui [claro,d e forma reusmida] e explicar nosso briefing pré-inicio

> https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/data-001-churn > > Leia o challenge, em todas as minucias, utilizando o modo /loop até que o /goal seja atingido: Goal é: pelo menos duas passdas consecutivas sem novos achados/descobertas ao reavaliar o briefing do desafio escolhido. Dessa forma, garantimos que o modelo abosrvue na totalidade tudo que foi trazido pelo texto/conteudo a ser avaliado. Registre no nosso diário tmabém essa decisao que é um diferencial criativo meu, gosto sempre de garantir com esse prompt a maior absorcaçao possível do conteúdo a ser analisado antes de criar qualquer coisa!

> agora, antes de seguirmos, registre tambem no nosso diário a decisao de seguir com a metodologia SDD {Spec-Driven} e, para isso, usaremos uma skillq ue gosto muito. Instale e use: https://claudecowork.im/resources/sdd npx skills add NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code

### Requirements

#### Objetivo e decisão

- Responder o que causa o churn, quais segmentos e contas estão em risco e quais ações priorizar.
- Ajudar o CEO a escolher qual problema sistêmico corrigir primeiro em até cinco minutos.
- Cruzar obrigatoriamente as cinco tabelas do Challenge 001.
- Priorizar contenção executável em uma semana e correção estrutural em 30–90 dias.

#### Método analítico

- Construir painel de conta por data de corte sem informação futura.
- Usar horizonte operacional de 30 dias e visão adicional da renovação anual.
- Calcular sinais de 7, 30 e 90 dias somente quando houver cobertura suficiente.
- Separar fato observado, associação controlada e hipótese causal.
- Usar `reason_code` e feedback somente no diagnóstico retrospectivo.
- Tratar evidência insuficiente como inconclusiva e suprimir rankings instáveis.
- Exibir MRR perdido como métrica principal e “MRR exposto — oportunidade máxima” como teto teórico.

#### Solução aprovada

- Implementar um pipeline Python único que valide dados e gere artefatos canônicos.
- Produzir relatório executivo em Markdown, dashboard Streamlit com três visões e fila operacional CSV.
- Disponibilizar `make reproduce` para validar e regenerar tudo e `make app` para abrir a interface.
- Manter execução local como requisito e demonstração pública somente leitura como diferencial não bloqueante.
- Excluir API, banco, autenticação, CRM, contato automático e chamadas pagas de IA.

#### Qualidade e aceite

- Rastrear cada finding até fontes, corte temporal, cálculo, evidência contrária, limitação e recomendação.
- Bloquear a entrega em falhas de schema, chaves, joins, receita, isolamento temporal, consistência de artefatos ou fumaça do dashboard.
- Incluir modelo preditivo apenas se superar baseline simples fora do tempo e agregar valor operacional por segmento.
- Manter relatório, dashboard e CSV consistentes e derivados da mesma execução.
- Documentar setup, limitações, decisões humanas e todo o uso de IA no process log.

#### Fontes de contexto

- Briefing oficial: `challenges/data-001-churn/README.md`.
- Regras de submissão: `submission-guide.md` e `CONTRIBUTING.md`.
- Descoberta aprovada: `submissions/luis-roquette/process-log/001-descoberta-socratica.md`.

## Description

// Will be filled in future stages by business analyst
