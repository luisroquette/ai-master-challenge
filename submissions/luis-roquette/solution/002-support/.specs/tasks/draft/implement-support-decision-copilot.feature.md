---
title: Implement Support Decision Copilot
---

## Initial User Prompt

Antes de seguir, registre o fechamento de toda essa parte de exploração e criação da SPEC no nosso diário e, depois, aprove e crie a SPEC.

### Requirements

#### Outcome

Construir o Challenge 002 como um **Support Decision Copilot** local e autocontido que conecta diagnóstico operacional, triagem segura, resposta assistida, decisão humana e evidência gerencial em um fluxo demonstrável.

#### Primary experience

- Abrir na fila diária priorizada do agente de suporte.
- Ordenar tickets por prioridade composta e explicável, usando somente sinais validados.
- Exibir contexto sanitizado, categoria, prioridade, confiança calibrada, regras acionadas e decisão do gate.
- Permitir aprovar, editar e aprovar, rejeitar ou escalonar.
- Persistir localmente decisão, motivo e diferença entre sugestão e resposta final.

#### Automation boundary

- Automatizar roteamento apenas quando confiança calibrada e regras explícitas de risco permitirem.
- Fazer regras de risco prevalecerem sobre confiança alta.
- Encaminhar caso sensível, crítico, ambíguo, inválido ou incerto para revisão humana.
- Nunca enviar respostas externas no MVP.
- Nunca aprender online com uma decisão individual.

#### Response assistance

- Recuperar resoluções históricas sanitizadas e semelhantes do conjunto permitido.
- Mostrar fontes, identificadores e scores usados.
- Produzir rascunho editável somente quando a evidência superar o limite validado.
- Abster-se e escalonar quando não houver precedente seguro.
- Não usar geração livre como fallback.

#### Dataset boundaries

- Usar o Dataset 1 para diagnóstico operacional, workspace de Customer Support e recuperação de respostas.
- Usar o Dataset 2 no Laboratório IT, com sua taxonomia de oito categorias e modelo próprio.
- Reutilizar componentes de classificação, calibração, abstinência e auditoria sem unir linhas, rótulos ou taxonomias dos datasets.
- Remover PII antes de treino, persistência, interface, screenshot ou exportação.

#### Analytics and evidence

- Quantificar gargalos, fatores associados à satisfação e desperdício recuperável com denominadores rastreáveis.
- Separar histórico observado, desempenho medido do protótipo e cenários projetados.
- Fornecer calculadora de cenários conservador, base e otimista com premissas editáveis.
- Tratar associação como associação e custo como cenário, nunca como causalidade ou fato não observado.
- Exibir scorecard gerencial compacto e Laboratório IT separado.

#### Validation

- Comparar baselines simples antes de modelos mais complexos.
- Selecionar modelos por validação cruzada no conjunto de desenvolvimento.
- Manter teste estratificado congelado até modelo, calibração, regras e thresholds estarem definidos.
- Reportar macro-F1, métricas por classe, matriz de confusão, calibração e risco versus cobertura.
- Avaliar recuperação em tickets não vistos com rubrica humana de relevância, correção, segurança e esforço de edição.
- Testar o fluxo ponta a ponta, persistência, exportação, abstinência e precedência das regras de risco.

#### Delivery constraints

- Executar localmente com um comando e sem API paga, credenciais ou serviço externo.
- Escolher framework, dependências, modelos e persistência somente após a Regra Zero de pesquisa e reprodução.
- Manter toda entrega pública em `submissions/luis-roquette/`.
- Incluir README executivo, setup, pesquisa, testes, métricas, limitações, process log e screenshot real.
- Excluir helpdesk real, envio de mensagens, autenticação, multiempresa, deploy obrigatório, aprendizado online e infraestrutura especulativa.
- Reduzir ou remover qualquer função invalidada pelos dados; nunca simular evidência ausente.

#### Process gates

- Pesquisar GitHub, Reddit e documentação oficial antes de implementar.
- Inspecionar pelo menos três candidatos quando existirem e reproduzir a menor prova útil do escolhido.
- Aplicar Ponytail `full`: primeiro reutilizar, depois escrever o mínimo necessário.
- Executar `plan-task` e obter revisão humana da SPEC antes de iniciar `implement-task`.
- Registrar contemporaneamente decisões, perguntas, respostas, erros, correções e verificações no diário.

## Description

Entregar um protótipo local para agentes de suporte e gestores de Operações diagnosticarem gargalos, avaliarem automação segura e demonstrarem o fluxo completo sobre dados reais. A solução prioriza decisões explicáveis e reversíveis: modelos separados sugerem classificação, um gate determinístico limita a automação, precedentes históricos sustentam ou recusam rascunhos, e toda decisão humana fica auditável.

O MVP cobre diagnóstico do Dataset 1, classificação independente nos dois domínios, recuperação sanitizada, fila diária, scorecard, Laboratório IT, cenários editáveis e evidências reproduzíveis. Não cobre envio externo, helpdesk real, autenticação, multiempresa, deploy obrigatório, aprendizado online nem geração livre.

- **Pesquisa técnica:** `../../../../../research/002-support.md`
- **Plano de implementação:** `../../../docs/superpowers/plans/2026-09-21-support-decision-copilot.md`
