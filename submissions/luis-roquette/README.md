# Submissão — Luis Fernando Roquette — Challenge 003

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge escolhido:** 003 — Lead Scorer

## Executive Summary

Construí uma aplicação Streamlit que transforma 8.800 oportunidades reais em filas de trabalho explicáveis para vendedor e gestor. As 2.089 oportunidades ativas são separadas entre `Engaging` e `Prospecting`, sem comparar escalas incompatíveis. Como as quatro rotas probabilísticas falharam nos gates de suporte, o produto não publica falsa precisão: ele entrega prioridade relativa, sinais observados e próxima ação. O resultado responde diretamente: **qual lead priorizar, por quê e o que fazer agora**.

## Comece aqui

1. **Experiência guiada:** após clonar o repositório, rode `python3 -m http.server 50400 --directory submissions/luis-roquette` e abra `http://127.0.0.1:50400/delivery/`.
2. **Produto funcional:** siga o [setup e o preflight do Lead Scorer](solution/003-lead-scorer/README.md).
3. **Construção visual:** veja o [vídeo de 5:48](delivery/assets/video-notebooklm.mp4), o [infográfico](delivery/assets/infografico-notebooklm.png) e o [mapa mental](delivery/assets/mapa-mental-notebooklm.png).

## Solução

### Abordagem

- Carregamento reproduzível dos quatro CSVs reais, com manifesto e checksums.
- Priorização independente por estágio, evitando leakage e comparações inválidas.
- Avaliação temporal de regressão logística e gradient boosting nas rotas completa e fallback.
- Explicações derivadas da saída real do modelo e ações de um playbook determinístico.

### Resultados / Findings

- 8.800 oportunidades analisadas; 2.089 ativas priorizadas.
- Quatro rotas probabilísticas avaliadas e rejeitadas; zero probabilidades indevidas publicadas.
- Filas acionáveis para vendedor e gestor, com “focar”, “atenção”, sinais e próxima ação.
- Nenhuma escrita no CRM e nenhuma API de IA no runtime.

### Recomendações

1. Usar a fila relativa em um piloto controlado com vendedores.
2. Registrar intervenção e desfecho antes de recalibrar o modelo.
3. Publicar probabilidades somente após superar novamente os gates temporais.

### Limitações

Dados estáticos, perfis demonstrativos sem autenticação, nenhuma escrita no CRM, pins sem persistência de produto e nenhuma inferência causal. Integração, controle de acesso, monitoramento de drift e retreino pertencem a uma fase posterior ao piloto.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Uso |
|---|---|
| OpenAI Codex | Descoberta, implementação, testes, auditorias e documentação |
| SDD Context Engineering Kit | SPEC, plano executável e critérios de aceite |
| Frontend Design | Lapidação da interface e do tour guiado |
| NotebookLM | Vídeo, infográfico e mapa mental a partir de fonte curada |

### Workflow

1. Leitura redundante do briefing até duas passadas sem novos achados.
2. Seis ondas socráticas adaptativas antes da SPEC.
3. SDD: especificação, revisão, execução e teste em feedback loops.
4. Redundância, lapidação de produto/UI e auditoria de segurança.
5. Embalagem visual e auditoria final contra as regras oficiais.

### Onde a IA errou e como corrigi

A primeira direção reduzia o problema a um dashboard com score. A revisão humana redefiniu o produto como uma fila de ação, bloqueou leakage, separou estágios incompatíveis e impediu a publicação de probabilidades não sustentadas. O primeiro mapa mental veio recolhido; o primeiro infográfico trouxe uma métrica ambígua; ambos foram refeitos e verificados.

### O que eu adicionei que a IA sozinha não faria

O Método de Construção Cognitiva em Loops (MCCL): documentação contemporânea, descoberta socrática antes da SPEC, critérios explícitos de saída, loops de correção e uma exigência central de utilidade — o vendedor deve saber **onde focar e por quê**, não apenas receber um número.

## Evidências

- [Diário contemporâneo completo](process-log/003-lead-scorer.md)
- [Método MCCL](docs/metodologia-construcao-cognitiva-em-loops.md) e [prompts-chave](docs/prompts-chave.md)
- [Métricas e avaliação](solution/003-lead-scorer/docs/evaluation.md)
- [Checklist de segurança](solution/003-lead-scorer/docs/security-checklist.md)
- Histórico Git com a evolução incremental da solução

---

_Submissão preparada em 22 de setembro de 2026._
